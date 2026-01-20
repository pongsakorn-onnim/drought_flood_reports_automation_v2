import logging
from pathlib import Path

# --- Rich UI Imports ---
try:
    from rich.console import Console
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
# -----------------------

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
# Import tasks ให้ตรงกับที่คุณเขียนไว้ใน drought/tasks.py
from .tasks import (
    update_footer,
    update_cover,
    update_rain_forecast_part1,  # Page 3
    update_rain_forecast_part2,  # Page 4
    update_risk_forecast,        # Page 5
)

logger = logging.getLogger(__name__)

def generate_drought_report(
    year: int,
    month: int,
    output_path: Path | str,
    config_path: str = "config.yaml",
):
    """
    Entry point for Drought Report generation.
    """
    # Setup Console
    console = Console() if RICH_AVAILABLE else None

    # Header
    if console:
        console.print(Rule(f"Generating Drought Report for {year}-{month:02d}", style="bold blue"))
    
    logger.info("Start drought report generation: year=%s month=%s", year, month)
    logger.info("Output path: %s", output_path)

    # 1. Load Resources
    loader = DataLoader(config_path)
    config = loader.get_config()
    template_path = config["drought_report"]["template_path"]
    
    logger.info(f"Template: {template_path}")

    # 2. Init Engine
    engine = PptEngine(template_path)
    
    # 3. Update Footer
    if console: console.print(Rule("Updating Footer"))
    else: logger.info("--- Updating Footer ---")
    
    update_footer(engine, config, year, month)
    logger.info("Footer updated successfully.")

    # 4. Update Cover (Page 1)
    if console: console.print(Rule("Updating Page 1 (Title Page)"))
    else: logger.info("--- Updating Cover Page ---")

    update_cover(engine, config, year, month)
    logger.info("Page 1 updated successfully.")

    # 5. Drought Forecast Part 1 (Page 3)
    if console: console.print(Rule("Updating Page 3 (3-Month Forecast)"))
    else: logger.info("--- Updating Page 3 ---")

    update_rain_forecast_part1(engine=engine, config=config, year=year, month=month)
    logger.info("Page 3 updated successfully.")

    # 6. Drought Forecast Part 2 (Page 4)
    if console: console.print(Rule("Updating Page 4 (3-Month Forecast)"))
    else: logger.info("--- Updating Page 4 ---")

    update_rain_forecast_part2(engine, config, year, month)
    logger.info("Page 4 updated successfully.")

    # 7. Drought Summary (Page 5)
    if console: console.print(Rule("Updating Page 5 (6-Month Summary)"))
    else: logger.info("--- Updating Page 5 ---")

    update_risk_forecast(engine, config, year, month)
    logger.info("Page 5 updated successfully.")

    # 8. Save
    if console: console.print(Rule("Saving Final Report"))
    else: logger.info("--- Saving Final Report ---")

    engine.save(output_path)
    logger.info(f"Report saved to: {output_path}")
    
    # Footer Summary (Green)
    if console:
        console.print(Rule("Report Generation Fully Successful", style="bold green"))
    else:
        logger.info("=== Report Generation Fully Successful ===")