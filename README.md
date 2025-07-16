# Background Removal API

A FastAPI-based service that removes backgrounds from images using the SILUETA model. This API serves as the backend for bgpeel.com.

## Features

- Background removal using the REMBG library with SILUETA model
- Support for PNG and JPG/JPEG images
- Multiple response formats (base64 or direct image)
- CORS enabled for bgpeel.com
- File size and type validation
- Error handling and logging
- Health check endpoint

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /remove-background` - Remove background from image

### Remove Background Endpoint

```bash
curl -X POST "https://api.bgpeel.com/remove-background" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -F "return_type=base64"
```

Parameters:
- `file`: Image file (PNG, JPG, JPEG)
- `return_type`: Response format (base64 or direct)

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bg-removal-api.git
cd bg-removal-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Environment Variables

- `PORT`: Port number (default: 8000)
- Additional configuration can be added in `.env` file

## Deployment

This API is deployed on Railway.app. The deployment process is automated through Railway's GitHub integration.

### Railway Setup

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway will automatically detect the Python project and install dependencies
4. The service will be deployed and a domain will be assigned

## Testing

To run the test script:
```bash
python test_api.py
```

## Limitations

- Maximum file size: 10MB
- Supported formats: PNG, JPG, JPEG
- Rate limiting may apply

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 