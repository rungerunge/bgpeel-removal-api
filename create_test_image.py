from PIL import Image, ImageDraw

def create_test_image():
    # Create a new image with a blue background
    width = 400
    height = 400
    background_color = (100, 150, 255)  # Light blue
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Draw a simple shape (circle) in black
    shape_color = (0, 0, 0)  # Black
    center = (width // 2, height // 2)
    radius = 100
    draw.ellipse([
        (center[0] - radius, center[1] - radius),
        (center[0] + radius, center[1] + radius)
    ], fill=shape_color)
    
    # Save the image
    image.save('test_image.jpg', 'JPEG')
    print("Test image created: test_image.jpg")

if __name__ == "__main__":
    create_test_image() 