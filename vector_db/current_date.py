from datetime import datetime
weekday_map = {
    0 : "Thứ Hai",
    1 : "Thứ Ba",
    2 : "Thứ Bốn",
    3 : "Thứ Năm",
    4 : "Thứ Sáu",
    5 : "Thứ Bảy",
    6 : "Chủ Nhật",
}
def extract_current_date():
    now = datetime.now()
    weekday = now.weekday()
    weekday = weekday_map.get(weekday)
    current_date = weekday + ", " + now.strftime("%d/%m/%Y")
    return current_date