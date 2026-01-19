import logging
from pathlib import Path

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
from .tasks import (
    update_footer,
    update_cover,
    update_rain_forecast_part1, 
    update_rain_forecast_part2, 
    update_risk_forecast, 
    )

logger = logging.getLogger(__name__)

def generate_flood_report(
    year: int,
    month: int,
    output_path: Path | str,
    config_path: str = "config.yaml",
):
    """
    Entry point for Flood Report generation.
    (Currently supports PAGE 3 only)
    """
    logger.info("Start flood report generation: year=%s month=%s output=%s", year, month, output_path)

    # Load config and template
    loader = DataLoader(config_path)
    config = loader.get_config()
    template_path = config["flood_report"]["template_path"]
    
    logger.debug("Using config file: %s", config_path)
    logger.debug("Flood template path: %s", template_path)

    # Init PPT Engine
    engine = PptEngine(template_path)
    logger.info("PowerPoint template loaded")

    # Edit PPT
    logger.info("Updating footer")
    update_footer(engine, config, year, month)

    logger.info("Updating cover page")
    update_cover(engine, config, year, month)

    logger.info("Updating rain forecast (lead0–lead2)")
    update_rain_forecast_part1(engine=engine, config=config, year=year, month=month)

    logger.info("Updating rain forecast (lead3–lead5)")
    update_rain_forecast_part2(engine, config, year, month)

    logger.info("Updating flood risk forecast (lead0–lead5)")
    update_risk_forecast(engine, config, year, month)


    # Save output
    logger.info("Saving flood report to: %s", output_path)
    engine.save(output_path)
    logger.info("Flood report generation completed successfully")
    
