# 💬 WhatsApp Chat Analyzer

A Streamlit web app that turns any exported WhatsApp chat (group or 1:1)
into a full statistical and behavioral analysis — activity trends, top
participants, word/emoji usage, sentiment, and reply behavior — with zero
manual data wrangling required.

**🔗 Live app:** [whatsapp-chat-analysis.streamlit.app](https://whatsapp-chat-analysis-shrkpvsh8wxmujytfkg89k.streamlit.app/)

> ⚠️ **Link looking broken / unstyled?** If you clicked this link from
> GitHub and the page looks like plain text with no icons, colors, or
> layout, this is a known Chrome/Edge quirk — **not** a bug in the app.
> **Copy the link above and open it in a new tab (or an Incognito
> window)** — that reliably fixes it. Full explanation in
> [Troubleshooting](#-troubleshooting-page-looks-broken-when-opened-from-github)
> below.

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

## 🛠 Troubleshooting: Page Looks Broken When Opened From GitHub

**Symptom:** you click the live app link from this README (in **Chrome**
or **Edge**), and instead of the normal colorful Streamlit app, you get a
plain, unstyled page — text with no layout, and little labels like
`keyboard_double_arrow_left` where icons should be.

**This is not a bug in the app.** The app itself works fine — you can
prove that by opening the same link directly (paste it into a new tab,
or open it in an Incognito window) and it will look completely normal.

**Why it happens, in plain terms:**

Modern Chrome and Edge try to make browsing feel faster by secretly
"pre-loading" a page in the background *before* you even click a link —
just because you hovered near it or the page you're on hints that you're
likely to go there next. This feature is usually invisible and harmless.

But this app isn't a simple webpage — it's a live, interactive app that
needs to open a real-time connection to fully "wake up" and load its
fonts, icons, and layout. When Chrome/Edge tries to secretly pre-load it
in the background, that wake-up process doesn't finish properly, and
the browser can keep serving you that same broken, half-loaded copy —
which is why it looks broken, and why even reloading the page doesn't
always fix it. Opening the link fresh (new tab or Incognito) forces the
browser to skip the broken pre-loaded copy and load the real thing.

(This is also exactly why **Brave** browser doesn't have this problem —
Brave blocks this kind of background pre-loading by default for privacy
reasons, so it always does a normal, full page load.)

**How to fix it — pick whichever is easiest for you:**

1. **Reliable fix:** copy the app's URL and open it in a **new tab**
   (paste it directly into the address bar), or open it in an
   **Incognito / Private window**. Both of these skip the background
   pre-loading entirely, so the app loads fully and correctly the very
   first time.

2. **Permanent fix (stops it from happening again):**
   Turn off the browser's background pre-loading feature.
   - **Chrome:** go to `chrome://settings/performance` → find
     **"Preload pages"** → set it to **"Standard preloading"** or
     **"No preloading."**
   - **Edge:** go to `edge://settings/privacy` → find **"Preload pages
     for faster browsing and searching"** → turn it **off.**

3. **If you'd rather not change settings:** just use a different browser
   for this link, like **Brave**, which doesn't do this kind of
   pre-loading by default.

   *Note: a plain hard refresh (Ctrl+Shift+R / Cmd+Shift+R) does **not**
   reliably fix this — the browser can still be serving the same
   pre-loaded copy of the page. Opening the link fresh in a new tab or
   Incognito window is what actually works.*
