from pathlib import Path

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
from ...core.image_handler import ImageHandler
from ...core.text_handler import get_months_for_leads


def update_rain_forecast_part1(engine: PptEngine, config: dict, year: int, month: int):
    """
    Flood – Rain Forecast Lead0–Lead2
    - Update title
    - Update month labels
    - Replace 3 forecast images
    """
    page_cfg = config["flood_report"]["pages"]["rain_forecast_part1"]
    data_sources = config["flood_report"]["data_sources"]
    slide = engine.find_slide_by_key(page_cfg["slide_key"])

    loader = DataLoader()
    img_handler = ImageHandler()

    leads = [0, 1, 2]
    months = get_months_for_leads(year, month, leads)

    title_text = (
        f"คาดการณ์ฝนเดือน{months[0]['thai_name']}"
        f"-{months[2]['thai_name']} "
        f"{months[0]['buddhist_year']} จาก ONEMAP"
    )
    engine.set_text(slide, page_cfg["title_shape"], title_text)

    for lead, month_info in zip(leads, months):
        # Label
        lbl_shape = page_cfg["labels"][f"lead{lead}"]
        engine.set_text(slide, lbl_shape, month_info["thai_name"])

        # Image
        url = loader.get_url(
            data_sources,
            "rain_pattern",
            yyyymm=f"{year}{month:02d}",
            lead=lead,
        )
        image_stream = img_handler.get_image(url, placeholder_text=f"Lead{lead}")
        img_shape = page_cfg["images"][f"lead{lead}"]
        engine.replace_image(slide, img_shape, image_stream)


def update_rain_forecast_part2(engine: PptEngine, config: dict, year: int, month: int):
    """
    Flood – Rain Forecast Lead3–Lead5
    - Update title
    - Update month labels
    - Replace 3 forecast images
    """
    page_cfg = config["flood_report"]["pages"]["rain_forecast_part2"]
    data_sources = config["flood_report"]["data_sources"]
    slide = engine.find_slide_by_key(page_cfg["slide_key"])

    loader = DataLoader()
    img_handler = ImageHandler()

    leads = [3, 4, 5]
    months = get_months_for_leads(year, month, leads)

    title_text = (
        f"คาดการณ์ฝนเดือน{months[0]['thai_name']}"
        f"-{months[2]['thai_name']} "
        f"{months[0]['buddhist_year']} จาก ONEMAP"
    )
    engine.set_text(slide, page_cfg["title_shape"], title_text)

    for lead, month_info in zip(leads, months):
        lbl_shape = page_cfg["labels"][f"lead{lead}"]
        engine.set_text(slide, lbl_shape, month_info["thai_name"])

        url = loader.get_url(
            data_sources,
            "rain_pattern",
            yyyymm=f"{year}{month:02d}",
            lead=lead,
        )
        image_stream = img_handler.get_image(url, placeholder_text=f"Lead{lead}")

        img_shape = page_cfg["images"][f"lead{lead}"]
        engine.replace_image(slide, img_shape, image_stream)

