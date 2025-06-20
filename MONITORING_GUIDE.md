# 📊 Enhanced Monitoring & Logging Guide

Comprehensive monitoring and logging system untuk OpenHands Backend yang memberikan insight mendalam tentang performance, health, dan usage patterns.

## ✨ **Features**

### 🎯 **Core Monitoring**
- **Request Tracking**: Monitor semua API requests dengan response time
- **System Metrics**: CPU, memory, disk usage monitoring
- **Error Tracking**: Comprehensive error logging dan analysis
- **Health Checks**: Multi-level health status monitoring
- **Performance Analytics**: Response time analysis dan bottleneck detection

### 📊 **Metrics Collection**
- **Real-time Metrics**: Live system dan application metrics
- **Historical Data**: Trend analysis dengan data retention
- **Endpoint Statistics**: Per-endpoint performance tracking
- **Error Rate Monitoring**: Error rate tracking per endpoint
- **Resource Usage**: System resource utilization tracking

## 🚀 **API Endpoints**

### **GET** `/health`
Simple health check untuk load balancers dan uptime monitoring.

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1703123456.789
}
```

### **GET** `/api/monitoring/health`
Detailed health check dengan comprehensive status information.

**Response:**
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "issues": [],
    "uptime": "2:30:45",
    "total_requests": 1250,
    "timestamp": "2025-06-20T16:30:00"
  },
  "timestamp": 1703123456.789
}
```

**Health Status Values:**
- `healthy`: Semua systems normal
- `degraded`: Ada issues minor tapi masih functional
- `unhealthy`: Critical issues yang memerlukan attention

### **GET** `/api/monitoring/stats`
Comprehensive monitoring statistics dan performance metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "uptime_seconds": 9045,
    "uptime_human": "2:30:45",
    "total_requests": 1250,
    "recent_requests_5min": 45,
    "error_rate_percent": 2.4,
    "avg_response_time_ms": 156.7,
    "current_system": {
      "cpu_percent": 15.2,
      "memory_percent": 45.8,
      "memory_used_mb": 512.3,
      "memory_available_mb": 1024.7,
      "disk_usage_percent": 67.2,
      "timestamp": "2025-06-20T16:30:00"
    },
    "endpoints": {
      "GET /api/chat": {
        "calls": 450,
        "avg_response_time": 0.234,
        "error_rate": 1.2,
        "last_called": "2025-06-20T16:29:45"
      },
      "POST /api/fizzo-auto-update": {
        "calls": 25,
        "avg_response_time": 15.678,
        "error_rate": 4.0,
        "last_called": "2025-06-20T16:25:30"
      }
    },
    "timestamp": "2025-06-20T16:30:00"
  },
  "timestamp": 1703123456.789
}
```

## 🔧 **System Monitoring**

### **Automatic Monitoring**
System monitoring berjalan otomatis di background dengan interval 30 detik:

- **CPU Usage**: Monitoring CPU utilization
- **Memory Usage**: RAM usage dan availability
- **Disk Usage**: Storage utilization
- **Process Monitoring**: Application process health

### **Alert Thresholds**
- **High CPU**: Warning jika CPU > 80%, Critical jika > 90%
- **High Memory**: Warning jika Memory > 80%, Critical jika > 90%
- **High Error Rate**: Warning jika error rate > 10%
- **Slow Response**: Warning jika avg response time > 5 seconds

## 📈 **Request Monitoring**

### **Automatic Request Tracking**
Semua HTTP requests otomatis di-track dengan informasi:

- **Endpoint**: URL path yang diakses
- **Method**: HTTP method (GET, POST, etc.)
- **Status Code**: Response status code
- **Response Time**: Request processing time
- **User Agent**: Client user agent
- **IP Address**: Client IP address
- **Error Messages**: Error details jika ada

### **Performance Metrics**
- **Average Response Time**: Per endpoint dan overall
- **Request Volume**: Total requests dan recent activity
- **Error Rates**: Success/failure ratios
- **Slow Requests**: Requests yang memakan waktu lama

## 🛠️ **Integration Examples**

### **Frontend Dashboard Integration**
```javascript
// Fetch monitoring stats untuk dashboard
const fetchMonitoringStats = async () => {
  try {
    const response = await fetch('/api/monitoring/stats');
    const data = await response.json();
    
    if (data.success) {
      updateDashboard(data.data);
    }
  } catch (error) {
    console.error('Failed to fetch monitoring stats:', error);
  }
};

// Health check untuk status indicator
const checkHealth = async () => {
  try {
    const response = await fetch('/api/monitoring/health');
    const data = await response.json();
    
    updateHealthIndicator(data.health.status);
  } catch (error) {
    updateHealthIndicator('unhealthy');
  }
};
```

### **Uptime Monitoring Integration**
```bash
# Script untuk external uptime monitoring
#!/bin/bash

BACKEND_URL="https://your-hf-space.hf.space"
HEALTH_ENDPOINT="$BACKEND_URL/health"

# Check health
response=$(curl -s -w "%{http_code}" "$HEALTH_ENDPOINT")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ Backend is healthy"
    exit 0
else
    echo "❌ Backend is unhealthy (HTTP $http_code)"
    exit 1
fi
```

### **Alerting Integration**
```python
import requests
import time

def check_backend_health(backend_url):
    """Check backend health dan send alerts jika perlu"""
    try:
        response = requests.get(f"{backend_url}/api/monitoring/health", timeout=10)
        data = response.json()
        
        if data['health']['status'] != 'healthy':
            send_alert(f"Backend unhealthy: {data['health']['issues']}")
            
        # Check error rate
        stats_response = requests.get(f"{backend_url}/api/monitoring/stats", timeout=10)
        stats_data = stats_response.json()
        
        if stats_data['data']['error_rate_percent'] > 10:
            send_alert(f"High error rate: {stats_data['data']['error_rate_percent']}%")
            
    except Exception as e:
        send_alert(f"Failed to check backend health: {e}")

def send_alert(message):
    """Send alert via email, Slack, etc."""
    print(f"🚨 ALERT: {message}")
    # Implement your alerting logic here
```

## 📊 **Dashboard Examples**

### **Simple Status Dashboard**
```html
<!DOCTYPE html>
<html>
<head>
    <title>OpenHands Backend Status</title>
    <style>
        .healthy { color: green; }
        .degraded { color: orange; }
        .unhealthy { color: red; }
        .metric { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Backend Status</h1>
    <div id="status"></div>
    <div id="metrics"></div>
    
    <script>
        async function updateStatus() {
            try {
                // Health check
                const healthResponse = await fetch('/api/monitoring/health');
                const healthData = await healthResponse.json();
                
                document.getElementById('status').innerHTML = `
                    <h2 class="${healthData.health.status}">
                        Status: ${healthData.health.status.toUpperCase()}
                    </h2>
                    <p>Uptime: ${healthData.health.uptime}</p>
                `;
                
                // Stats
                const statsResponse = await fetch('/api/monitoring/stats');
                const statsData = await statsResponse.json();
                
                document.getElementById('metrics').innerHTML = `
                    <div class="metric">Total Requests: ${statsData.data.total_requests}</div>
                    <div class="metric">Error Rate: ${statsData.data.error_rate_percent}%</div>
                    <div class="metric">Avg Response Time: ${statsData.data.avg_response_time_ms}ms</div>
                    <div class="metric">CPU Usage: ${statsData.data.current_system?.cpu_percent || 'N/A'}%</div>
                    <div class="metric">Memory Usage: ${statsData.data.current_system?.memory_percent || 'N/A'}%</div>
                `;
                
            } catch (error) {
                document.getElementById('status').innerHTML = `
                    <h2 class="unhealthy">Status: ERROR</h2>
                    <p>Failed to fetch status</p>
                `;
            }
        }
        
        // Update every 30 seconds
        updateStatus();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"psutil not available"**
   - Solution: Install psutil dengan `pip install psutil>=5.9.0`
   - Fallback: Basic monitoring endpoints tetap tersedia

2. **High memory usage**
   - Check: Metrics retention settings
   - Solution: Reduce `max_requests` di MetricsCollector

3. **Monitoring not starting**
   - Check: System permissions untuk resource monitoring
   - Check: Background task execution

### **Performance Tuning**

- **Metrics Retention**: Adjust `max_requests` parameter
- **Monitoring Interval**: Change system monitoring interval
- **Log Level**: Adjust logging level untuk performance

## 🚀 **Deployment Considerations**

### **Hugging Face Spaces**
- ✅ **Resource Monitoring**: Works dengan HF Spaces limitations
- ✅ **Background Tasks**: Monitoring tasks run properly
- ✅ **Memory Efficient**: Optimized untuk free tier
- ✅ **No External Dependencies**: Self-contained monitoring

### **Production Deployment**
- **Load Balancer Health Checks**: Use `/health` endpoint
- **Monitoring Integration**: Connect dengan external monitoring tools
- **Alerting**: Setup alerts berdasarkan health status
- **Log Aggregation**: Integrate dengan log management systems

## 📈 **Benefits**

### **For Developers**
- **Debug Performance Issues**: Identify slow endpoints
- **Monitor Resource Usage**: Track system utilization
- **Error Analysis**: Comprehensive error tracking
- **Usage Analytics**: Understand API usage patterns

### **For Operations**
- **Uptime Monitoring**: Real-time health status
- **Performance Monitoring**: Response time tracking
- **Capacity Planning**: Resource usage trends
- **Incident Response**: Quick issue identification

## 🎯 **Best Practices**

1. **Regular Monitoring**: Check health status regularly
2. **Set Alerts**: Configure alerts untuk critical issues
3. **Performance Baselines**: Establish normal performance metrics
4. **Log Analysis**: Review logs untuk patterns dan issues
5. **Resource Planning**: Monitor trends untuk capacity planning

---

**📊 Enhanced monitoring memberikan visibility lengkap ke dalam backend performance dan health!**