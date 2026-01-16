from pathlib import Path

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
from ...core.image_handler import ImageHandler
from ...core.text_handler import get_next_3_months


def update_page3_rain_forecast(
    engine: PptEngine,
    config: dict,
    year: int,
    month: int,
):
    """
    PAGE 3: Flood – Rain Forecast M1–M3
    - Update title
    - Update month labels
    - Replace 3 forecast images
    """

    # Config shortcuts
    page_cfg = config["flood_report"]["pages"]["rain_forecast_part1"]
    data_sources = config["flood_report"]["data_sources"]

    slide_key = page_cfg["slide_key"]


    # Init helpers
    loader = DataLoader()
    img_handler = ImageHandler()

    # Find slide
    slide = engine.find_slide_by_key(slide_key)

    # Month calculation (M1–M3)
    months = get_next_3_months(year, month)

    # Update title
    title_text = (
        f"คาดการณ์ฝนเดือน{months[0]['thai_name']}"
        f"-{months[2]['thai_name']} "
        f"{months[0]['buddhist_year']} จาก ONEMAP"
    )

    engine.set_text(slide, page_cfg["title_shape"], title_text)

    # Update each month (M1–M3)
    for idx, month_info in enumerate(months, start=1):
        # --- Label ---
        lbl_shape = page_cfg["labels"][f"m{idx}"]
        engine.set_text(slide, lbl_shape, month_info["thai_name"])

        # --- Image ---
        url = loader.get_url(
            data_sources,
            "rain_pattern",
            yyyymm=f"{year}{month:02d}",
            lead=idx
        )

        image_stream = img_handler.get_image(
            url,
            placeholder_text=f"M{idx}"
        )

        img_shape = page_cfg["images"][f"m{idx}"]
        engine.replace_image(slide, img_shape, image_stream)
