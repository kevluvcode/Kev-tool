from datetime import datetime, date
import calendar


def _parse_date(text: str) -> date:
    text = text.strip()
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Cannot parse date: {text}. Use YYYY-MM-DD, DD/MM/YYYY, etc.")


def _calculate_age(birth: date, reference: date = None) -> dict:
    if reference is None:
        reference = date.today()
    
    years = reference.year - birth.year
    months = reference.month - birth.month
    days = reference.day - birth.day
    
    if days < 0:
        months -= 1
        prev_month = reference.month - 1 if reference.month > 1 else 12
        prev_year = reference.year if reference.month > 1 else reference.year - 1
        days_in_prev = calendar.monthrange(prev_year, prev_month)[1]
        days += days_in_prev
    
    if months < 0:
        years -= 1
        months += 12
    
    total_days = (reference - birth).days
    total_months = years * 12 + months
    total_weeks = total_days // 7
    total_hours = total_days * 24
    total_minutes = total_hours * 60
    total_seconds = total_minutes * 60
    
    next_birthday = date(reference.year, birth.month, birth.day)
    if next_birthday <= reference:
        next_birthday = date(reference.year + 1, birth.month, birth.day)
    days_until = (next_birthday - reference).days
    
    return {
        'years': years,
        'months': months,
        'days': days,
        'total_days': total_days,
        'total_months': total_months,
        'total_weeks': total_weeks,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'total_seconds': total_seconds,
        'next_birthday': next_birthday,
        'days_until_birthday': days_until,
        'birth_day_of_week': birth.strftime("%A"),
        'reference_day_of_week': reference.strftime("%A"),
    }


def run(kevbin):
    kevbin.box_title("Age Calculator")
    kevbin.box_print("Calculate age from date of birth in years, months, days, and more")
    
    while True:
        kevbin.box_print("")
        dob_input = kevbin.box_input("Date of birth (YYYY-MM-DD, DD/MM/YYYY, etc.) or 'q' to quit: ").strip()
        if dob_input.lower() in ('q', 'quit', 'exit'):
            break
        if not dob_input:
            continue
        
        try:
            birth = _parse_date(dob_input)
        except ValueError as e:
            kevbin.box_print(f"[red]{e}[/red]")
            continue
        
        ref_input = kevbin.box_input("Reference date (empty for today): ").strip()
        try:
            reference = _parse_date(ref_input) if ref_input else date.today()
        except ValueError as e:
            kevbin.box_print(f"[red]{e}[/red]")
            continue
        
        age = _calculate_age(birth, reference)
        
        rows = [
            ["Component", "Value"],
            ["Years", str(age['years'])],
            ["Months", str(age['months'])],
            ["Days", str(age['days'])],
            ["", ""],
            ["Total Days", f"{age['total_days']:,}"],
            ["Total Weeks", f"{age['total_weeks']:,} weeks {age['total_days'] % 7} days"],
            ["Total Months", f"{age['total_months']:,}"],
            ["Total Hours", f"{age['total_hours']:,}"],
            ["Total Minutes", f"{age['total_minutes']:,}"],
            ["Total Seconds", f"{age['total_seconds']:,}"],
            ["", ""],
            ["Birth Day", age['birth_day_of_week']],
            ["Reference Day", age['reference_day_of_week']],
            ["Next Birthday", age['next_birthday'].strftime("%Y-%m-%d (%A)")],
            ["Days Until Birthday", str(age['days_until_birthday'])],
        ]
        
        title = f"Age as of {reference.strftime('%Y-%m-%d')}"
        if reference != date.today():
            title += f" (from {birth})"
        kevbin.box_table(rows, title=title)
        
        if age['years'] >= 100:
            kevbin.box_print(f"\n[green]🎉 Centenarian! {age['years']} years young![/green]")
        elif age['years'] >= 18:
            kevbin.box_print(f"\n[green]Adult ({age['years']} years)[/green]")
        elif age['years'] >= 13:
            kevbin.box_print(f"\n[blue]Teenager ({age['years']} years)[/blue]")
        else:
            kevbin.box_print(f"\n[yellow]Child ({age['years']} years)[/yellow]")


if __name__ == "__main__":
    class MockKevbin:
        def box_title(self, t): print(f"\n=== {t} ===")
        def box_print(self, t): print(t)
        def box_input(self, t): return input(t + " ")
        def box_table(self, rows, title=""):
            if title: print(f"\n{title}")
            for row in rows:
                print(" | ".join(str(c) for c in row))
        def box_code(self, code, language=""): print(code)
    
    run(MockKevbin())