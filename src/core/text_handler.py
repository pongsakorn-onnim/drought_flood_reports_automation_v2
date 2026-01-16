import datetime

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def get_thai_month(month_idx: int) -> str:
    """คืนค่าชื่อเดือนไทยเต็ม (1-12)"""
    if 1 <= month_idx <= 12:
        return THAI_MONTHS[month_idx - 1]
    return ""

def get_buddhist_year(year: int) -> int:
    """แปลง ค.ศ. เป็น พ.ศ."""
    return year + 543

def get_next_months(start_year: int, start_month: int, n: int):
    if n <= 0:
        return []

    results = []
    for i in range(n):
        future_month_idx = (start_month + i - 1) % 12 + 1
        year_offset = (start_month + i - 1) // 12
        future_year = start_year + year_offset

        results.append({
            "year": future_year,
            "month": future_month_idx,
            "thai_name": get_thai_month(future_month_idx),
            "buddhist_year": get_buddhist_year(future_year),
        })
    return results


def get_months_for_leads(start_year: int, start_month: int, leads: list[int]):
    if not leads:
        return []

    max_lead = max(leads)
    all_months = get_next_months(start_year, start_month, max_lead + 1)
    return [all_months[l] for l in leads]


def format_month_range(months: list[dict]) -> str:
    """
    Standard month-range style for ALL slides:
    uses en dash with spaces: ' – '

    Same-year example: "มกราคม – มิถุนายน 2569"
    Cross-year example: "ธันวาคม 2568 – มิถุนายน 2569"
    """
    if not months:
        return ""

    start = months[0]
    end = months[-1]
    sep = " – "

    # Use buddhist_year for comparison because that's what we render
    if start["buddhist_year"] == end["buddhist_year"]:
        return f"{start['thai_name']}{sep}{end['thai_name']} {start['buddhist_year']}"

    return (
        f"{start['thai_name']} {start['buddhist_year']}"
        f"{sep}"
        f"{end['thai_name']} {end['buddhist_year']}"
    )

