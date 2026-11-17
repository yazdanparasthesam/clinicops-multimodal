import datetime

def compute_deadline(created_at: datetime.datetime, hours: int = 72) -> datetime.datetime:
    return created_at + datetime.timedelta(hours=hours)

def add_months(dt: datetime.datetime, months: int) -> datetime.datetime:
    # Month-end clamping 
    import calendar
    year = dt.year + (dt.month -1 + months)//12
    month = (dt.month -1 + months) %12 +1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def is_overdue(deadline: datetime.datetime) -> bool:
    if not deadline:
        return False
    return datetime.datetime.utcnow() > deadline
