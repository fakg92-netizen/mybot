import logging
import urllib.request
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الخاص بك
TOKEN = "8927206296:AAGo8UYpYK346zT0zbDSKA3N6cuH19SWp94"

# سيرفر وهمي لإبقاء Render سعيداً ولا يغلق البوت
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    # Render يرسل المنفذ تلقائياً عبر متغير بيئي اسمه PORT، وإذا لم يجده يستخدم 10000
    import os
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebServer)
    print(f"Web server started on port {port}")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 أهلاً بك في بوت تحليل الأوبشن المستقر على سيرفر Render!\n"
        "أرسل لي رمز السهم بالحروف الكبيرة (مثال: AAPL) وسيتم جلب البيانات فوراً."
    )

async def analyze_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker_symbol = update.message.text.upper().strip()
    await update.message.reply_text(f"🔄 جاري جلب بيانات {ticker_symbol}...")
    
    try:
        req = urllib.request.Request(
            f"https://finnhub.io/api/v1/quote?symbol={ticker_symbol}&token=sandbox_cifbe99r01qg87g9ct10cifbe99r01qg87g9ct1g",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            current_price = data.get("c", 0)
            
            if current_price == 0:
                await update.message.reply_text(f"❌ لم يتم العثور على بيانات للسهم `{ticker_symbol}`.")
                return
                
            reply = f"📊 **بيانات سهم {ticker_symbol} الحالية:**\n\n"
            reply += f"💵 **السعر الحالي:** `${current_price}`\n"
            reply += f"🟢 **أعلى سعر:** `${data.get('h', 0)}`\n"
            reply += f"🔴 **أدنى سعر:** `${data.get('l', 0)}`\n\n"
            reply += "📡 *السيرفر مستقر وبدون أي قيود!*"
            
            await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⚠️ حدث خطأ أثناء جلب البيانات.")

def main():
    # تشغيل السيرفر الوهمي في خلفية الكود
    threading.Thread(target=run_web_server, daemon=True).start()

    # تشغيل البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_option))
    
    print("البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
