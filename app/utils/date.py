from datetime import datetime

def calculate_days(start_date: str, end_date: str) -> int:
    try:
        start = datetime.strptime(start_date.strip().strip(","), "%Y-%m-%d")
        end = datetime.strptime(end_date.strip().strip(","), "%Y-%m-%d")
        return (end - start).days + 1
    except Exception as e:
        print(f"❌ 日期解析錯誤：{start_date} ~ {end_date}, 錯誤：{e}")
        return 0
