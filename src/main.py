# src/main.py
from pathlib import Path
import argparse
import logging

from .reports.drought.manager import generate_drought_report
from .reports.flood.manager import generate_flood_report
from .core.output_manager import OutputManager, OutputSpec
from .core.logging_config import setup_logging

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="HII Drought/Flood Report Generator"
    )
    
    parser.add_argument(
        "--report",
        choices=["drought", "flood"],
        required=True,
        help="Which report to generate",
    )
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Write output to output/<type>/_dev/ (default writes to output/<type>/)"
    )

    # --- Logging options ---
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional path to write logs (e.g. logs/run.log)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable console logs (useful when only writing to --log-file)"
    )

    args = parser.parse_args()

    setup_logging(
        level=args.log_level,
        log_file=Path(args.log_file) if args.log_file else None,
        quiet=args.quiet,
    )

    report_type = args.report
    
    logger.info("Starting report generator")
    logger.info("Args: report=%s year=%s month=%s dev=%s", report_type, args.year, args.month, args.dev)

    out_mgr = OutputManager(base_output_dir="output")
    spec = OutputSpec(
        report_type=args.report,
        year=args.year,
        month=args.month,
        mode="dev" if args.dev else "prod",
    )
    output_path = out_mgr.build_output_path(spec)

    logger.info("Output path: %s", output_path)
    
    REPORT_GENERATORS = {
        "flood": generate_flood_report,
        "drought": generate_drought_report,
    }
    
    generator = REPORT_GENERATORS[report_type]
    
    logger.info("Generating %s report", report_type)

    generator(
        year=args.year,
        month=args.month,
        output_path=output_path,
    )

if __name__ == "__main__":
    main()
