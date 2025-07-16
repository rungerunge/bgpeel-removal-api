import requests
import base64

def test_background_removal(image_path='image.png'):
    """Test the background removal API with the handbag image"""
    print(f"Testing background removal with {image_path}...")
    
    # Test with production server
    api_url = "https://bgpeel-api-production-0aa2.up.railway.app"
    
    # Prepare the image file
    with open(image_path, 'rb') as img_file:
        files = {'file': ('handbag.png', img_file, 'image/png')}
        
        # Test both response types
        for return_type in ['base64', 'direct']:
            print(f"\nTesting {return_type} response...")
            try:
                response = requests.post(
                    f"{api_url}/remove-background",
                    files=files,
                    data={'return_type': return_type}
                )
                
                if response.status_code == 200:
                    output_path = f'handbag_no_bg_{return_type}.png'
                    
                    if return_type == 'base64':
                        # Save the base64 processed image
                        base64_image = response.json()['image']
                        image_data = base64.b64decode(base64_image)
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        print(f"✅ Base64 test successful!")
                        print(f"Processing time: {response.json().get('process_time', 'N/A')}s")
                    else:
                        # Save the direct processed image
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Direct response test successful!")
                        print(f"Processing time: {response.headers.get('X-Process-Time', 'N/A')}s")
                        
                    print(f"Processed image saved as: {output_path}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(response.json())
                    
            except Exception as e:
                print(f"❌ Error testing {return_type} response: {str(e)}")
            
            # Reset file pointer for next test
            img_file.seek(0)

if __name__ == "__main__":
    test_background_removal() 