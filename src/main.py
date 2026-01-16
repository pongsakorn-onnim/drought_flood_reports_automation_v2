# src/main.py
from pathlib import Path
import argparse

from .reports.flood.manager import generate_flood_report
from .core.output_manager import OutputManager, OutputSpec


def main():
    parser = argparse.ArgumentParser(
        description="HII Drought/Flood Report Generator"
    )

    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Write output to output/<type>/_dev/ (default writes to output/<type>/)"
    )

    args = parser.parse_args()
    
    out_mgr = OutputManager(base_output_dir="output")
    spec = OutputSpec(
        report_type="flood",
        year=args.year,
        month=args.month,
        mode="dev" if args.dev else "prod",
    )
    output_path = out_mgr.build_output_path(spec)

    generate_flood_report(
        year=args.year,
        month=args.month,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
