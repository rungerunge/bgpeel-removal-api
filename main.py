from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from rembg import remove, new_session
from PIL import Image
import io
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="BGPeel Background Removal API",
    description="API for removing backgrounds from images using REMBG SILUETA model",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bgpeel.com",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize REMBG session
session = new_session()  # Using default model since SILUETA is not available in newer versions

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def is_valid_file(filename: str) -> bool:
    return filename.lower().split(".")[-1] in ALLOWED_EXTENSIONS

@app.get("/")
async def root():
    return {
        "message": "BGPeel Background Removal API",
        "version": "1.0.0",
        "endpoints": {
            "/remove-background": "POST - Remove background from image",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not is_valid_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Allowed types: PNG, JPG, JPEG"
            )
        
        # Read and validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )
        
        # Process image
        input_image = Image.open(io.BytesIO(contents))
        
        # Remove background
        output_image = remove(input_image, session=session)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Convert to base64
        base64_image = base64.b64encode(img_byte_arr).decode()
        
        return JSONResponse(content={
            "status": "success",
            "message": "Background removed successfully",
            "image": base64_image
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port) 