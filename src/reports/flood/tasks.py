import logging
from pathlib import Path

from ...core.ppt_engine import PptEngine
from ...core.data_loader import DataLoader
from ...core.image_handler import ImageHandler
from ...core.text_handler import get_months_for_leads, format_month_range
    
logger = logging.getLogger(__name__)

def update_footer(engine: PptEngine, config: dict, year: int, month: int) -> None:
    months = get_months_for_leads(year, month, [0, 1, 2, 3, 4, 5])
    month_range = format_month_range(months)

    footer_text = f" | การวิเคราะห์เพื่อกำหนดพื้นที่เสี่ยงอุทกภัยเดือน{month_range}"
    updated = engine.set_text_on_layouts("Txt_Footer", footer_text, preserve_format=True)

    
def update_cover(engine: PptEngine, config: dict, year: int, month: int):
    page_cfg = config["flood_report"]["pages"]["cover"]
    slide = engine.find_slide_by_key(page_cfg["slide_key"])

    # Report period = 6 months (lead0..lead5)
    months_6 = get_months_for_leads(year, month, [0, 1, 2, 3, 4, 5])
    engine.set_text(
        slide,
        page_cfg["report_period_shape"],
        format_month_range(months_6),
    )

    # Issue date = fixed day 1, use lead0 month/year
    lead0 = get_months_for_leads(year, month, [0])[0]
    issue_text = f"1 {lead0['thai_name']} {lead0['buddhist_year']}"
    engine.set_text(
        slide,
        page_cfg["issue_date_shape"],
        issue_text,
    )
    
def _format_rain_title(months: list[dict]) -> str:
    return f"คาดการณ์ฝนเดือน{format_month_range(months)} จาก ONEMAP"


def _format_risk_title(months: list[dict]) -> str:
    return f"สรุปผลการคาดการณ์พื้นที่เสี่ยงอุทกภัยเดือน{format_month_range(months)}"


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

    title_text = _format_rain_title(months)
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

    title_text = _format_rain_title(months)
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


def update_risk_forecast(engine: PptEngine, config: dict, year: int, month: int):
    """
    Flood – Risk Forecast Lead0–Lead5
    - Update title
    - Replace 6 risk map images (lead0..lead5)
    NOTE: This slide has no month label textboxes.
    """
    page_cfg = config["flood_report"]["pages"]["risk_forecast"]
    data_sources = config["flood_report"]["data_sources"]
    slide = engine.find_slide_by_key(page_cfg["slide_key"])

    loader = DataLoader()
    img_handler = ImageHandler()

    leads = list(range(6))
    months = get_months_for_leads(year, month, leads)

    # Title (optional but useful)
    start = months[0]
    end = months[-1]

    title_text = _format_risk_title(months)
    engine.set_text(slide, page_cfg["title_shape"], title_text)
    
    # Replace images lead0..lead5
    for lead in leads:
        url = loader.get_url(
            data_sources,
            "risk_pattern",
            yyyymm=f"{year}{month:02d}",
            lead=lead,
        )
        image_stream = img_handler.get_image(url, placeholder_text=f"Lead{lead}")

        img_shape = page_cfg["images"][f"lead{lead}"]
        engine.replace_image(slide, img_shape, image_stream)

