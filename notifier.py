import feedparser
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# ========== CONFIG ==========

FEED_URL = "https://www.lenkaray.cz/feed/"
LAST_POST_FILE = "last_post.txt"

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SUBJECT = "🆕 New blog post on LenkaRay.cz!"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ========== MAIN FUNCTIONS ==========

def get_latest_post():
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        raise Exception("No posts found in feed.")
    latest_entry = feed.entries[0]
    return latest_entry.link, latest_entry.title

def load_last_seen_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_last_seen_post(url):
    with open(LAST_POST_FILE, "w") as f:
        f.write(url)

def send_email_notification(post_url, post_title):
    body = f"New post published: {post_title}\n\nRead it here: {post_url}"

    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = Header(EMAIL_SUBJECT, "utf-8")
    msg['From'] = formataddr(("LenkaRay Notifier", EMAIL_FROM))
    msg['To'] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print("✅ Email sent.")

def send_telegram_notification(post_url, post_title):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not set. Skipping Telegram notification.")
        return

    message = f"🆕 New blog post: {post_title}\n{post_url}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram notification sent.")
        else:
            print(f"❌ Telegram error: {response.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# ========== RUN ==========

def main():
    try:
        latest_url, latest_title = get_latest_post()
        last_seen = load_last_seen_post()

        if latest_url != last_seen:
            print("🔔 New post detected!")
            send_email_notification(latest_url, latest_title)
            send_telegram_notification(latest_url, latest_title)
            save_last_seen_post(latest_url)
        else:
            print("✅ No new posts.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
