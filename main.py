from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from rembg import remove, new_session
from PIL import Image
import io
import logging
import uvicorn
import base64
import time
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Background Removal API",
    description="API for removing backgrounds from images using the SILUETA model",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bgpeel.com",
        "http://localhost:3000"
    ] + (["*"] if os.getenv("ENVIRONMENT") != "production" else []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if os.getenv("ENVIRONMENT") != "production" else [
        "bgpeel.com",
        "api.bgpeel.com",
        "bgpeel-api-production-0aa2.up.railway.app"
    ]
)

# Initialize the SILUETA model session
try:
    session = new_session('silueta')
    logger.info("SILUETA model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SILUETA model: {str(e)}")
    raise

# Maximum file size (10MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))

# Request rate limiting
REQUEST_LIMIT = int(os.getenv("REQUEST_LIMIT", 100))  # requests
TIME_WINDOW = int(os.getenv("TIME_WINDOW", 3600))    # seconds
request_history = {}

def is_rate_limited(client_ip: str) -> bool:
    """Check if a client has exceeded the rate limit"""
    now = time.time()
    if client_ip in request_history:
        requests = [t for t in request_history[client_ip] if now - t < TIME_WINDOW]
        request_history[client_ip] = requests
        return len(requests) >= REQUEST_LIMIT
    return False

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add processing time header and handle rate limiting"""
    # Rate limiting
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    # Track request
    if client_ip not in request_history:
        request_history[client_ip] = []
    request_history[client_ip].append(time.time())
    
    # Process time tracking
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "Background Removal API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/remove-background": "POST - Remove background from image",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test model session
        test_img = Image.new('RGB', (1, 1), color='white')
        remove(test_img, session=session)
        return {
            "status": "healthy",
            "model": "operational",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

@app.post("/remove-background")
async def remove_background(
    request: Request,
    file: UploadFile = File(...),
    return_type: str = "base64"  # Options: base64, direct
):
    """
    Remove background from uploaded image
    
    Args:
        file: Image file (PNG, JPG, JPEG)
        return_type: Response format (base64 or direct)
    
    Returns:
        Processed image with transparent background
    """
    start_time = time.time()
    client_ip = request.client.host
    
    try:
        # Validate file size
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size limit exceeded: {file_size} bytes from {client_ip}")
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )

        # Validate file type
        content_type = file.content_type
        if content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            logger.warning(f"Invalid file type: {content_type} from {client_ip}")
            raise HTTPException(
                status_code=415,
                detail="File type not supported. Please upload PNG or JPG/JPEG images"
            )

        # Process image
        try:
            input_image = Image.open(io.BytesIO(contents))
            output_image = remove(input_image, session=session)
            
            # Prepare response
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format="PNG")
            output_buffer.seek(0)
            
            process_time = time.time() - start_time
            logger.info(f"Image processed successfully in {process_time:.2f}s for {client_ip}")
            
            if return_type == "base64":
                # Return base64 encoded image
                base64_image = base64.b64encode(output_buffer.getvalue()).decode()
                return JSONResponse(
                    content={
                        "image": base64_image,
                        "process_time": process_time
                    }
                )
            else:
                # Return direct image response
                return Response(
                    content=output_buffer.getvalue(),
                    media_type="image/png",
                    headers={"X-Process-Time": str(process_time)}
                )
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)} for {client_ip}")
            raise HTTPException(
                status_code=500,
                detail="Error processing image"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling request: {str(e)} for {client_ip}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        await file.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("MAX_WORKERS", 1))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    ) 