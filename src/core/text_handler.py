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
