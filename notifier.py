import os
print("Current working directory:", os.getcwd())
import feedparser
import os
import smtplib

# ========== CONFIG ==========

FEED_URL = "https://www.lenkaray.cz/feed/"
LAST_POST_FILE = "last_post.txt"

EMAIL_FROM = "micheleliasbechara@gmail.com"
EMAIL_TO = "micheleliasbechara@gmail.com"
EMAIL_SUBJECT = "🆕 New blog post on LenkaRay.cz!"
EMAIL_PASSWORD = "pfbl dqno orhq abtj"  # Use app password, not your main one

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
    
    # Use MIMEText with UTF-8 encoding for the email content
    from email.mime.text import MIMEText
    from email.header import Header
    from email.utils import formataddr

    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = Header(EMAIL_SUBJECT, "utf-8")
    msg['From'] = formataddr(("LenkaRay Notifier", EMAIL_FROM))
    msg['To'] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


# ========== RUN ==========

def main():
    try:
        latest_url, latest_title = get_latest_post()
        last_seen = load_last_seen_post()

        if latest_url != last_seen:
            print("🔔 New post detected!")
            send_email_notification(latest_url, latest_title)
            save_last_seen_post(latest_url)
        else:
            print("✅ No new posts.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

