# src/core/output_manager.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional


Mode = Literal["prod", "dev"]


@dataclass(frozen=True)
class OutputSpec:
    report_type: str               # "flood" | "drought" (ไม่บังคับตายตัว แต่ควรใช้ตามนี้)
    year: int
    month: int
    mode: Mode = "prod"


class OutputManager:
    """
    Output policy (Design #2):
      - prod  -> output/<report_type>/
      - dev   -> output/<report_type>/_dev/
    Filename:
      {report_type}_report_{yyyymm}_run{yyyymmdd_HHMM}.pptx

    Responsibilities:
      - create folders
      - build output path
      - guarantee no overwrite by using timestamp
    """

    def __init__(self, base_output_dir: str | Path = "output"):
        self.base_dir = Path(base_output_dir)

    def build_output_path(
        self,
        spec: OutputSpec,
        now: Optional[datetime] = None,
    ) -> Path:
        """
        Returns the full output filepath and ensures the parent directory exists.

        Parameters
        ----------
        spec : OutputSpec
            report_type/year/month/mode
        now : datetime | None
            Optional injection for deterministic tests. Defaults to datetime.now().
        """
        self._validate_spec(spec)

        now = now or datetime.now()
        yyyymm = f"{spec.year}{spec.month:02d}"
        run_ts = now.strftime("%Y%m%d_%H%M")

        out_dir = self.base_dir / spec.report_type
        if spec.mode == "dev":
            out_dir = out_dir / "_dev"

        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{spec.report_type}_report_{yyyymm}_run{run_ts}.pptx"
        return out_dir / filename

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
