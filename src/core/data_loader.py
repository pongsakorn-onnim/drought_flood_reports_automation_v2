import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class DataLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_config(self) -> Dict[str, Any]:
        """Returns the entire configuration dictionary."""
        return self.config

    def get_url(self, source_config: Dict[str, Any], pattern_key: str, **kwargs) -> str:
        """
        Generates a URL by formatting the pattern found in source_config.
        
        Args:
            source_config: The 'data_sources' dictionary from the config.
            pattern_key: The key of the pattern to use (e.g., 'rain_pattern').
            **kwargs: Dynamic values to fill in the pattern (e.g., yyyymm='202601', lead=1).
            
        Returns:
            The fully formatted URL string.
        """
        if pattern_key not in source_config:
            raise KeyError(f"Pattern '{pattern_key}' not found in data_sources config.")

        raw_pattern = source_config[pattern_key]
        base_url = source_config.get('base_url', '')

        # Step 1: Inject base_url if placeholder exists
        # ใช้ .replace ตรงๆ เพื่อความง่ายและชัดเจน
        url_template = raw_pattern.replace("{base_url}", base_url)

        # Step 2: Inject dynamic values (yyyymm, lead, etc.)
        try:
            return url_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing parameter for URL pattern '{pattern_key}': {e}")

# --- Test Block (สำหรับรันเทสไฟล์นี้เดี่ยวๆ) ---
if __name__ == "__main__":
    # ลองเทสดูว่าอ่าน Config ออกมาเป็น URL ได้จริงไหม
    try:
        loader = DataLoader() # อ่าน config.yaml ที่ root
        config = loader.get_config()
        
        # สมมติว่าเรากำลังทำ Flood Report
        flood_sources = config['flood_report']['data_sources']
        
        # ลองเจน URL เล่นๆ
        test_url = loader.get_url(
            flood_sources, 
            'rain_pattern', 
            yyyymm='202601', 
            lead=1
        )
        print(f"Generated URL: {test_url}")
        
    except Exception as e:
        print(f"Error: {e}")