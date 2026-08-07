import re
import pandas as pd


# WhatsApp exports the same chat in several different date/time formats
# depending on the phone's OS, region and date settings. Instead of hard
# coding one pattern, we try each known pattern (with both 2-digit and
# 4-digit year variants) against the raw text and use whichever one
# actually produces the most successfully-parsed dates.
DATE_PATTERNS = [
    # Android, 12-hour, no seconds -> "8/8/25, 5:37 pm - "
    (r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)\s-\s",
     ["%d/%m/%y, %I:%M %p - ", "%d/%m/%Y, %I:%M %p - "]),
    # Android, 24-hour, no seconds -> "8/8/2025, 17:37 - "
    (r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s",
     ["%d/%m/%y, %H:%M - ", "%d/%m/%Y, %H:%M - "]),
    # iOS, 12-hour, with seconds, square brackets -> "[8/8/25, 5:37:12 PM] "
    (r"\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s?(?:am|pm|AM|PM)\]\s",
     ["[%d/%m/%y, %I:%M:%S %p] ", "[%d/%m/%Y, %I:%M:%S %p] "]),
    # iOS, 24-hour, with seconds, square brackets -> "[8/8/2025, 17:37:12] "
    (r"\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]\s",
     ["[%d/%m/%y, %H:%M:%S] ", "[%d/%m/%Y, %H:%M:%S] "]),
]


def _detect_pattern(data: str):
    """
    Try every known (regex, format) combination and return the one that
    successfully parses the most messages into real dates. Returns
    (pattern, fmt, parsed_date_count) or None if nothing matches.
    """
    best = None
    best_count = 0
    for pattern, fmts in DATE_PATTERNS:
        raw_dates = re.findall(pattern, data)
        if not raw_dates:
            continue
        raw_dates = pd.Series(raw_dates).str.replace(
            "am", "AM", regex=False
        ).str.replace("pm", "PM", regex=False)
        for fmt in fmts:
            parsed = pd.to_datetime(raw_dates, format=fmt, errors="coerce")
            count = parsed.notna().sum()
            if count > best_count:
                best_count = count
                best = (pattern, fmt)
    return best, best_count


def preprocess(data: str) -> pd.DataFrame:
    """
    Parse a raw exported WhatsApp .txt chat into a tidy DataFrame with one
    row per message and rich date/time-derived columns for analysis.
    Raises ValueError if the text doesn't look like a WhatsApp export.
    """

    # WhatsApp sometimes uses a narrow no-break space between time and am/pm.
    data = data.replace("\u202f", " ").replace("\u200e", "")

    match, matched_count = _detect_pattern(data)
    if match is None or matched_count == 0:
        raise ValueError(
            "This doesn't look like a WhatsApp chat export. Make sure you "
            "exported the chat as a .txt file (Chat > More > Export chat > "
            "Without media) and pasted/uploaded it as-is."
        )

    pattern, fmt = match

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    if len(messages) != len(dates) or len(messages) == 0:
        raise ValueError("Couldn't parse any messages from this file.")

    df = pd.DataFrame({"message_date": dates, "user_message": messages})

    # normalize am/pm casing so strptime is happy, and coerce bad rows to NaT
    # instead of blowing up the whole parse.
    df["message_date"] = (
        df["message_date"]
        .str.replace("am", "AM", regex=False)
        .str.replace("pm", "PM", regex=False)
    )
    df["date"] = pd.to_datetime(df["message_date"], format=fmt, errors="coerce")
    df = df.dropna(subset=["date"]).reset_index(drop=True)
    df = df[["user_message", "date"]]

    users, messages_clean = [], []
    for message in df["user_message"]:
        entry = re.split(r"([\w\W]+?):\s", message, maxsplit=1)
        if entry[1:]:
            users.append(entry[1])
            messages_clean.append(entry[2])
        else:
            users.append("group_notification")
            messages_clean.append(entry[0])

    df["user"] = users
    df["message"] = [m.strip("\n") for m in messages_clean]
    df.drop(columns=["user_message"], inplace=True)

    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    def _period(hour):
        start = f"{hour:02d}"
        end = "00" if hour == 23 else f"{hour + 1:02d}"
        return f"{start}-{end}"

    df["period"] = df["hour"].apply(_period)

    # a few derived helper columns used across the app
    df["is_media"] = df["message"].str.contains(
        r"<Media omitted>|image omitted|video omitted|audio omitted|sticker omitted|GIF omitted|document omitted",
        case=False, regex=True, na=False,
    )
    df["is_deleted"] = df["message"].str.contains(
        "This message was deleted|You deleted this message", case=False, na=False
    )
    df["word_count"] = df["message"].apply(lambda m: len(m.split()))

    return df
