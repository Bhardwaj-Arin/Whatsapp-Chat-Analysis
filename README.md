# 💬 WhatsApp Chat Analyzer

A Streamlit web app that turns any exported WhatsApp chat (group or 1:1)
into a full statistical and behavioral analysis — activity trends, top
participants, word/emoji usage, sentiment, and reply behavior — with zero
manual data wrangling required.

**🔗 Live app:** [whatsapp-chat-analysis.streamlit.app](https://whatsapp-chat-analysis-shrkpvsh8wxmujytfkg89k.streamlit.app/)

> 🔒 **Privacy note:** this repo does **not** ship with anyone's real
> personal chat. No sample chat is bundled by default, since real
> conversations can't be shared publicly. **To use the app, export your
> own chat from WhatsApp and upload or paste it yourself** — everything
> is parsed locally in your own session; nothing is uploaded to a server
> or persisted anywhere. (If you drop your own demo `.txt` export into
> `datasets/`, the app will automatically pick it up and offer it as a
> "Try a sample chat" option in the sidebar — see below.)

## ✨ Features

- **Flexible input** — upload a `.txt` export, or paste chat text
  directly. A "Try a sample chat" option appears automatically if you add
  your own demo export(s) to `datasets/` (see note above).
- **Robust parsing** — auto-detects Android/iOS, 12h/24h, and 2-digit/
  4-digit-year WhatsApp export formats.
- **Top statistics** — messages, words, media, links, participants,
  active days, chat span, deleted messages.
- **Auto-generated key insights** — plain-English callouts (busiest day,
  most active participant, dominant sentiment, top emoji, etc.).
- **Activity analysis** — monthly/daily timelines, busiest day/month/hour,
  and a day-vs-hour weekly activity heatmap.
- **Participant analysis** — message share per person, average message
  length, who starts conversations, and typical reply speed.
- **Word analysis** — word cloud and most frequent words, with a built-in
  Hinglish stopword list.
- **Emoji analysis** — frequency breakdown and distribution chart.
- **Sentiment analysis** — per-message Positive / Neutral / Negative
  scoring (VADER), aggregated overall and per participant.
- **Data export** — download the parsed chat as CSV.

## 🖥️ Tech Stack

- **App / UI:** Streamlit
- **Data processing:** Pandas, regex-based parsing
- **Visualization:** Plotly (interactive charts), Matplotlib (word cloud)
- **NLP:** VADER Sentiment, WordCloud, urlextract, emoji

## 📂 Project Structure

```
whatsapp-chat-analyzer/
├── app.py              # Streamlit UI
├── preprocessor.py      # Raw .txt export -> structured DataFrame
├── helper.py            # All analysis/statistics functions
├── requirements.txt
├── datasets/
│   ├── stop_hinglish.txt        # Stopword list used for word analysis
│   └── (optional) *.txt         # Drop your own demo export(s) here to
│                                 # enable the "Try a sample chat" option
└── notebooks/
    └── whatsapp_analysis.ipynb  # Original exploratory analysis
```

## 🚀 Try It Out

- **Live app:** [whatsapp-chat-analysis.streamlit.app](https://whatsapp-chat-analysis-shrkpvsh8wxmujytfkg89k.streamlit.app/) — no setup required.
- **Run locally:**

```bash
git clone <this-repo>
cd whatsapp-chat-analyzer
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## 📱 How to Export Your Own WhatsApp Chat

1. Open the chat (individual or group) in WhatsApp.
2. Tap **⋮ (More)** → **Export chat**.
3. Choose **Without media**.
4. Upload the resulting `.txt` file in the app, or open it and paste the
   contents into the "Paste chat text" option.

## 🧠 Notes on the Analysis

- Sentiment scoring uses VADER, a lexicon-based model tuned for short,
  informal text. It's a useful signal, not a verdict — sarcasm, slang,
  and Hinglish phrasing can throw it off.
- "Reply speed" and "conversation starters" are heuristics based on
  message timing (e.g., a reply is a message from a different user
  within 3 hours of the previous one) rather than actual message-thread
  data, since WhatsApp exports don't include reply references.
