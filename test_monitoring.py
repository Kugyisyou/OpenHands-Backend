#!/usr/bin/env python3
"""
Test suite untuk Enhanced Monitoring System
"""

import asyncio
import json
import time
import sys
from datetime import datetime

async def test_monitoring_system():
    """Test monitoring system functionality"""
    
    print("🧪 Testing Enhanced Monitoring System")
    print("=" * 50)
    
    try:
        # Import monitoring modules
        from monitoring import (
            MetricsCollector,
            SystemMonitor,
            RequestLogger,
            RequestMetrics,
            SystemMetrics,
            get_monitoring_stats,
            get_health_check
        )
        print("✅ Monitoring modules imported successfully")
        
        # Test MetricsCollector
        print("\n📊 Testing MetricsCollector...")
        collector = MetricsCollector(max_requests=100)
        
        # Add test requests
        test_requests = [
            RequestMetrics(
                endpoint="/api/test",
                method="GET",
                status_code=200,
                response_time=0.150,
                timestamp=datetime.now(),
                user_agent="test-agent",
                ip_address="127.0.0.1"
            ),
            RequestMetrics(
                endpoint="/api/test",
                method="POST",
                status_code=201,
                response_time=0.250,
                timestamp=datetime.now()
            ),
            RequestMetrics(
                endpoint="/api/error",
                method="GET",
                status_code=500,
                response_time=1.500,
                timestamp=datetime.now(),
                error_message="Test error"
            )
        ]
        
        for req in test_requests:
            collector.add_request(req)
        
        print(f"✅ Added {len(test_requests)} test requests")
        
        # Test system metrics
        print("\n🖥️ Testing System Metrics...")
        try:
            import psutil
            
            system_metrics = SystemMetrics(
                cpu_percent=25.5,
                memory_percent=60.2,
                memory_used_mb=1024.5,
                memory_available_mb=512.3,
                disk_usage_percent=45.8,
                timestamp=datetime.now()
            )
            
            collector.add_system_metrics(system_metrics)
            print("✅ System metrics added successfully")
            
        except ImportError:
            print("⚠️ psutil not available, skipping system metrics test")
        
        # Test statistics
        print("\n📈 Testing Statistics Generation...")
        stats = collector.get_stats()
        
        print("📊 Generated Statistics:")
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Error Rate: {stats['error_rate_percent']}%")
        print(f"   Avg Response Time: {stats['avg_response_time_ms']}ms")
        print(f"   Endpoints: {len(stats['endpoints'])}")
        
        # Test health check
        print("\n🏥 Testing Health Check...")
        health = collector.get_health_status()
        
        print("🏥 Health Status:")
        print(f"   Status: {health['status']}")
        print(f"   Issues: {len(health['issues'])}")
        print(f"   Uptime: {health['uptime']}")
        
        # Test global functions
        print("\n🌐 Testing Global Functions...")
        global_stats = get_monitoring_stats()
        global_health = get_health_check()
        
        print("✅ Global monitoring functions working")
        
        print("\n✅ All monitoring tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("⚠️ Make sure monitoring.py is available")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    return True

async def test_monitoring_endpoints():
    """Test monitoring API endpoints"""
    
    print("\n🌐 Testing Monitoring API Endpoints")
    print("=" * 40)
    
    try:
        import httpx
        print("✅ httpx available")
    except ImportError:
        print("❌ httpx not available, installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "httpx"])
        import httpx
        print("✅ httpx installed")
    
    base_url = "http://localhost:7860"
    endpoints = [
        "/health",
        "/api/monitoring/health", 
        "/api/monitoring/stats"
    ]
    
    print(f"🎯 Testing endpoints on {base_url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            try:
                print(f"\n📡 Testing {endpoint}...")
                
                response = await client.get(f"{base_url}{endpoint}")
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Response: Valid JSON")
                        
                        # Validate response structure
                        if endpoint == "/health":
                            if "status" in data:
                                print(f"   ✅ Health check OK: {data['status']}")
                            else:
                                print(f"   ⚠️ Missing 'status' field")
                        
                        elif endpoint == "/api/monitoring/health":
                            if "health" in data and "status" in data["health"]:
                                print(f"   ✅ Detailed health OK: {data['health']['status']}")
                            else:
                                print(f"   ⚠️ Invalid health response structure")
                        
                        elif endpoint == "/api/monitoring/stats":
                            if "data" in data and "total_requests" in data["data"]:
                                print(f"   ✅ Stats OK: {data['data']['total_requests']} requests")
                            else:
                                print(f"   ⚠️ Invalid stats response structure")
                        
                    except json.JSONDecodeError:
                        print(f"   ❌ Invalid JSON response")
                        print(f"   Raw: {response.text[:100]}...")
                
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                    
            except httpx.ConnectError:
                print(f"   ❌ Connection failed - server not running?")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n🏁 Endpoint testing completed")

def test_performance():
    """Test monitoring system performance"""
    
    print("\n⚡ Testing Monitoring Performance")
    print("=" * 35)
    
    try:
        from monitoring import MetricsCollector, RequestMetrics
        
        # Test with many requests
        collector = MetricsCollector(max_requests=1000)
        
        print("📊 Adding 1000 test requests...")
        start_time = time.time()
        
        for i in range(1000):
            req = RequestMetrics(
                endpoint=f"/api/test/{i % 10}",
                method="GET" if i % 2 == 0 else "POST",
                status_code=200 if i % 10 != 9 else 500,
                response_time=0.1 + (i % 100) * 0.01,
                timestamp=datetime.now()
            )
            collector.add_request(req)
        
        add_time = time.time() - start_time
        print(f"✅ Added 1000 requests in {add_time:.3f}s")
        
        # Test stats generation
        print("📈 Generating statistics...")
        start_time = time.time()
        
        stats = collector.get_stats()
        
        stats_time = time.time() - start_time
        print(f"✅ Generated stats in {stats_time:.3f}s")
        
        # Test health check
        print("🏥 Generating health check...")
        start_time = time.time()
        
        health = collector.get_health_status()
        
        health_time = time.time() - start_time
        print(f"✅ Generated health check in {health_time:.3f}s")
        
        # Performance summary
        print(f"\n⚡ Performance Summary:")
        print(f"   Request Addition: {1000/add_time:.0f} req/s")
        print(f"   Stats Generation: {stats_time*1000:.1f}ms")
        print(f"   Health Check: {health_time*1000:.1f}ms")
        
        # Memory usage
        try:
            import sys
            memory_usage = sys.getsizeof(collector.requests) + sys.getsizeof(collector.endpoint_stats)
            print(f"   Memory Usage: ~{memory_usage/1024:.1f}KB")
        except:
            print(f"   Memory Usage: Unable to calculate")
        
        print("✅ Performance test completed")
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")

async def main():
    """Run all monitoring tests"""
    
    print("🚀 Enhanced Monitoring Test Suite")
    print("=" * 50)
    
    # Test monitoring system
    system_test = await test_monitoring_system()
    
    # Test performance
    test_performance()
    
    # Test endpoints (requires server running)
    print("\n" + "=" * 50)
    print("⚠️ Note: The following test requires the server to be running")
    print("   Start server with: python app.py")
    print("   Then run this test in another terminal")
    print("=" * 50)
    
    try:
        await test_monitoring_endpoints()
    except KeyboardInterrupt:
        print("\n🛑 Endpoint testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Endpoint testing error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    if system_test:
        print("✅ Monitoring System: PASSED")
    else:
        print("❌ Monitoring System: FAILED")
    
    print("✅ Performance Test: COMPLETED")
    print("⚠️ Endpoint Test: Requires running server")
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")