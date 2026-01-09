import calendar
import datetime

def get_month_calendar(year: int, month: int, events: list):
    """
    Returns a list of weeks. Each week is a list of days.
    Each day is a dict: {date: datetime.date, day: int, is_current_month: bool, events: []}
    """
    cal = calendar.Calendar(firstweekday=0) # Monday
    month_days = cal.monthdatescalendar(year, month)
    
    calendar_data = []
    
    for week in month_days:
        week_data = []
        for day in week:
            day_events = [e for e in events if e.date.date() == day]
            week_data.append({
                "date": day,
                "day": day.day,
                "is_current_month": day.month == month,
                "events": day_events
            })
        calendar_data.append(week_data)
        
    return calendar_data


def get_multi_month_calendar(year: int, start_month: int, month_count: int, events: list):
    """
    Returns calendar data for multiple consecutive months.
    month_count: 1 (default), 3 (Quartal), or 6 (Halbjahr)
    
    Returns list of month objects:
    [{"name": "January 2026", "year": 2026, "month": 1, "weeks": [...]}]
    """
    months_data = []
    
    for i in range(month_count):
        m = start_month + i
        y = year
        # Handle month overflow into next year
        while m > 12:
            m -= 12
            y += 1
        
        month_calendar = get_month_calendar(y, m, events)
        month_name = datetime.date(y, m, 1).strftime("%B %Y")
        
        months_data.append({
            "name": month_name,
            "year": y,
            "month": m,
            "weeks": month_calendar
        })
    
    return months_data
