import telebot
import requests
import re
import os

# Thay token bot của bạn
BOT_TOKEN = "7870901710:AAGs5BoaksY_toFV8XSOsEZ-BxfVTDAdOYI"
bot = telebot.TeleBot(BOT_TOKEN)

NETFLIX_CHECK_URL = "https://www.netflix.com/browse"
LIVE_COOKIES_FILE = "live_cookies.txt"

def check_cookie(secure_id, netflix_id):
    """Kiểm tra cookie Netflix có live không"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": f"SecureNetflixId={secure_id}; NetflixId={netflix_id}"
    }
    
    try:
        response = requests.get(NETFLIX_CHECK_URL, headers=headers, allow_redirects=False)
        return response.status_code == 200
    except requests.RequestException:
        return False

def read_cookies_from_file(file_path):
    """Trích xuất cookie từ file"""
    cookies = []
    pattern = r"SecureNetflixId=([\w%.-]+)\s*;\s*NetflixId=([\w%.-]+)"
    
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                secure_id = match.group(1)
                netflix_id = match.group(2)
                cookies.append((secure_id, netflix_id))

    return cookies

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Chào bạn! Hãy gửi một file .txt chứa danh sách cookie để tôi kiểm tra.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Xử lý khi người dùng gửi file txt"""
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"{message.chat.id}_cookies.txt"
    with open(file_path, "wb") as file:
        file.write(downloaded_file)

    bot.reply_to(message, "📂 Đã nhận file! Đang kiểm tra cookie...")

    cookies = read_cookies_from_file(file_path)
    
    if not cookies:
        bot.reply_to(message, "⚠️ Không tìm thấy cookie hợp lệ trong file.")
        return

    live_cookies = []

    for secure_id, netflix_id in cookies:
        if check_cookie(secure_id, netflix_id):
            live_cookies.append(f"SecureNetflixId={secure_id}; NetflixId={netflix_id}")

    if not live_cookies:
        bot.reply_to(message, "❌ Không có cookie nào LIVE.")
    else:
        with open(LIVE_COOKIES_FILE, "w", encoding="utf-8") as file:
            file.write("\n".join(live_cookies))

        with open(LIVE_COOKIES_FILE, "rb") as file:
            bot.send_document(message.chat.id, file, caption="✅ Danh sách cookie LIVE!")

    os.remove(file_path)  # Xóa file tạm sau khi xử lý

# Chạy bot
print("🤖 Bot đang chạy...")
bot.infinity_polling()
