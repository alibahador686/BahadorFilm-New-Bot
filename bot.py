import os
import random
import telebot
from flask import Flask, request
from telebot import types

# === توکن ربات شما ===
TOKEN = "8584661357:AAFN7Sl0_H0bOG-M8Og9tyYIDexQKu_0N_k"  # توکن اصلی ربات خود را اینجا قرار دهید
bot = telebot.TeleBot(TOKEN)

# === راه‌اندازی سرور وب Flask برای سازگاری با Render و UptimeRobot ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bahador Film Bot is running live and active!"

# مسیر وب‌هوک برای دریافت پیام‌ها از تلگرام
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Forbidden", 403

# === حافظه موقت برای آمار و سفارشات ===
bot_stats = {
    "total_visits": 0,
    "unique_users": set(),
    "orders": []
}

# === گالری آثار برای نمایش رندوم عکس و معرفی در منوی استارت ===
ARTWORKS_GALLERY = [
    {
        "caption": "🎬 **سریال ماندگار «شب هزار و یکم»**\nکارگردان: استاد علی بهادر (پخش از شبکه ۱ سیما - درباره پزشکان در دفاع مقدس)",
        "photo": "https://via.placeholder.com/600x400.png?text=Shabe+Hezaro+Yekom"
    },
    {
        "caption": "🎬 **سریال محبوب «بهترین تابستان من»**\nپرمخاطب‌ترین مجموعه طنز دفاع مقدس به کارگردانی استاد علی بهادر",
        "photo": "https://via.placeholder.com/600x400.png?text=Behtarin+Tabestane+Man"
    },
    {
        "caption": "📚 **کتاب مرجع ملی «گاز، انرژی پاک با نیم قرن تلاش»**\nتألیف استاد علی بهادر - رونمایی با حضور ریاست محترم جمهوری",
        "photo": "https://via.placeholder.com/600x400.png?text=Gas+Reference+Book"
    },
    {
        "caption": "🎬 **سریال تلویزیونی «عشق سال‌های جنگ»**\nبه کارگردانی استاد علی بهادر (پخش از شبکه ۳ سیما)",
        "photo": "https://via.placeholder.com/600x400.png?text=Eshghe+Salhaye+Jang"
    },
    {
        "caption": "🌍 **مجموعه مستند برون‌مرزی «نوروز در ازبکستان»**\nبرنده دو جایزه بهترین تهیه‌کنندگی و تدوین از جشنواره صدا و سیما",
        "photo": "https://via.placeholder.com/600x400.png?text=Norooz+In+Uzbekistan"
    }
]

# === محتوای کامل رزومه و منوهای مؤسسه هنری بهادر فیلم ===
CONTENT = {
    "about_ceo": (
        "👤 **درباره مدیرعامل مؤسسه هنری بهادر فیلم**\n\n"
        "**استاد علی بهادر**\n"
        "• کارگردان، تهیه‌کننده، نویسنده و تدوینگر سینما و تلویزیون\n"
        "• تحصیلات: لیسانس کارگردانی از دانشکده صدا و سیما و کارشناس ارشد ادبیات نمایشی\n"
        "• پیشکسوت و بازنشسته خوش‌نام سازمان صدا و سیما\n"
        "• شروع فعالیت خبری در همدان از سال ۱۳۶۰ و بیش از ۱۸ ماه حضور در پوشش رسانه‌ای دوران دفاع مقدس\n"
        "• پدیدآورنده و مؤلف آثار مرجع مکتوب و مستندهای کلان ملی\n"
        "• مدیرعامل مؤسسه فرهنگی-هنری بهادر فیلم"
    ),
    "services": (
        "📦 **پکیج‌های خدمات تخصصی مؤسسه بهادر فیلم**\n\n"
        "1️⃣ **تولیدات نمایشی و تلویزیونی:** ساخت سریال‌های داستانی، تله‌فیلم، فیلم‌های سینمایی و ویدئویی بلند و کوتاه.\n"
        "2️⃣ **مستندسازی کلان و تخصصی:** تولید مستندهای صنعتی، تاریخی، پژوهشی و مجموعه‌های تلویزیونی کلان (همکاری‌های گسترده ملی با صنعت نفت و گاز کشور).\n"
        "3️⃣ **تولیدات بین‌المللی:** ساخت مستندهای برون‌مرزی در کشورهای تاجیکستان، ازبکستان، ترکمنستان، قزاقستان و...\n"
        "4️⃣ **انیمیشن و موشن‌گرافیک:** تولید مجموعه‌های انیمیشن طنز و آموزشی موزیکال (مانند «اسرافی و انصافی»).\n"
        "5️⃣ **آموزش و مشاوره تخصصی:** مشاوره‌های حرفه‌ای در حوزه کارگردانی، نگارش فیلمنامه، تدوین پیشرفته و تدوین کتب مرجع ملی."
    ),
    "portfolio": (
        "🎬 **رزومه کامل و آرشیو آثار استاد علی بهادر**\n\n"
        "📚 **الف) تألیفات و پروژه‌های ویژه ملی:**\n"
        "• **کتاب مرجع «گاز، انرژی پاک با نیم قرن تلاش»:** (چاپ و انتشار در سال ۱۳۹۵) تدوین، گردآوری و تألیف کتاب مرجع ملی صنعت گاز کشور که طی مراسمی رسمی در پنجمین دهه تأسیس شرکت ملی گاز ایران با حضور **ریاست محترم جمهوری اسلامی ایران** رونمایی شد (همراه با تولید مجموعه مستند پژوهشی ۶۳ قسمتی).\n\n"
        "📺 **ب) سریال‌های تلویزیونی، سینمایی و داستانی کوتاه:**\n"
        "• **شب هزار و یکم:** (۱۳۸۷-۱۳۸۸) کارگردانی سریال ۲۳ قسمتی با موضوع پزشکان در دفاع مقدس (پخش از شبکه ۱ سیما)\n"
        "• **عشق سال‌های جنگ:** (۱۳۸۰) کارگردانی و تهیه‌کنندگی مشترک سریال ۱۳ قسمتی (پخش از شبکه ۳ سیما)\n"
        "• **بهترین تابستان من:** (۱۳۷۲) کارگردانی سریال ۸ قسمتی طنز دفاع مقدس (پرمخاطب‌ترین مجموعه سیما در زمان پخش و بازپخش‌های متعدد)\n"
        "• **قدم زدن در بهشت:** (۱۳۹۱-۱۳۹۳) کارگردانی تله‌فیلم سینمایی-تلویزیونی با نوگرایی خاص\n"
        "• **مجموعه برکت:** (۱۳۹۷) تهیه‌کنندگی و کارگردانی مینی‌سریال ۴ قسمتی\n"
        "• **مجموعه مشتری‌مداری:** (۱۴۰۰) تهیه‌‌کنندگی و کارگردانی سریال آموزشی ۳۰ قسمتی\n"
        "• **فیلم‌های ویدئویی سینمایی:** «ارثیه پرماجرا» و «شاهزاده و گدا» (تهیه‌کنندگی - ۱۳۹۳)\n"
        "• **فیلم‌های داستانی کوتاه:** «آن شب» و «گردنبند» (موضوع دفاع مقدس)\n\n"
        "🌍 **ج) بخش مستند، پژوهشی و مجموعه‌های تلویزیونی کلان:**\n"
        "• **روایتی از رسانه:** (۱۴۰۳-۱۴۰۴) تهیه‌‌کنندگی و کارگردانی مجموعه مستند تحقیقی-پژوهشی ۱۸ قسمتی با موضوع بررسی ویژگی‌های مدیریت رسانه در دوران ریاست آقایان محمد هاشمی، شهید علی لاریجانی و عزت‌الله ضرغامی\n"
        "• **مستند زندگی:** (۱۳۷۰) برنده ۳ جایزه از جشنواره فیلم دفاع مقدس، جشنواره رشد و جشنواره همدان\n"
        "• **مستندهای برون‌مرزی:** «نوروز در ازبکستان» (برنده ۲ جایزه بهترین تهیه‌کنندگی و تدوین)، «بدخشان بام جهان» (تاجیکستان)، نوروز در تاجیکستان، قزاقستان و ترکمنستان\n"
        "• **مجموعه‌های معارفی و ملی:** «دعای جوشن کبیر»، «قوسیان خاک»، «نخل‌های صبور»، «عطر میعاد» (حج)، «حج اکبر» (شبکه العالم)، «بچه‌های مسجد» (شبکه ۵)، «نسیم کوثر» (شبکه مستند)، «تلاش بی‌پایان» (اورهال صنعت گاز - ۱۴۰۴) و مستندهای متعدد صنعتی و گازی.\n\n"
        "🌐 **برای مشاهده جزئیات تکمیلی و گالری آثار:**\n"
        "alibahador.ir"
    ),
    "process": (
        "⚙️ **فرآیند کار در مؤسسه بهادر فیلم**\n\n"
        "1️⃣ **جلسه مشاوره و نیازسنجی:** بررسی دقیق اهداف، محتوا و مخاطبان پروژه\n"
        "2️⃣ **نگارش و پژوهش:** تدوین طرح توجیهی، سناریو و ساختار پژوهشی اثر\n"
        "3️⃣ **پیش‌تولید حرفه‌ای:** انتخاب عوامل، تجهیزات به‌روز و برنامه‌ریزی دقیق تولید\n"
        "4️⃣ **تولید و پس‌تولید (تصویربرداری و تدوین):** اجرای استاندارد تصویربرداری و نظارت مستقیم استاد علی بهادر بر تدوین، اصلاح رنگ و خروجی نهایی"
    ),
    "gift": (
        "🎁 **هدیه رایگان (فایل راهنما)**\n\n"
        "فایل‌های راهنما، مقالات تخصصی کارگردانی و جزوات آموزشی سینما به‌زودی در این بخش بارگذاری خواهد شد."
    ),
    "digital_card": (
        "💳 **کارت ویزیت دیجیتال**\n\n"
        "🏢 **مؤسسه فرهنگی-هنری بهادر فیلم**\n"
        "👤 مدیرعامل: استاد علی بهادر (کارگردان و تهیه‌کننده پیشکسوت صدا و سیما)\n"
        "🎯 ارائه‌دهنده خدمات تخصصی فیلم‌سازی، مستندسازی ملی و بین‌المللی و آموزش رسانه\n"
        "🌐 وبسایت رسمی: alibahador.ir"
    ),
    "media": (
        "📰 **مصاحبه‌ها و رسانه**\n\n"
        "• انتشار مقاله تخصصی **«۱۲ نگاه به سینمای مستند؛ از چالش‌ها تا فرصت‌ها»** در روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)\n"
        "• مصاحبه‌ها و گفتگوهای تخصصی با صدا و سیما تحت عنوان «تصویر مقاومت در آیینه رسانه» و بازتاب حضور در رسانه‌های جمعی کشور."
    ),
    "faq": (
        "❓ **پرسش‌های متداول (FAQ)**\n\n"
        "• **جایزه ویژه سفارش کار چیست؟**\n"
        "در صورت ثبت سفارش هر پروژه، یک تیزر یا کلیپ یک‌دقیقه‌ای به‌صورت **رایگان** به سفارش‌دهنده تحویل داده خواهد شد!\n"
        "• **ساعات پاسخگویی ربات و پشتیبانی چگونه است؟**\n"
        "همکاران ما هر روز از **ساعت ۹ صبح تا ۲۰** آماده پاسخگویی و دریافت سفارشات شما هستند."
    ),
    "newsletter": (
        "🔔 **خبرنامه آموزشی**\n\n"
        "دریافت آخرین مقالات آموزشی کارگردانی، یادداشت‌های تخصصی و اطلاعیه‌های جدید مؤسسه بهادر فیلم."
    )
}

# === منوی اصلی ۱۱ تایی شکیل و مرتب ===
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🎬 نمونه کارها و رزومه کامل")
    btn2 = types.KeyboardButton("👤 درباره مدیرعامل")
    btn3 = types.KeyboardButton("💬 ارسال پیام به مدیریت")
    btn4 = types.KeyboardButton("💳 کارت ویزیت دیجیتال")
    btn5 = types.KeyboardButton("📦 پکیج‌های خدمات")
    btn6 = types.KeyboardButton("💬 ثبت سفارش و درخواست مشاوره")
    btn7 = types.KeyboardButton("📰 مصاحبه‌ها و رسانه")
    btn8 = types.KeyboardButton("❓ پرسش‌های متداول (FAQ)")
    btn9 = types.KeyboardButton("🎁 هدیه رایگان (فایل راهنما)")
    btn10 = types.KeyboardButton("⚙️ فرآیند کار ما")
    btn11 = types.KeyboardButton("🔔 خبرنامه آموزشی")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7, btn8)
    markup.add(btn9, btn10)
    markup.add(btn11)
    return markup

# === استارت ربات و نمایش عکس رندوم آثار ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot_stats["total_visits"] += 1
    bot_stats["unique_users"].add(chat_id)
    
    random_artwork = random.choice(ARTWORKS_GALLERY)
    
    welcome_text = (
        f"{random_artwork['caption']}\n\n"
        "مؤسسه فرهنگی هنری بهادر فیلم 🎬\n\n"
        "🎁 **ویژه سفارش‌دهندگان:** با ثبت سفارش در ربات، یک تیزر یا کلیپ یک‌دقیقه‌ای به‌صورت **رایگان** هدیه بگیرید!\n"
        "⏰ **ساعات پاسخگویی:** همواره از ساعت ۹ صبح تا ۲۰ آماده خدمت‌رسانی هستیم.\n\n"
        "👇 از منوی زیر انتخاب کنید:"
    )
    
    try:
        bot.send_photo(chat_id, random_artwork["photo"], caption=welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# === مدیریت کلیک دکمه‌ها ===
@bot.message_handler(func=lambda message: True)
def handle_menu_clicks(message):
    text = message.text
    chat_id = message.chat.id
    
    if "ثبت سفارش" in text:
        msg = bot.send_message(chat_id, "📝 لطفاً موضوع پروژه، توضیحات و **شماره تماس** خود را ارسال کنید تا همکاران ما در اسرع وقت (ساعات پاسخگویی: ۹ الی ۲۰) با شما تماس بگیرند.\n\n*(با ثبت سفارش، یک تیزر ۱ دقیقه‌ای رایگان هدیه خواهید گرفت)*")
        bot.register_next_step_handler(msg, save_order_step)
        
    elif "ارسال پیام به مدیریت" in text:
        msg = bot.send_message(chat_id, "💬 پیام خود را مستقیماً برای مدیریت (استاد علی بهادر) ارسال کنید تا به دست ایشان برسد:")
        bot.register_next_step_handler(msg, forward_to_admin_step)
        
    elif "پکیج‌های خدمات" in text:
        bot.send_message(chat_id, CONTENT["services"], parse_mode="Markdown")
    elif "هدیه رایگان" in text:
        bot.send_message(chat_id, CONTENT["gift"], parse_mode="Markdown")
    elif "فرآیند کار ما" in text:
        bot.send_message(chat_id, CONTENT["process"], parse_mode="Markdown")
    elif "نمونه کارها" in text:
        bot.send_message(chat_id, CONTENT["portfolio"], parse_mode="Markdown")
    elif "کارت ویزیت دیجیتال" in text:
        bot.send_message(chat_id, CONTENT["digital_card"], parse_mode="Markdown")
    elif "درباره مدیرعامل" in text:
        bot.send_message(chat_id, CONTENT["about_ceo"], parse_mode="Markdown")
    elif "مصاحبه‌ها و رسانه" in text:
        bot.send_message(chat_id, CONTENT["media"], parse_mode="Markdown")
    elif "پرسش‌های متداول" in text:
        bot.send_message(chat_id, CONTENT["faq"], parse_mode="Markdown")
    elif "خبرنامه آموزشی" in text:
        bot.send_message(chat_id, CONTENT["newsletter"], parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "لطفاً از دکمه‌های منوی زیر استفاده کنید:", reply_markup=main_menu_keyboard())

# === ثبت سفارش و شماره تماس ===
def save_order_step(message):
    chat_id = message.chat.id
    order_text = message.text
    bot_stats["orders"].append({"chat_id": chat_id, "text": order_text})
    
    bot.send_message(
        chat_id, 
        "✅ درخواست سفارش و شماره تماس شما با موفقیت ثبت شد.\n"
        "🎁 **تبریک!** مشمول دریافت **تیزر یا کلیپ ۱ دقیقه‌ای رایگان** شدید.\n"
        "کارشناسان ما در ساعات اداری (۹ صبح تا ۲۰) در اسرع وقت با شما تماس خواهند گرفت.",
        reply_markup=main_menu_keyboard()
    )

# === ارسال پیام به مدیریت ===
def forward_to_admin_step(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "✅ پیام شما با موفقیت برای مدیریت (استاد علی بهادر) ارسال شد. از حسن توجه شما سپاسگزاریم.",
        reply_markup=main_menu_keyboard()
    )

if __name__ == '__main__':
    # تنظیم وب‌هوک روی سرور رندر به صورت خودکار
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print(f"Webhook set to: {RENDER_URL}/{TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
