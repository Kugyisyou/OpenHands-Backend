#!/usr/bin/env python3
"""
Enhanced Monitoring and Logging System for OpenHands Backend
Provides comprehensive monitoring, metrics, and logging capabilities
"""

import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Metrics for individual requests"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: datetime

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_requests: int = 1000):
        self.max_requests = max_requests
        self.requests: deque = deque(maxlen=max_requests)
        self.system_metrics: deque = deque(maxlen=100)  # Last 100 system snapshots
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'errors': 0,
            'last_called': None
        })
        self.start_time = datetime.now()
        
    def add_request(self, metrics: RequestMetrics):
        """Add request metrics"""
        self.requests.append(metrics)
        
        # Update endpoint statistics
        endpoint_key = f"{metrics.method} {metrics.endpoint}"
        stats = self.endpoint_stats[endpoint_key]
        stats['count'] += 1
        stats['total_time'] += metrics.response_time
        stats['last_called'] = metrics.timestamp
        
        if metrics.status_code >= 400:
            stats['errors'] += 1
            
        logger.info(f"📊 Request: {metrics.method} {metrics.endpoint} - "
                   f"{metrics.status_code} - {metrics.response_time:.3f}s")
    
    def add_system_metrics(self, metrics: SystemMetrics):
        """Add system metrics"""
        self.system_metrics.append(metrics)
        
        # Log high resource usage
        if metrics.cpu_percent > 80:
            logger.warning(f"⚠️ High CPU usage: {metrics.cpu_percent:.1f}%")
        if metrics.memory_percent > 80:
            logger.warning(f"⚠️ High memory usage: {metrics.memory_percent:.1f}%")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Request statistics
        total_requests = len(self.requests)
        recent_requests = [r for r in self.requests if now - r.timestamp < timedelta(minutes=5)]
        
        # Error statistics
        error_requests = [r for r in self.requests if r.status_code >= 400]
        error_rate = len(error_requests) / total_requests if total_requests > 0 else 0
        
        # Response time statistics
        response_times = [r.response_time for r in self.requests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # System statistics
        current_system = self.system_metrics[-1] if self.system_metrics else None
        
        # Endpoint statistics
        endpoint_summary = {}
        for endpoint, stats in self.endpoint_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            error_rate_endpoint = stats['errors'] / stats['count'] if stats['count'] > 0 else 0
            
            endpoint_summary[endpoint] = {
                'calls': stats['count'],
                'avg_response_time': round(avg_time, 3),
                'error_rate': round(error_rate_endpoint * 100, 2),
                'last_called': stats['last_called'].isoformat() if stats['last_called'] else None
            }
        
        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime).split('.')[0],
            'total_requests': total_requests,
            'recent_requests_5min': len(recent_requests),
            'error_rate_percent': round(error_rate * 100, 2),
            'avg_response_time_ms': round(avg_response_time * 1000, 2),
            'current_system': asdict(current_system) if current_system else None,
            'endpoints': endpoint_summary,
            'timestamp': now.isoformat()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health check status"""
        stats = self.get_stats()
        
        # Determine health status
        health_issues = []
        
        if stats['error_rate_percent'] > 10:
            health_issues.append(f"High error rate: {stats['error_rate_percent']}%")
        
        if stats['avg_response_time_ms'] > 5000:
            health_issues.append(f"Slow response time: {stats['avg_response_time_ms']}ms")
        
        if stats['current_system']:
            if stats['current_system']['cpu_percent'] > 90:
                health_issues.append(f"High CPU: {stats['current_system']['cpu_percent']}%")
            if stats['current_system']['memory_percent'] > 90:
                health_issues.append(f"High memory: {stats['current_system']['memory_percent']}%")
        
        status = "healthy" if not health_issues else "degraded" if len(health_issues) < 3 else "unhealthy"
        
        return {
            'status': status,
            'issues': health_issues,
            'uptime': stats['uptime_human'],
            'total_requests': stats['total_requests'],
            'timestamp': datetime.now().isoformat()
        }

class SystemMonitor:
    """Monitors system resources"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring = False
        
    async def start_monitoring(self, interval: int = 30):
        """Start system monitoring"""
        self.monitoring = True
        logger.info(f"🔍 Starting system monitoring (interval: {interval}s)")
        
        while self.monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / 1024 / 1024,
                    memory_available_mb=memory.available / 1024 / 1024,
                    disk_usage_percent=disk.percent,
                    timestamp=datetime.now()
                )
                
                self.metrics_collector.add_system_metrics(metrics)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ System monitoring error: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        logger.info("🛑 System monitoring stopped")

class RequestLogger:
    """Enhanced request logging"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        
    def log_request(self, 
                   endpoint: str,
                   method: str,
                   status_code: int,
                   response_time: float,
                   user_agent: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   error_message: Optional[str] = None):
        """Log request with metrics"""
        
        metrics = RequestMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            timestamp=datetime.now(),
            user_agent=user_agent,
            ip_address=ip_address,
            error_message=error_message
        )
        
        self.metrics_collector.add_request(metrics)
        
        # Log special cases
        if status_code >= 500:
            logger.error(f"🚨 Server error: {method} {endpoint} - {status_code} - {error_message}")
        elif status_code >= 400:
            logger.warning(f"⚠️ Client error: {method} {endpoint} - {status_code}")
        elif response_time > 10:
            logger.warning(f"🐌 Slow request: {method} {endpoint} - {response_time:.3f}s")

# Global instances
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
request_logger = RequestLogger(metrics_collector)

def get_monitoring_stats() -> Dict[str, Any]:
    """Get current monitoring statistics"""
    return metrics_collector.get_stats()

def get_health_check() -> Dict[str, Any]:
    """Get health check status"""
    return metrics_collector.get_health_status()

async def start_system_monitoring(interval: int = 30):
    """Start system monitoring task"""
    await system_monitor.start_monitoring(interval)

def stop_system_monitoring():
    """Stop system monitoring"""
    system_monitor.stop_monitoring()

def log_request_metrics(endpoint: str, method: str, status_code: int, 
                       response_time: float, **kwargs):
    """Log request metrics"""
    request_logger.log_request(endpoint, method, status_code, response_time, **kwargs)

# Middleware function for FastAPI
def create_monitoring_middleware():
    """Create FastAPI middleware for request monitoring"""
    
    async def monitoring_middleware(request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            response_time = time.time() - start_time
            
            # Log request
            log_request_metrics(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                user_agent=request.headers.get('user-agent'),
                ip_address=request.client.host if request.client else None
            )
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Log error
            log_request_metrics(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500,
                response_time=response_time,
                user_agent=request.headers.get('user-agent'),
                ip_address=request.client.host if request.client else None,
                error_message=str(e)
            )
            
            raise e
    
    return monitoring_middleware

if __name__ == "__main__":
    # Test the monitoring system
    print("🧪 Testing monitoring system...")
    
    # Simulate some requests
    for i in range(10):
        log_request_metrics(
            endpoint="/api/test",
            method="GET",
            status_code=200 if i < 8 else 500,
            response_time=0.1 + (i * 0.05)
        )
    
    # Get stats
    stats = get_monitoring_stats()
    health = get_health_check()
    
    print("\n📊 Stats:")
    print(json.dumps(stats, indent=2, default=str))
    
    print("\n🏥 Health:")
    print(json.dumps(health, indent=2, default=str))