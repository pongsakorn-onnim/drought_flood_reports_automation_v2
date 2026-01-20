# src/main.py
"""
Main Entry Point for HII Drought/Flood Report Generator.

This script orchestrates the entire reporting process, including:
1. Argument parsing (CLI support).
2. Interactive mode (Rich UI) when no arguments are provided.
3. Logging configuration and rotation (cleanup).
4. Dispatching tasks to specific report managers (Drought/Flood).
5. Post-processing actions (opening output folders).
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# --- Third-party Imports ---
try:
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# --- Project Imports ---
from .reports.drought.manager import generate_drought_report
from .reports.flood.manager import generate_flood_report
from .core.output_manager import OutputManager, OutputSpec
from .core.logging_config import setup_logging

# Setup module-level logger
logger = logging.getLogger(__name__)


def cleanup_old_logs(log_dir: Path, pattern: str = "run_*.log", keep: int = 5) -> None:
    """
    Retention Policy: Keeps only the N most recent log files.
    
    Args:
        log_dir (Path): Directory containing log files.
        pattern (str): Glob pattern to match log files (e.g., 'run_*.log').
        keep (int): Number of recent files to keep.
    """
    if not log_dir.exists():
        return

    # Find all files matching the pattern
    files = list(log_dir.glob(pattern))
    
    if len(files) <= keep:
        return

    # Sort files by modification time (descending: newest first)
    files.sort(key=os.path.getmtime, reverse=True)

    # Identify files to delete (skip the first 'keep' files)
    files_to_delete = files[keep:]

    for f in files_to_delete:
        try:
            os.remove(f)
        except OSError:
            # Ignore errors (e.g., file in use)
            pass


def interactive_mode() -> tuple[str, int, int]:
    """
    Launches an interactive CLI session using 'Rich'.
    Returns the user's selected report type, year, and month.
    """
    
    # ล้างปุ่มที่ User อาจเผลอกดค้างไว้ตอนรอรายงานเสร็จ
    if os.name == 'nt': 
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()   
    
    console = Console()
    
    # 1. Display Header
    console.print(Panel(
        Text("HII Report Generator", justify="center", style="bold white"),
        style="bold blue",
        subtitle="v2.0"
    ))

# Display menu options
    console.print("\nSelect an option:")
    console.print(" [bold cyan]1[/]: Drought Report")
    console.print(" [bold cyan]2[/]: Flood Report")
    console.print(" [bold red]0[/]: Exit Program")
    
    # Prompt for user choice (Removed default value for UX clarity)
    choice = Prompt.ask(
        "Enter choice", 
        choices=["1", "2", "0"], 
        show_choices=False
    )

    if choice == "0":
        return None, None, None 

    report_type = "drought" if choice == "1" else "flood"

    # 3. Ask Year
    # Provide visual hint for current year
    current_year = datetime.now().year
    year = IntPrompt.ask(
        f"Enter year (e.g. [bold cyan]{current_year}[/]) [dim](default: current)[/]", 
        default=current_year, 
        show_default=False
    )

    # 4. Ask Month
    current_month = datetime.now().month
    month = IntPrompt.ask(
        f"Enter month ([bold cyan]1-12[/]) [dim](default: current)[/]", 
        default=current_month, 
        show_default=False
    )
    
    return report_type, year, month


def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="HII Drought/Flood Report Generator")
    parser.add_argument("--report", choices=["drought", "flood"], help="Report type to generate.")
    parser.add_argument("--year", type=int, help="Target year (e.g., 2026).")
    parser.add_argument("--month", type=int, help="Target month (1-12).")
    parser.add_argument("--dev", action="store_true", help="Enable development mode output.")
    
    # Logging arguments
    parser.add_argument("--log-level", default="INFO", help="Set logging verbosity.")
    parser.add_argument("--log-file", default=None, help="Custom path for the log file.")
    parser.add_argument("--log-style", choices=["dev", "user"], default="user", help="Console output style.")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output.")

    args = parser.parse_args()

    # Check for automation mode (CLI arguments provided)
    is_cli_automation = (args.report and args.year and args.month)
    
    # Initial logging setup (Console only)
    setup_logging(
        level=args.log_level,
        quiet=args.quiet,
        console_style=args.log_style
    )
    
    exit_reason = "NORMAL" 

    # --- Main Application Loop ---
    while True:
        try:
            # --- Determine Parameters ---
            if is_cli_automation:
                report_type = args.report
                year = args.year
                month = args.month
            else:
                # Interactive Mode
                if RICH_AVAILABLE:
                    report_type, year, month = interactive_mode()
                    
                    # Exit condition
                    if report_type is None:
                        exit_reason = "USER_EXIT"
                        break
                else:
                    # Standard input fallback
                    print("Rich library not found. Using standard input.")
                    report_type = input("Report (drought/flood): ").strip()
                    year = int(input("Year: "))
                    month = int(input("Month: "))

            # --- Reset Logging Handlers ---
            # Remove existing handlers to prevent duplication across iterations
            root_logger = logging.getLogger()
            if root_logger.handlers:
                for h in root_logger.handlers[:]:
                    root_logger.removeHandler(h)

            # Generate log filename based on current report task
            if not args.log_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_dir = Path("logs")
                log_dir.mkdir(exist_ok=True)
                cleanup_old_logs(log_dir, pattern="run_*.log", keep=5)

                log_filename = f"run_{report_type}_{year}{month:02d}_{timestamp}.log"
                log_file_path = log_dir / log_filename
            else:
                log_file_path = Path(args.log_file)

            # Re-configure logging with file handler
            setup_logging(
                level=args.log_level,
                log_file=log_file_path,
                quiet=args.quiet,
                console_style=args.log_style,
                file_level="DEBUG"
            )

            if RICH_AVAILABLE and not args.quiet:
                Console().print(f"\n[dim]Log file: {log_file_path}[/dim]\n")

            # --- Execute Report Generation ---
            out_mgr = OutputManager(base_output_dir="output")
            spec = OutputSpec(
                report_type=report_type,
                year=year,
                month=month,
                mode="dev" if args.dev else "prod",
            )
            output_path = out_mgr.build_output_path(spec)

            REPORT_GENERATORS = {
                "flood": generate_flood_report,
                "drought": generate_drought_report,
            }
            
            generator = REPORT_GENERATORS[report_type]
            generator(
                year=year,
                month=month,
                output_path=output_path,
            )

            # --- Post-Processing ---
            logger.info("Opening output folder...")
            if os.name == 'nt':
                subprocess.Popen(f'explorer /select,"{output_path}"')
            else:
                subprocess.Popen(['open' if os.name == 'posix' else 'xdg-open', str(output_path.parent)])

        except Exception as e:
            logger.critical(f"Report generation failed: {e}", exc_info=True)
            
            # Pause on error in interactive mode
            if not args.quiet and RICH_AVAILABLE:
                input("\nAn error occurred. Press Enter to return to menu...")
            
            # Exit immediately in automation mode
            if is_cli_automation:
                exit(1)

        # Break loop if running in automation mode
        if is_cli_automation:
            break
        
    return exit_reason


if __name__ == "__main__":
    exit_reason = main()
    raise SystemExit(0)