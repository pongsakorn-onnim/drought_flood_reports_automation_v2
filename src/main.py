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
    console = Console()
    
    # 1. Display Header
    console.print(Panel(
        Text("HII Report Generator", justify="center", style="bold white"),
        style="bold blue",
        subtitle="v2.0"
    ))

    # 2. Ask Report Type
    # Highlight choices [1] and [2] in cyan
    console.print("Which report would you like to generate?")
    console.print(" [[bold cyan]1[/]]: Drought Report")
    console.print(" [[bold cyan]2[/]]: Flood Report")
    
    choice = Prompt.ask(
        "Enter your choice ([bold cyan]1 or 2[/])", 
        choices=["1", "2"], 
        show_choices=False
    )
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
    # --- 1. Argument Parsing ---
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

    # --- 2. Initial Logging Setup (Console Only) ---
    # This allows us to log errors even before the file logging is configured.
    setup_logging(
        level=args.log_level,
        quiet=args.quiet,
        console_style=args.log_style
    )

    # --- 3. Determine Parameters (Interactive vs Arguments) ---
    if not args.report or not args.year or not args.month:
        if RICH_AVAILABLE:
            report_type, year, month = interactive_mode()
        else:
            # Fallback for environments without Rich
            print("Rich library not found. Using standard input.")
            report_type = input("Report (drought/flood): ").strip()
            year = int(input("Year: "))
            month = int(input("Month: "))
    else:
        report_type = args.report
        year = args.year
        month = args.month

    # --- 4. File Logging & Retention Policy ---
    if not args.log_file:
        # Generate standard log filename: logs/run_<type>_<date>_<time>.log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Cleanup old logs before creating a new one
        cleanup_old_logs(log_dir, pattern="run_*.log", keep=5)

        log_filename = f"run_{report_type}_{year}{month:02d}_{timestamp}.log"
        log_file_path = log_dir / log_filename
    else:
        log_file_path = Path(args.log_file)

    # Re-configure logging to include the File Handler
    setup_logging(
        level=args.log_level,
        log_file=log_file_path,
        quiet=args.quiet,
        console_style=args.log_style,
        file_level="DEBUG"  # Always keep detailed logs in file
    )

    # Print log location for user reference
    if RICH_AVAILABLE and not args.quiet:
        Console().print(f"\n[dim]Log file: {log_file_path}[/dim]\n")

    # --- 5. Report Generation Execution ---
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
    
    try:
        generator = REPORT_GENERATORS[report_type]
        generator(
            year=year,
            month=month,
            output_path=output_path,
        )

        # --- 6. Post-Processing: Open Output Folder ---
        logger.info("Opening output folder...")
        if os.name == 'nt':  # Windows only
            # Open folder and highlight the generated file
            subprocess.Popen(f'explorer /select,"{output_path}"')
        else:
            # Fallback for macOS/Linux (open folder only)
            subprocess.Popen(['open' if os.name == 'posix' else 'xdg-open', str(output_path.parent)])

    except Exception as e:
        logger.critical(f"Report generation failed: {e}", exc_info=True)
        # In interactive mode, pause so user can see the error
        if not args.quiet and RICH_AVAILABLE:
            input("\nPress Enter to exit...")
        exit(1)

if __name__ == "__main__":
    main()