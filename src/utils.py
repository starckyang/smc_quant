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


def generate_10_day_intervals(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    intervals = []

    while current <= end:
        period_end = current + timedelta(days=9)

        # Adjust period_end to include the 31st in the current interval
        if period_end.day == 31 or period_end.month != (current + timedelta(days=9)).month:
            period_end = (current.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        if period_end > end:
            period_end = end

        intervals.append(
            (current.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d"))
        )

        current = period_end + timedelta(days=1)

    return intervals


