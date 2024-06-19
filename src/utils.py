from datetime import datetime, timedelta


def generate_month_intervals(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    intervals = []

    while current <= end:
        month_start = current.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        if month_end > end:
            month_end = end
        if month_start < start:
            month_start = start
        intervals.append(
            (month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
        )
        current = next_month

    return intervals

