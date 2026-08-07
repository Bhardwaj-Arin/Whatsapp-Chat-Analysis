from pathlib import Path
from collections import Counter

import pandas as pd
import emoji
from urlextract import URLExtract
from wordcloud import WordCloud

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER = SentimentIntensityAnalyzer()
except Exception:  # pragma: no cover - sentiment becomes unavailable gracefully
    _VADER = None

extractor = URLExtract()

BASE_DIR = Path(__file__).resolve().parent
STOPWORDS_PATH = BASE_DIR / "datasets" / "stop_hinglish.txt"

with open(STOPWORDS_PATH, "r", encoding="utf-8") as _f:
    STOP_WORDS = set(_f.read().splitlines())


def _filter_user(selected_user, df):
    if selected_user != "Overall":
        return df[df["user"] == selected_user]
    return df


def _real_messages(df):
    """Messages from actual people (no group notifications, media, or deletions)."""
    return df[
        (df["user"] != "group_notification")
        & (~df["is_media"])
        & (~df["is_deleted"])
    ]


def fetch_stats(selected_user, df):
    df = _filter_user(selected_user, df)

    num_messages = df.shape[0]
    words = sum(df["message"].str.split().str.len().fillna(0))
    num_media_messages = int(df["is_media"].sum())

    links = []
    for message in df["message"]:
        links.extend(extractor.find_urls(message))

    return num_messages, int(words), num_media_messages, len(links)


def overview_stats(selected_user, df):
    """Extra top-line stats: active participants, date span, deleted messages."""
    filtered = _filter_user(selected_user, df)
    people = filtered[filtered["user"] != "group_notification"]

    active_days = people["only_date"].nunique()
    span_days = max((df["only_date"].max() - df["only_date"].min()).days + 1, 1)
    participants = df[df["user"] != "group_notification"]["user"].nunique()
    deleted = int(filtered["is_deleted"].sum())

    return {
        "participants": participants,
        "active_days": active_days,
        "span_days": span_days,
        "deleted_messages": deleted,
        "first_message": df["date"].min(),
        "last_message": df["date"].max(),
    }


def most_busy_user(df):
    people = df[df["user"] != "group_notification"]
    x = people["user"].value_counts().head(10)
    percent_df = (
        round(people["user"].value_counts() / people.shape[0] * 100, 2)
        .reset_index()
        .rename(columns={"user": "Name", "count": "Percent"})
    )
    return x, percent_df


def create_wordcloud(selected_user, df):
    df = _filter_user(selected_user, df)
    temp = _real_messages(df)

    def remove_stop_words(message):
        return " ".join(
            w for w in message.lower().split() if w not in STOP_WORDS
        )

    text = temp["message"].apply(remove_stop_words).str.cat(sep=" ").strip()
    if not text:
        return None

    wc = WordCloud(
        width=800, height=500, min_font_size=10,
        background_color="white", colormap="viridis",
    )
    return wc.generate(text)


def most_common_words(selected_user, df, top_n=20):
    df = _filter_user(selected_user, df)
    temp = _real_messages(df)

    words = []
    for message in temp["message"]:
        for word in message.lower().split():
            if word.strip() and word.strip() not in STOP_WORDS:
                words.append(word.strip())

    return pd.DataFrame(
        Counter(words).most_common(top_n), columns=["Common Word", "No. of Times"]
    )


def emoji_helper(selected_user, df):
    df = _filter_user(selected_user, df)

    emojis = []
    for message in df["message"]:
        emojis.extend(c for c in message if c in emoji.EMOJI_DATA)

    if not emojis:
        return pd.DataFrame(columns=["Emoji", "No. of times"])

    counts = Counter(emojis)
    return pd.DataFrame(counts.most_common(len(counts)), columns=["Emoji", "No. of times"])


def monthly_timeline(selected_user, df):
    df = _filter_user(selected_user, df)
    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()
    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    df = _filter_user(selected_user, df)
    return df.groupby("only_date").count()["message"].reset_index()


def week_activity_map(selected_user, df):
    df = _filter_user(selected_user, df)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = df["day_name"].value_counts().reindex(order).fillna(0)
    return counts


def month_activity_map(selected_user, df):
    df = _filter_user(selected_user, df)
    order = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
    counts = df["month"].value_counts().reindex(order).dropna()
    return counts


def hourly_activity(selected_user, df):
    df = _filter_user(selected_user, df)
    counts = df.groupby("hour")["message"].count().reindex(range(24), fill_value=0)
    return counts


def activity_heatmap(selected_user, df):
    df = _filter_user(selected_user, df)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    period_order = [f"{h:02d}-{(h + 1) % 24:02d}" for h in range(24)]
    pivot = df.pivot_table(index="day_name", columns="period", values="message", aggfunc="count").fillna(0)
    pivot = pivot.reindex(index=order)
    cols = [c for c in period_order if c in pivot.columns]
    pivot = pivot.reindex(columns=cols).fillna(0)
    return pivot


def message_length_by_user(df, top_n=10):
    people = df[df["user"] != "group_notification"]
    avg_len = people.groupby("user")["word_count"].mean().sort_values(ascending=False).head(top_n)
    return avg_len.round(1)


def sentiment_available():
    return _VADER is not None


def sentiment_analysis(selected_user, df):
    """
    Returns a DataFrame with a 'sentiment' column (Positive/Neutral/Negative)
    for each real message, or None if the sentiment library isn't installed.
    """
    if _VADER is None:
        return None

    df = _filter_user(selected_user, df)
    temp = _real_messages(df).copy()
    if temp.empty:
        return temp.assign(sentiment=[])

    def label(msg):
        score = _VADER.polarity_scores(str(msg))["compound"]
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        return "Neutral"

    temp["sentiment"] = temp["message"].apply(label)
    return temp


def sentiment_by_user(sentiment_df, top_n=10):
    """% positive per user, for users with a meaningful number of messages."""
    counts = sentiment_df.groupby(["user", "sentiment"]).size().unstack(fill_value=0)
    for col in ["Positive", "Neutral", "Negative"]:
        if col not in counts.columns:
            counts[col] = 0
    counts["total"] = counts[["Positive", "Neutral", "Negative"]].sum(axis=1)
    counts = counts[counts["total"] >= 5]
    counts["% Positive"] = round(counts["Positive"] / counts["total"] * 100, 1)
    return counts.sort_values("% Positive", ascending=False).head(top_n)


def response_time_stats(df, max_gap_minutes=180, top_n=10):
    """
    Median time (in minutes) each user takes to reply after someone else's
    message, ignoring gaps longer than max_gap_minutes (treated as a new
    conversation rather than a 'reply').
    """
    people = df[df["user"] != "group_notification"].sort_values("date").reset_index(drop=True)
    if people.shape[0] < 2:
        return pd.Series(dtype=float)

    gap_minutes = people["date"].diff().dt.total_seconds() / 60
    prev_user = people["user"].shift(1)
    is_reply = (people["user"] != prev_user) & (gap_minutes <= max_gap_minutes) & (gap_minutes >= 0)

    reply_gaps = pd.DataFrame({"user": people["user"], "gap": gap_minutes, "is_reply": is_reply})
    reply_gaps = reply_gaps[reply_gaps["is_reply"]]

    median_reply = reply_gaps.groupby("user")["gap"].median().sort_values()
    counts = people["user"].value_counts()
    median_reply = median_reply[median_reply.index.isin(counts[counts >= 10].index)]

    return median_reply.head(top_n).round(1)


def conversation_starters(df, top_n=10):
    """Who tends to send the first message after a long silence (new conversation)."""
    people = df[df["user"] != "group_notification"].sort_values("date").reset_index(drop=True)
    if people.shape[0] < 2:
        return pd.Series(dtype=int)

    gap_hours = people["date"].diff().dt.total_seconds() / 3600
    starter_mask = gap_hours.isna() | (gap_hours >= 3)
    starters = people.loc[starter_mask, "user"]
    return starters.value_counts().head(top_n)


def generate_insights(selected_user, df):
    """
    A short list of plain-English, auto-generated observations about the
    chat — the kind of thing a human analyst would call out first.
    """
    insights = []
    filtered = _filter_user(selected_user, df)
    people = filtered[filtered["user"] != "group_notification"]
    if people.empty:
        return insights

    # busiest day of week
    busy_day = week_activity_map(selected_user, df)
    if busy_day.sum() > 0:
        top_day = busy_day.idxmax()
        insights.append(f"**{top_day}** is the most active day, averaging the most messages.")

    # busiest hour
    hourly = hourly_activity(selected_user, df)
    if hourly.sum() > 0:
        top_hour = int(hourly.idxmax())
        insights.append(
            f"Activity peaks around **{top_hour:02d}:00–{(top_hour + 1) % 24:02d}:00**."
        )

    # dominant participant (group chats only)
    if selected_user == "Overall" and df[df["user"] != "group_notification"]["user"].nunique() > 1:
        _, pct_df = most_busy_user(df)
        if not pct_df.empty:
            top = pct_df.iloc[0]
            insights.append(
                f"**{top['Name']}** is the most active participant, sending "
                f"**{top['Percent']}%** of all messages."
            )

        starters = conversation_starters(df, top_n=1)
        if not starters.empty:
            insights.append(
                f"**{starters.index[0]}** starts conversations most often "
                f"({int(starters.iloc[0])} times, after 3+ hours of silence)."
            )

    # media / links share
    media_share = round(filtered["is_media"].mean() * 100, 1) if filtered.shape[0] else 0
    if media_share > 0:
        insights.append(f"About **{media_share}%** of messages are media (photos, videos, etc.).")

    # sentiment
    if sentiment_available():
        sdf = sentiment_analysis(selected_user, df)
        if sdf is not None and not sdf.empty:
            top_sent = sdf["sentiment"].value_counts().idxmax()
            share = round(sdf["sentiment"].value_counts(normalize=True).max() * 100, 1)
            insights.append(f"Most messages come across as **{top_sent.lower()}** ({share}%).")

    # emoji
    edf = emoji_helper(selected_user, df)
    if not edf.empty:
        insights.append(f"The most used emoji is {edf.iloc[0]['Emoji']}, used {int(edf.iloc[0]['No. of times'])} times.")

    return insights
