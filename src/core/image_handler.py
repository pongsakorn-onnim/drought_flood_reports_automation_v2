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
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def download_image(self, url: str) -> BytesIO:
        """
        Downloads an image. Returns None if fails (logs warning).
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
            
        except requests.exceptions.HTTPError as e:
            # [Clean Log] บอกแค่ URL และ Status Code พอ
            status = e.response.status_code
            logger.warning(f"Image not found: {url} (Status: {status})")
            return None
            
        except Exception as e:
            logger.warning(f"Download failed: {url} ({e})")
            return None

    def create_placeholder(self, text: str, width: int = 655, height: int = 1200) -> BytesIO:
        """
        Creates a placeholder image in memory.
        """
        try:
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Font handling
            font_size = min(width, height) // 20
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            # Text handling
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                text_width, text_height = draw.textsize(text, font=font)

            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill='gray', font=font)
            draw.rectangle([0, 0, width-1, height-1], outline='lightgray', width=2)
            
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            # [Clean Log] บอกแค่ว่าสร้าง Placeholder เสร็จแล้ว (ไม่ต้องบอก path/size)
            # .replace เพื่อให้ log อยู่บรรทัดเดียวสวยๆ
            clean_text = text.replace('\n', ' ').replace('\r', '')
            logger.info(f"-> Generated placeholder instead. (Text: '{clean_text}')")
            
            return buf
            
        except Exception as e:
            logger.error(f"Error creating placeholder: {e}")
            fallback = Image.new('RGB', (1, 1), color='white')
            buf = BytesIO()
            fallback.save(buf, format='PNG')
            buf.seek(0)
            return buf

    def get_image(self, url: str, placeholder_text: str = "N/A") -> BytesIO:
        """
        Tries to download. If fails, returns placeholder immediately.
        """
        img_stream = self.download_image(url)
        if img_stream:
            return img_stream
        
        # [Clean Log] ลบ log "Attempting..." ทิ้งไปเลย เพราะข้างบนมี Warning แล้ว
        # และข้างล่างก็จะมี Info บอกว่าสร้าง placeholder
        
        return self.create_placeholder(f"Image Not Found:\n{placeholder_text}")