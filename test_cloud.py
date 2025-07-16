import requests
import base64

def test_background_removal(image_path='image.png'):
    """Test background removal using the remove.bg API"""
    print(f"Testing background removal with {image_path}...")
    
    # Using remove.bg API (you'll need an API key)
    api_url = "https://api.remove.bg/v1.0/removebg"
    
    # Read the image file
    with open(image_path, 'rb') as img_file:
        # Send the request
        try:
            response = requests.post(
                api_url,
                files={'image_file': img_file},
                data={'size': 'auto'},
                headers={'X-Api-Key': 'YOUR-API-KEY'},  # Replace with your API key
            )
            
            if response.status_code == 200:
                # Save the processed image
                output_path = 'handbag_no_bg_cloud.png'
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Background removal successful!")
                print(f"Processed image saved as: {output_path}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Note: This script requires a remove.bg API key.")
    print("Please replace 'YOUR-API-KEY' in the script with your actual API key.")
    print("You can get a free API key at: https://www.remove.bg/api\n")
    test_background_removal() 