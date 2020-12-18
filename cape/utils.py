from datetime import datetime


def is_date(string: str) -> datetime:
    acceptable_fmts = (
        "%Y",
        "%Y-%m-%d",
        "%b %d, %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%B %d %Y",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%b %Y",
        "%B%Y",
        "%b %d,%Y",
    )

    date = None
    for fmt in acceptable_fmts:
        try:
            date = datetime.strptime(string, fmt)
            break
        except ValueError:
            pass

    return date
