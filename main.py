from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from rembg import remove, new_session
from PIL import Image
import io
import logging
import uvicorn
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Background Removal API",
    description="API for removing backgrounds from images using the SILUETA model",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bgpeel.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the SILUETA model session
session = new_session('silueta')

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

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
    return {"status": "healthy"}

@app.post("/remove-background")
async def remove_background(
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
    try:
        # Validate file size
        file_size = 0
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )

        # Validate file type
        content_type = file.content_type
        if content_type not in ["image/png", "image/jpeg", "image/jpg"]:
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
            
            if return_type == "base64":
                # Return base64 encoded image
                base64_image = base64.b64encode(output_buffer.getvalue()).decode()
                return JSONResponse(content={"image": base64_image})
            else:
                # Return direct image response
                return Response(
                    content=output_buffer.getvalue(),
                    media_type="image/png"
                )
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing image"
            )
            
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        await file.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 