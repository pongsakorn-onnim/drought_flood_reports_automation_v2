from pathlib import Path

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
from .tasks import update_page3_rain_forecast


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

    # Load config
    loader = DataLoader(config_path)
    config = loader.get_config()

    template_path = config["flood_report"]["template_path"]

    # Init PPT Engine
    engine = PptEngine(template_path)

    # PAGE 3: Rain Forecast M1–M3
    update_page3_rain_forecast(
        engine=engine,
        config=config,
        year=year,
        month=month,
    )

    # Save output
    engine.save(output_path)
