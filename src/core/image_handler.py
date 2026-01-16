import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging

# Setup Logger
logger = logging.getLogger(__name__)

class ImageHandler:
    def __init__(self, retries=3, backoff_factor=0.3):
        self.session = requests.Session()
        
        # Setup Retry Strategy
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Add User-Agent to mimic a browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def download_image(self, url: str) -> BytesIO:
        """
        Downloads an image and returns it as a BytesIO object.
        Returns None if download fails after retries.
        """
        try:
            # timeout=10 seconds
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return None

    def create_placeholder(self, text: str, width: int = 655, height: int = 1200) -> BytesIO:
        """
        Creates a placeholder image in memory (White background + Text).
        """
        try:
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Font handling
            font_size = min(width, height) // 20
            try:
                # Try loading Arial (common on Windows)
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            # Calculate text size (Compatibility for old/new Pillow)
            try:
                # Modern Pillow
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                # Older Pillow
                text_width, text_height = draw.textsize(text, font=font)

            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill='gray', font=font)
            # Add a border
            draw.rectangle([0, 0, width-1, height-1], outline='lightgray', width=2)
            
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            return buf
            
        except Exception as e:
            logger.error(f"Error creating placeholder: {e}")
            # Fallback: Create a tiny 1x1 white pixel if everything fails
            fallback = Image.new('RGB', (1, 1), color='white')
            buf = BytesIO()
            fallback.save(buf, format='PNG')
            buf.seek(0)
            return buf

    def get_image(self, url: str, placeholder_text: str = "N/A") -> BytesIO:
        """
        High-level function: Tries to download. If fails, returns placeholder.
        Always returns a valid BytesIO image.
        """
        img_stream = self.download_image(url)
        if img_stream:
            return img_stream
        
        print(f"[INFO] Generating placeholder for: {url}")
        return self.create_placeholder(f"Image Not Found:\n{placeholder_text}")

# --- Test Block ---
if __name__ == "__main__":
    handler = ImageHandler()
    
    # 1. Test Download (Google Logo)
    test_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
    print(f"Testing download from: {test_url}")
    img_data = handler.get_image(test_url)
    print(f"Result size: {img_data.getbuffer().nbytes} bytes")
    
    # 2. Test Placeholder (Invalid URL)
    print("Testing placeholder generation...")
    fail_data = handler.get_image("https://invalid-url.com/nothing.png", "Test Placeholder")
    print(f"Placeholder size: {fail_data.getbuffer().nbytes} bytes")