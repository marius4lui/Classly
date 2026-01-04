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
