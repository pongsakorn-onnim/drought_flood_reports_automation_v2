# src/core/logging_config.py
from __future__ import annotations
import logging
from pathlib import Path

# ต้องลง rich ใน requirements.txt ด้วยนะครับ
try:
    from rich.logging import RichHandler
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Format สำหรับ File Log (ยังคงเก็บละเอียดเหมือนเดิม)
FILE_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    quiet: bool = False,
    console_style: str = "dev",  # "dev" หรือ "user"
    file_level: str | None = None,
) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG) # ปล่อยให้ Root รับทุกอย่าง Handler ค่อยกรองเอง

    # ล้าง handler เก่า
    for h in list(root.handlers):
        root.removeHandler(h)

    # ---- 1. Console Handler (พระเอกของเรา) ----
    if not quiet:
        console_level = getattr(logging, level.upper(), logging.INFO)
        
        if RICH_AVAILABLE:
            # ถ้าเป็น style user เราจะปิด path ปิด time (หรือเปิด time แบบสั้น) ให้ดูคลีนๆ
            is_user_mode = (console_style == "user")
            
            rich_handler = RichHandler(
                level=console_level,
                rich_tracebacks=True,       # Error สวย
                markup=True,                # รองรับการใส่สีใน string
                show_path=not is_user_mode, # User mode ไม่โชว์ path ไฟล์ python
                show_time=True,             # โชว์เวลา
                show_level=True,
                log_time_format="[%X]" if is_user_mode else "[%Y-%m-%d %H:%M:%S]"
            )
            root.addHandler(rich_handler)
        else:
            # Fallback กรณีไม่มี lib rich
            ch = logging.StreamHandler()
            ch.setLevel(console_level)
            fmt = "[%(levelname)s] %(message)s"
            ch.setFormatter(logging.Formatter(fmt))
            root.addHandler(ch)

    # ---- 2. File Handler (เก็บลงไฟล์ละเอียดๆ) ----
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        effective_file_level = file_level or level
        fh.setLevel(getattr(logging, effective_file_level.upper(), logging.DEBUG))
        fh.setFormatter(logging.Formatter(fmt=FILE_FMT, datefmt=DATE_FMT))
        root.addHandler(fh)