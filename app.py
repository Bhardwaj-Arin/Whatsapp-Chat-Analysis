from pathlib import Path

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import preprocessor
import helper

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"

# Sample chats are auto-discovered from datasets/*.txt (anything other than
# the stopword list). This repo ships with none by default — real personal
# chats can't be committed publicly — so add your own *_group.txt / *.txt
# demo export there if you want a "Try a sample chat" option to appear.
SAMPLE_CHATS = {
    p.stem.replace("_", " ").title(): p
    for p in sorted(DATASETS_DIR.glob("*.txt"))
    if p.name != "stop_hinglish.txt"
}

PLOTLY_TEMPLATE = "plotly_white"
GREEN, DARK_GREEN, TEAL = "#25D366", "#128C7E", "#075E54"

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.6rem; max-width: 1200px; }
    div[data-testid="stMetric"] {
        background: rgba(37, 211, 102, 0.08);
        border: 1px solid rgba(37, 211, 102, 0.25);
        border-radius: 10px;
        padding: 10px 14px;
    }
    div[data-testid="stMetricValue"] { color: #128C7E; }
    h1, h2, h3 { color: #075E54; }
    .insight-box {
        background: rgba(7, 94, 84, 0.05);
        border-left: 4px solid #25D366;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 8px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(37, 211, 102, 0.06);
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================================
# SIDEBAR — data input
# ==========================================================================
st.sidebar.title("💬 WhatsApp Chat Analyzer")
st.sidebar.caption("Turn a raw chat export into statistics, trends and insights.")

input_options = ["Upload a .txt file", "Paste chat text"]
if SAMPLE_CHATS:
    input_options.append("Try a sample chat")

input_mode = st.sidebar.radio("Get your chat data in", input_options)

chat_text = None

if input_mode == "Upload a .txt file":
    uploaded_file = st.sidebar.file_uploader("Choose your exported chat (.txt)", type=["txt"])
    if uploaded_file is not None:
        chat_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

elif input_mode == "Paste chat text":
    pasted = st.sidebar.text_area(
        "Paste the exported chat text here", height=200,
        placeholder="08/08/25, 5:37 pm - Alice: Hey, how's it going?",
    )
    if st.sidebar.button("Analyze pasted text", use_container_width=True):
        if pasted.strip():
            chat_text = pasted
        else:
            st.sidebar.warning("Paste some chat text first.")

else:  # Try a sample chat (only reachable when SAMPLE_CHATS is non-empty)
    sample_choice = st.sidebar.selectbox("Pick a sample chat", list(SAMPLE_CHATS.keys()))
    st.sidebar.caption("Demo data only — see the privacy note below.")
    if st.sidebar.button("Load sample chat", use_container_width=True):
        chat_text = SAMPLE_CHATS[sample_choice].read_text(encoding="utf-8")

with st.sidebar.expander("📋 How to export your WhatsApp chat"):
    st.markdown(
        """
        1. Open the chat (individual or group) in WhatsApp.
        2. Tap **⋮ (More)** → **Export chat**.
        3. Choose **Without media**.
        4. Share/save the `.txt` file, then upload it here (or open it and
           paste its contents into the **Paste chat text** option).
        """
    )

st.sidebar.divider()
if SAMPLE_CHATS:
    st.sidebar.markdown(
        "🔒 **Privacy note** — this app processes your chat entirely in "
        "your own browser session; nothing is uploaded to a server or "
        "stored anywhere. The sample chats are demo data only, since real "
        "personal conversations can't be shared publicly — **to analyze "
        "your own chat, upload or paste it yourself using the options "
        "above.**"
    )
else:
    st.sidebar.markdown(
        "🔒 **Privacy note** — this app processes your chat entirely in "
        "your own browser session; nothing is uploaded to a server or "
        "stored anywhere. No sample chat ships with this app, since real "
        "personal conversations can't be shared publicly — **upload or "
        "paste your own chat above to try it out.**"
    )

if not helper.sentiment_available():
    st.sidebar.caption("ℹ️ Sentiment analysis needs `vaderSentiment` (see requirements.txt).")


# ==========================================================================
# LANDING STATE — no data loaded yet
# ==========================================================================
if chat_text is None and "df" not in st.session_state:
    st.title("💬 WhatsApp Chat Analyzer")
    st.markdown(
        "A statistical deep-dive into any WhatsApp conversation — group or "
        "one-on-one — built entirely from the chat export WhatsApp already "
        "gives you."
    )

    if SAMPLE_CHATS:
        st.warning(
            "🔒 **Privacy note:** this project can't ship with a real personal "
            "chat as a public demo, so the *sample chats* in the sidebar are "
            "provided instead. To analyze **your own** conversation, export it "
            "from WhatsApp and upload or paste it yourself — it's processed "
            "locally in this session and never stored."
        )
    else:
        st.warning(
            "🔒 **Privacy note:** this project doesn't ship with any real "
            "personal chat data — that can't be shared publicly. To try the "
            "app, export **your own** WhatsApp chat and upload or paste it "
            "using the sidebar; everything is processed locally in this "
            "session and never stored."
        )

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("**📊 Activity & trends**")
        st.caption("Daily/monthly timelines, busiest day/month/hour, weekly heatmap.")
    with f2:
        st.markdown("**👥 Participants**")
        st.caption("Who talks most, average message length, conversation starters, reply speed.")
    with f3:
        st.markdown("**💬 Content**")
        st.caption("Word cloud, most common words, emoji breakdown, message sentiment.")

    prompt = "upload, paste, or load a sample chat" if SAMPLE_CHATS else "upload or paste your chat"
    st.info(f"👈 Use the sidebar to {prompt} to begin.")
    st.stop()


# ==========================================================================
# PARSE
# ==========================================================================
if chat_text is not None:
    try:
        st.session_state["df"] = preprocessor.preprocess(chat_text)
    except ValueError as e:
        st.error(str(e))
        st.stop()

df = st.session_state.get("df")
if df is None or df.empty:
    st.warning("Couldn't find any messages in that chat. Try a different export.")
    st.stop()

user_list = sorted(u for u in df["user"].unique().tolist() if u != "group_notification")
user_list.insert(0, "Overall")

selected_user = st.sidebar.selectbox("Analyze messages from", user_list)
st.sidebar.caption(f"Loaded {df.shape[0]:,} lines from the chat export.")

is_group = df[df["user"] != "group_notification"]["user"].nunique() > 1


# ==========================================================================
# HEADER + KEY INSIGHTS
# ==========================================================================
st.title("💬 WhatsApp Chat Analyzer")
scope_label = "the whole chat" if selected_user == "Overall" else f"**{selected_user}**"
st.caption(f"Showing analysis for {scope_label}.")

num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
overview = helper.overview_stats(selected_user, df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Messages", f"{num_messages:,}")
c2.metric("Words", f"{words:,}")
c3.metric("Media Shared", f"{num_media_messages:,}")
c4.metric("Links Shared", f"{num_links:,}")
c5.metric("Active Days", overview["active_days"])

st.caption(
    f"Chat spans **{overview['span_days']:,} days** · "
    f"first message **{overview['first_message']:%d %b %Y}**, "
    f"last message **{overview['last_message']:%d %b %Y}** · "
    f"**{overview['deleted_messages']}** deleted messages"
)

insights = helper.generate_insights(selected_user, df)
if insights:
    st.subheader("🔎 Key Insights")
    cols = st.columns(2)
    for i, text in enumerate(insights):
        with cols[i % 2]:
            st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)

st.divider()


# ==========================================================================
# TABS
# ==========================================================================
tab_timeline, tab_activity, tab_people, tab_words, tab_emoji, tab_sentiment, tab_data = st.tabs(
    ["📈 Timeline", "🗓️ Activity Map", "👥 Participants", "🔤 Words", "😀 Emoji", "🙂 Sentiment", "🗂️ Raw Data"]
)

# ---- Timeline ----
with tab_timeline:
    st.subheader("Monthly Timeline")
    timeline = helper.monthly_timeline(selected_user, df)
    fig = px.line(timeline, x="time", y="message", markers=True, template=PLOTLY_TEMPLATE)
    fig.update_traces(line_color=DARK_GREEN)
    fig.update_layout(xaxis_title=None, yaxis_title="Messages", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Timeline")
    daily = helper.daily_timeline(selected_user, df)
    fig = px.line(daily, x="only_date", y="message", template=PLOTLY_TEMPLATE)
    fig.update_traces(line_color=GREEN)
    fig.update_layout(xaxis_title=None, yaxis_title="Messages")
    st.plotly_chart(fig, use_container_width=True)

# ---- Activity map ----
with tab_activity:
    am1, am2, am3 = st.columns(3)
    with am1:
        st.subheader("Busiest Day")
        busy_day = helper.week_activity_map(selected_user, df)
        fig = px.bar(x=busy_day.index, y=busy_day.values, template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[GREEN])
        fig.update_layout(xaxis_title=None, yaxis_title="Messages")
        st.plotly_chart(fig, use_container_width=True)
    with am2:
        st.subheader("Busiest Month")
        busy_month = helper.month_activity_map(selected_user, df)
        fig = px.bar(x=busy_month.index, y=busy_month.values, template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[DARK_GREEN])
        fig.update_layout(xaxis_title=None, yaxis_title="Messages", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with am3:
        st.subheader("Busiest Hour")
        hourly = helper.hourly_activity(selected_user, df)
        fig = px.bar(x=hourly.index, y=hourly.values, template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis_title="Hour of day", yaxis_title="Messages")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Weekly Activity Heatmap")
    st.caption("When during the week messages are typically sent (day vs. hour block).")
    heatmap = helper.activity_heatmap(selected_user, df)
    fig = go.Figure(data=go.Heatmap(z=heatmap.values, x=heatmap.columns, y=heatmap.index, colorscale="Greens"))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ---- Participants ----
with tab_people:
    if is_group and selected_user == "Overall":
        x, percent_df = helper.most_busy_user(df)
        st.subheader("Most Active Participants")
        bc1, bc2 = st.columns([2, 1])
        with bc1:
            fig = px.bar(x=x.index, y=x.values, template=PLOTLY_TEMPLATE,
                         color_discrete_sequence=["#DC2626"])
            fig.update_layout(xaxis_title=None, yaxis_title="Messages", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with bc2:
            st.dataframe(percent_df, use_container_width=True, height=380)

        st.subheader("Average Words per Message")
        avg_len = helper.message_length_by_user(df)
        fig = px.bar(x=avg_len.index, y=avg_len.values, template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[DARK_GREEN])
        fig.update_layout(xaxis_title=None, yaxis_title="Avg. words / message", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        pc1, pc2 = st.columns(2)
        with pc1:
            st.subheader("Conversation Starters")
            st.caption("Sends the first message after 3+ hours of silence.")
            starters = helper.conversation_starters(df)
            if not starters.empty:
                fig = px.bar(x=starters.index, y=starters.values, template=PLOTLY_TEMPLATE,
                             color_discrete_sequence=["#7C3AED"])
                fig.update_layout(xaxis_title=None, yaxis_title="Times", xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        with pc2:
            st.subheader("Typical Reply Speed")
            st.caption("Median minutes to reply (within 3 hrs, 10+ replies).")
            reply_times = helper.response_time_stats(df)
            if not reply_times.empty:
                fig = px.bar(x=reply_times.index, y=reply_times.values, template=PLOTLY_TEMPLATE,
                             color_discrete_sequence=["#2563EB"])
                fig.update_layout(xaxis_title=None, yaxis_title="Median minutes", xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Not enough back-and-forth messages to calculate this.")
    else:
        st.info(
            "Participant comparisons apply to group chats viewed as **Overall**. "
            "Switch the sidebar selector to 'Overall' on a group chat to see this tab."
        )

# ---- Words ----
with tab_words:
    wc1, wc2 = st.columns([1, 1])
    with wc1:
        st.subheader("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig, use_container_width=True)
        else:
            st.caption("Not enough text to build a word cloud.")
    with wc2:
        st.subheader("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig = px.bar(
                most_common_df.sort_values("No. of Times"),
                x="No. of Times", y="Common Word", orientation="h",
                template=PLOTLY_TEMPLATE, color_discrete_sequence=[GREEN],
            )
            fig.update_layout(yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No common words found.")

# ---- Emoji ----
with tab_emoji:
    emoji_df = helper.emoji_helper(selected_user, df)
    if not emoji_df.empty:
        ec1, ec2 = st.columns(2)
        with ec1:
            fig = px.pie(emoji_df.head(10), names="Emoji", values="No. of times", template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig, use_container_width=True)
        with ec2:
            st.dataframe(emoji_df, use_container_width=True, height=380)
    else:
        st.caption("No emojis found in this chat.")

# ---- Sentiment ----
with tab_sentiment:
    if helper.sentiment_available():
        st.caption(
            "Each message is scored automatically (VADER lexicon) as Positive, "
            "Neutral or Negative. Treat this as a rough signal, not a verdict — "
            "sarcasm, slang and Hinglish text can throw it off."
        )
        sentiment_df = helper.sentiment_analysis(selected_user, df)
        if sentiment_df is not None and not sentiment_df.empty:
            sc1, sc2 = st.columns([1, 1])
            with sc1:
                counts = sentiment_df["sentiment"].value_counts()
                fig = px.pie(
                    names=counts.index, values=counts.values, template=PLOTLY_TEMPLATE,
                    color=counts.index,
                    color_discrete_map={"Positive": GREEN, "Neutral": "#9CA3AF", "Negative": "#DC2626"},
                )
                st.plotly_chart(fig, use_container_width=True)
            with sc2:
                if is_group and selected_user == "Overall":
                    st.markdown("**Most positive participants** (5+ messages)")
                    pos_df = helper.sentiment_by_user(sentiment_df)
                    st.dataframe(pos_df[["Positive", "Neutral", "Negative", "% Positive"]],
                                 use_container_width=True, height=330)
                else:
                    st.markdown("**Breakdown**")
                    st.dataframe(counts.rename("Messages"), use_container_width=True)
        else:
            st.caption("Not enough text messages to analyze sentiment.")
    else:
        st.info("Install `vaderSentiment` (see requirements.txt) to enable sentiment analysis.")

# ---- Raw data ----
with tab_data:
    display_df = df if selected_user == "Overall" else df[df["user"] == selected_user]
    st.dataframe(
        display_df[["date", "user", "message"]].sort_values("date", ascending=False),
        use_container_width=True, height=420,
    )
    st.download_button(
        "⬇️ Download this data as CSV",
        display_df[["date", "user", "message"]].to_csv(index=False).encode("utf-8"),
        file_name="whatsapp_chat_parsed.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Built with Streamlit, Pandas & Plotly · Your chat data stays in your "
    "browser session and is never stored or uploaded elsewhere."
)
