# run_app.py (ใส่โค้ดนี้ก่อนรัน build.bat)
import sys
import os
import traceback
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from src.main import main

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\nCRITICAL ERROR:")
        traceback.print_exc()
    finally:
        # บรรทัดนี้สำคัญมาก! ทำให้หน้าจอค้างรอ User กดปิด
        input("\nPress Enter to exit...")