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

def get_next_3_months(start_year: int, start_month: int):
    """
    (NEW) คำนวณเดือนล่วงหน้า 3 เดือน (สำหรับ Forecast)
    return: list ของ dict {year, month, thai_name, buddhist_year}
    """
    results = []
    # Loop 3 รอบ (เดือนปัจจุบัน + อีก 2 เดือนถัดไป)
    for i in range(3):
        # คำนวณเดือน (ถ้าเกิน 12 ให้วนกลับไป 1)
        future_month_idx = (start_month + i - 1) % 12 + 1
        
        # คำนวณปี (ถ้าเดือนวนข้ามปี ต้องบวกปีเพิ่ม)
        # สูตร: ถ้า (start_month + i - 1) >= 12 แปลว่าข้ามปี
        year_offset = (start_month + i - 1) // 12
        future_year = start_year + year_offset
        
        results.append({
            'year': future_year,
            'month': future_month_idx,
            'thai_name': get_thai_month(future_month_idx),
            'buddhist_year': get_buddhist_year(future_year)
        })
    return results