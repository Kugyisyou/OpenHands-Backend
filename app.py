"""
OpenHands Backend optimized for Hugging Face Spaces deployment
Final fixed version that handles all import issues
"""
import os
import sys
import logging
import uvicorn
import time
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_hf_environment():
    """Setup environment variables for Hugging Face Spaces"""
    
    # Core HF Spaces configuration
    os.environ.setdefault("PORT", "7860")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("OPENHANDS_RUNTIME", "local")  # Use local runtime, not docker
    os.environ.setdefault("CORS_ALLOWED_ORIGINS", "*")
    
    # Use memory-based storage to avoid file permission issues
    os.environ["SETTINGS_STORE_TYPE"] = "memory"
    os.environ["SECRETS_STORE_TYPE"] = "memory"
    os.environ["CONVERSATION_STORE_TYPE"] = "memory"
    os.environ["FILE_STORE"] = "memory"
    os.environ["SESSION_STORE_TYPE"] = "memory"
    
    # Disable security and auth for public API
    os.environ["DISABLE_SECURITY"] = "true"
    os.environ["OPENHANDS_DISABLE_AUTH"] = "true"
    os.environ["SECURITY_CONFIRMATION_MODE"] = "false"
    
    # Disable file-based features that might cause issues
    os.environ["DISABLE_FILE_LOGGING"] = "true"
    os.environ["DISABLE_PERSISTENT_SESSIONS"] = "true"
    os.environ["SERVE_FRONTEND"] = "false"
    
    # Set reasonable defaults for public usage
    os.environ.setdefault("MAX_ITERATIONS", "30")
    os.environ.setdefault("DEFAULT_AGENT", "CodeActAgent")
    
    # LLM configuration - use OpenRouter by default
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("⚠️  LLM_API_KEY or OPENROUTER_API_KEY not set. Please set it in HF Spaces environment variables.")
        logger.warning("⚠️  Without API key, the backend will start but LLM calls will fail.")
    else:
        logger.info("✅ LLM API key found")
        # Ensure LLM_API_KEY is set to the OpenRouter key
        os.environ["LLM_API_KEY"] = api_key
    
    # Fixed model name format for OpenRouter (remove openrouter/ prefix)
    os.environ.setdefault("LLM_MODEL", "anthropic/claude-3.5-sonnet")
    os.environ.setdefault("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Force OpenRouter provider to avoid direct Anthropic connection
    os.environ.setdefault("LLM_CUSTOM_LLM_PROVIDER", "openrouter")
    
    # Create directories if they don't exist
    directories = ["/tmp/openhands", "/tmp/cache", "/tmp/workspace", "/tmp/file_store"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ Environment configured for Hugging Face Spaces")

def check_dependencies():
    """Check if critical dependencies are available"""
    missing_deps = []
    
    try:
        import fastapi
        logger.info("✅ FastAPI available")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
        logger.info("✅ Uvicorn available")
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import litellm
        logger.info("✅ LiteLLM available")
    except ImportError:
        missing_deps.append("litellm")
    
    # Check optional dependencies
    try:
        import docker
        logger.info("⚠️  Docker available (not needed for HF Spaces)")
    except ImportError:
        logger.info("✅ Docker not available (expected for HF Spaces)")
    
    # Google Cloud is COMPLETELY OPTIONAL - no login required, no API key needed
    # This is just for informational purposes only
    try:
        import google.api_core
        logger.info("⚠️  Google Cloud available (OPTIONAL - not needed for basic functionality)")
    except ImportError:
        logger.info("✅ Google Cloud not available (PERFECTLY FINE - no login/API key required)")
    
    if missing_deps:
        logger.error(f"❌ Missing critical dependencies: {missing_deps}")
        return False
    
    return True

def setup_fizzo_automation():
    """Setup Fizzo automation dependencies"""
    try:
        import playwright
        logger.info("✅ Playwright available for Fizzo automation")
        
        # Auto-install browsers if needed
        try:
            import subprocess
            import sys
            logger.info("🎭 Installing Playwright browsers...")
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install", "chromium"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Playwright Chromium installed successfully")
            else:
                logger.warning(f"⚠️ Playwright install failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Could not auto-install Playwright browsers: {e}")
            
        return True
    except ImportError:
        logger.warning("⚠️ Playwright not available - Fizzo automation disabled")
        return False

if __name__ == "__main__":
    try:
        logger.info("🔧 Setting up Hugging Face environment...")
        setup_hf_environment()
        
        logger.info("🔍 Checking dependencies...")
        if not check_dependencies():
            logger.error("❌ Critical dependencies missing. Cannot start server.")
            sys.exit(1)
            
        logger.info("🎭 Setting up Fizzo automation...")
        fizzo_available = setup_fizzo_automation()
        
        logger.info("📦 Importing OpenHands app...")
        from openhands.server.app import app
        
        # Add Fizzo automation endpoint if available
        if fizzo_available:
            try:
                from fastapi import HTTPException
                from pydantic import BaseModel
                import asyncio
                
                # Import Fizzo automation with fallback
                try:
                    from fizzo_automation import fizzo_auto_update
                    logger.info("✅ Fizzo automation module loaded")
                except ImportError as e:
                    logger.error(f"❌ Could not import fizzo_automation: {e}")
                    logger.info("🔧 Creating inline Fizzo automation...")
                    
                    # Inline Fizzo automation implementation
                    async def fizzo_auto_update(email: str, password: str, chapter_title: str, chapter_content: str):
                        """Inline Fizzo automation implementation"""
                        try:
                            from playwright.async_api import async_playwright
                            
                            # Validate input
                            if not email or not password:
                                return {"success": False, "error": "Email and password are required"}
                            if not chapter_title or not chapter_content:
                                return {"success": False, "error": "Chapter title and content are required"}
                            if len(chapter_content) < 1000:
                                return {"success": False, "error": "Chapter content must be at least 1,000 characters"}
                            if len(chapter_content) > 60000:
                                return {"success": False, "error": "Chapter content must be less than 60,000 characters"}
                            
                            logger.info("🚀 Starting Fizzo auto-update process...")
                            
                            playwright = await async_playwright().start()
                            browser = await playwright.chromium.launch(
                                headless=True,
                                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                            )
                            page = await browser.new_page()
                            
                            try:
                                # Navigate to fizzo.org
                                await page.goto("https://fizzo.org", wait_until='networkidle', timeout=30000)
                                
                                # Click hamburger menu
                                await page.click('button:has-text("☰")')
                                await asyncio.sleep(1)
                                
                                # Click "Menulis Cerita"
                                await page.click('text="Menulis Cerita"')
                                await asyncio.sleep(2)
                                
                                # Click "Lanjutkan dengan Email"
                                await page.click('text="Lanjutkan dengan Email"')
                                await asyncio.sleep(2)
                                
                                # Fill login form
                                await page.fill('input[type="email"]', email)
                                await page.fill('input[type="password"]', password)
                                await page.click('button:has-text("Lanjut")')
                                
                                # Wait for dashboard
                                await page.wait_for_url('**/mobile/**', timeout=15000)
                                
                                # Click "New Chapter"
                                await page.click('text="New Chapter"')
                                await asyncio.sleep(3)
                                
                                # Fill chapter form
                                await page.fill('input[placeholder*="chapter name"]', chapter_title)
                                await page.fill('textarea[placeholder*="Start writing"]', chapter_content)
                                await asyncio.sleep(3)
                                
                                # Publish chapter
                                await page.click('button:has-text("✈️")')
                                await asyncio.sleep(5)
                                
                                return {
                                    "success": True,
                                    "message": "Chapter created successfully",
                                    "chapter_title": chapter_title,
                                    "content_length": len(chapter_content)
                                }
                                
                            finally:
                                await browser.close()
                                await playwright.stop()
                                
                        except Exception as e:
                            logger.error(f"❌ Fizzo automation failed: {e}")
                            return {"success": False, "error": str(e)}
                
                class FizzoUpdateRequest(BaseModel):
                    email: str
                    password: str
                    chapter_title: str
                    chapter_content: str
                
                @app.post("/api/fizzo-auto-update")
                async def fizzo_update_endpoint(request: FizzoUpdateRequest):
                    """
                    Auto-update novel chapter ke fizzo.org
                    
                    Requires:
                    - email: Email login fizzo.org
                    - password: Password login fizzo.org  
                    - chapter_title: Judul chapter (contoh: "Bab 28")
                    - chapter_content: Isi chapter (1,000-60,000 karakter)
                    """
                    try:
                        # Validate authentication (gunakan existing auth system)
                        # Note: Bisa ditambahkan Bearer token validation di sini
                        
                        logger.info(f"🚀 Starting Fizzo auto-update for chapter: {request.chapter_title}")
                        
                        # Run automation
                        result = await fizzo_auto_update(
                            email=request.email,
                            password=request.password,
                            chapter_title=request.chapter_title,
                            chapter_content=request.chapter_content
                        )
                        
                        if result.get("success"):
                            logger.info("✅ Fizzo auto-update successful")
                            return {
                                "success": True,
                                "message": "Chapter berhasil diupload ke fizzo.org",
                                "data": result
                            }
                        else:
                            logger.error(f"❌ Fizzo auto-update failed: {result.get('error')}")
                            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
                            
                    except Exception as e:
                        logger.error(f"❌ Fizzo endpoint error: {e}")
                        raise HTTPException(status_code=500, detail=str(e))
                    
                logger.info("✅ Fizzo automation endpoint added: /api/fizzo-auto-update")
                
            except Exception as e:
                logger.error(f"❌ Failed to setup Fizzo automation endpoint: {e}")
                logger.warning("⚠️ Fizzo automation will not be available")
        
        # Add Enhanced Monitoring endpoints
        try:
            logger.info("📊 Setting up enhanced monitoring...")
            
            # Import monitoring system
            try:
                from monitoring import (
                    get_monitoring_stats, 
                    get_health_check, 
                    start_system_monitoring,
                    create_monitoring_middleware
                )
                
                # Add monitoring middleware
                from starlette.middleware.base import BaseHTTPMiddleware
                
                class MonitoringMiddleware(BaseHTTPMiddleware):
                    async def dispatch(self, request, call_next):
                        start_time = time.time()
                        
                        try:
                            response = await call_next(request)
                            response_time = time.time() - start_time
                            
                            # Log successful requests
                            if hasattr(request.state, 'endpoint_name'):
                                endpoint = request.state.endpoint_name
                            else:
                                endpoint = str(request.url.path)
                            
                            logger.info(f"📊 {request.method} {endpoint} - {response.status_code} - {response_time:.3f}s")
                            
                            return response
                            
                        except Exception as e:
                            response_time = time.time() - start_time
                            logger.error(f"❌ {request.method} {str(request.url.path)} - ERROR - {response_time:.3f}s - {str(e)}")
                            raise e
                
                app.add_middleware(MonitoringMiddleware)
                
                # Add monitoring endpoints
                @app.get("/api/monitoring/stats")
                async def monitoring_stats():
                    """Get comprehensive monitoring statistics"""
                    try:
                        stats = get_monitoring_stats()
                        return {
                            "success": True,
                            "data": stats,
                            "timestamp": time.time()
                        }
                    except Exception as e:
                        logger.error(f"❌ Monitoring stats error: {e}")
                        return {
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                
                @app.get("/api/monitoring/health")
                async def health_check():
                    """Health check endpoint with detailed status"""
                    try:
                        health = get_health_check()
                        return {
                            "success": True,
                            "health": health,
                            "timestamp": time.time()
                        }
                    except Exception as e:
                        logger.error(f"❌ Health check error: {e}")
                        return {
                            "success": False,
                            "error": str(e),
                            "status": "unhealthy",
                            "timestamp": time.time()
                        }
                
                @app.get("/health")
                async def simple_health():
                    """Simple health check for load balancers"""
                    return {"status": "ok", "timestamp": time.time()}
                
                # Start system monitoring in background
                async def start_monitoring_task():
                    try:
                        await start_system_monitoring(interval=30)
                    except Exception as e:
                        logger.error(f"❌ System monitoring error: {e}")
                
                # Schedule monitoring task
                asyncio.create_task(start_monitoring_task())
                
                logger.info("✅ Enhanced monitoring endpoints added:")
                logger.info("   📊 /api/monitoring/stats - Detailed statistics")
                logger.info("   🏥 /api/monitoring/health - Health check")
                logger.info("   ❤️ /health - Simple health check")
                
            except ImportError as e:
                logger.warning(f"⚠️ Monitoring module not available: {e}")
                logger.info("🔧 Creating basic monitoring endpoints...")
                
                # Basic monitoring fallback
                @app.get("/health")
                async def basic_health():
                    """Basic health check"""
                    return {"status": "ok", "timestamp": time.time()}
                
                @app.get("/api/monitoring/health")
                async def basic_health_detailed():
                    """Basic health check with more details"""
                    return {
                        "success": True,
                        "health": {
                            "status": "healthy",
                            "uptime": "unknown",
                            "timestamp": time.time()
                        }
                    }
                
                logger.info("✅ Basic monitoring endpoints added")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup monitoring: {e}")
            logger.warning("⚠️ Enhanced monitoring will not be available")
        
        # Get configuration
        port = int(os.getenv("PORT", 7860))
        host = os.getenv("HOST", "0.0.0.0")
        
        # Startup information
        print("\n" + "="*50)
        print("🤗 OpenHands Backend for Hugging Face Spaces")
        print("="*50)
        print(f"🚀 Server: {host}:{port}")
        print(f"🔑 LLM API Key: {'✅ Set' if os.getenv('LLM_API_KEY') else '❌ Missing'}")
        print(f"🤖 LLM Model: {os.getenv('LLM_MODEL', 'Not configured')}")
        print(f"🏃 Runtime: {os.getenv('OPENHANDS_RUNTIME', 'local')}")
        print("📡 API Endpoints available at /docs")
        print("="*50 + "\n")
        
        logger.info("🚀 Starting uvicorn server...")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 This usually means a required dependency is missing.")
        logger.error("💡 Check that all dependencies in requirements.txt are installed.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)