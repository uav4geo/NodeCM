from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def get_image_size(file_path, fallback_on_error=True):
    """
    Return (width, height) for a given img file
    """
    with Image.open(file_path) as img:
        width, height = img.size
    return (width, height)