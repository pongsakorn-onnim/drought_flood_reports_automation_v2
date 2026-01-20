# src/core/output_manager.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional


Mode = Literal["prod", "dev"]


@dataclass(frozen=True)
class OutputSpec:
    report_type: str               # "flood" | "drought"
    year: int
    month: int
    mode: Mode = "prod"


class OutputManager:
    """
    Output policy (Updated):
      - prod  -> output/<report_type>/<year>/<month>/
      - dev   -> output/<report_type>/<year>/<month>/_dev/
    
    Filename (Official Thai Gov Format):
      - Drought: yyyymm_ผลการวิเคราะห์พื้นที่เสี่ยงแล้งเดือน{Start}-{End}{YY}.pptx
      - Flood:   yyyymm_ผลการวิเคราะห์พื้นที่เสี่ยงอุทกภัย{Start}-{End}{YY}.pptx
      
    Responsibility:
      - Create folders
      - Generate official filename
      - Handle duplicates with Windows style naming: "File (1).pptx"
    """

    def __init__(self, base_output_dir: str | Path = "output"):
        self.base_dir = Path(base_output_dir)

    def build_output_path(
        self,
        spec: OutputSpec,
        now: Optional[datetime] = None,
    ) -> Path:
        """
        Returns the full output filepath with official naming and unique handling.
        Ensures parent directories exist.
        """
        self._validate_spec(spec)

        # 1. Determine Directory Structure: output/type
        out_dir = self.base_dir / spec.report_type  

        if spec.mode == "dev":
            out_dir = out_dir / "_dev"

        out_dir.mkdir(parents=True, exist_ok=True)

        # 2. Generate Official Filename
        filename = self._generate_official_filename(spec)

        # 3. Get Unique Path (Handle duplicates)
        return self._get_unique_filepath(out_dir, filename)

    # --- Helper Functions ---

    def _get_thai_month_abbr(self, month_idx: int) -> str:
        """Helper: แปลงเลขเดือนเป็นชื่อย่อไทย"""
        thai_months = [
            "", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
            "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
        ]
        if 1 <= month_idx <= 12:
            return thai_months[month_idx]
        return ""

    def _generate_official_filename(self, spec: OutputSpec) -> str:
        """
        สร้างชื่อไฟล์ตาม format ราชการ
        """
        # 1. ปี พ.ศ. 2 หลัก (เช่น 2026 -> 69)
        thai_year_short = str(spec.year + 543)[-2:]
        
        # 2. ช่วงเดือน (คำนวณล่วงหน้า 6 เดือน)
        end_month = (spec.month + 5) % 12
        if end_month == 0: end_month = 12
        
        m_start = self._get_thai_month_abbr(spec.month)
        m_end = self._get_thai_month_abbr(end_month)
        
        # 3. เลือกข้อความตามประเภทรายงาน (Drought มีคำว่า 'เดือน', Flood ไม่มี)
        if spec.report_type == "drought":
            topic = "แล้งเดือน"
        else:
            topic = "อุทกภัย"

        # Format: 202601_ผลการวิเคราะห์พื้นที่เสี่ยง...
        return (
            f"{spec.year}{spec.month:02d}_"
            f"ผลการวิเคราะห์พื้นที่เสี่ยง{topic}{m_start}-{m_end}{thai_year_short}.pptx"
        )

    def _get_unique_filepath(self, directory: Path, filename: str) -> Path:
        """
        เช็คไฟล์ซ้ำ ถ้าซ้ำให้เติม (1), (2) ... ตามสไตล์ Windows
        """
        name_stem = Path(filename).stem
        suffix = Path(filename).suffix
        
        counter = 1
        final_path = directory / filename
        
        while final_path.exists():
            new_name = f"{name_stem} ({counter}){suffix}"
            final_path = directory / new_name
            counter += 1
            
        return final_path

    @staticmethod
    def _validate_spec(spec: OutputSpec) -> None:
        if not spec.report_type or not spec.report_type.strip():
            raise ValueError("report_type must be a non-empty string")

        if not (1 <= spec.month <= 12):
            raise ValueError(f"month must be 1..12 (got {spec.month})")

        if spec.year < 1900 or spec.year > 3000:
            raise ValueError(f"year looks invalid (got {spec.year})")

        if spec.mode not in ("prod", "dev"):
            raise ValueError(f"mode must be 'prod' or 'dev' (got {spec.mode})")