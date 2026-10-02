import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# تنظیمات لاگینگ برای پایش دقیق رویدادها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# سرور HTTP بسیار ساده جهت پاسخ به نیاز پلتفرم Render و UptimeRobot (روی پورت 10000)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# اجرای سرور در یک ترد جداگانه به صورت دیمون
threading.Thread(target=run_http_server, daemon=True).start()

# توکن و شناسه ادمین از متغیرهای محیطی رندر
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8584661357:AAHfHd78FGHDInBD0fmtF3X6jcTe1gojDuE")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "198728977"))

# شناسه‌های تصاویر و پوسترهای آثار (Photo File IDs)
PHOTO_IDS = {
    "logo": "AgACAgQAAxkBAANoarTxcvaLVFFDuPSMVCLQ6XXcCEgAAj8QaxslQqhRHyuGPLEPCTYBAAMCAAN5AAM9BA",
    "work_1": "AgACAgQAAxkBAANZarTpN4VZ_zuBvY8qfr8XmbNw7pkAAjQQaxslQqhRXfvpAAFEs83zAQADAgADeQADPQQ",
    "work_2": "AgACAgQAAxkBAANearTvmlgwxRnFLGAlGWxU8rkT-1AAAjgQaxslQqhR53FaIRSpKHYBAAMCAAN5AAM9BA",
    "work_3": "AgACAgQAAxkBAANgarTwM3C7YugVl34Zx5zmdfqblxEAAjoQaxslQqhRjoQOS53pRBEBAAMCAAN5AAM9BA",
    "work_4": "AgACAgQAAxkBAANiarTwitFl3GizqfXA940Rm6KoAywAAjsQaxslQqhRLcDSK7px4JIBAAMCAAN5AAM9BA",
    "work_5": "AgACAgQAAxkBAANkarTw6xfxZ84odXO_PlgJBVLWvY8AAjwQaxslQqhR3hmwjUYRM0wBAAMCAAN5AAM9BA",
    "work_6": "AgACAgQAAxkBAANmarTxHy9f8plmCbwBwH-n-0U3eUcAAj4QaxslQqhR79dvxxWcmpIBAAMCAAN5AAM9BA",
    "work_7": "AgACAgQAAxkBAANoarTxcvaLVFFDuPSMVCLQ6XXcCEgAAj8QaxslQqhRHyuGPLEPCTYBAAMCAAN5AAM9BA",
    "work_8": "AgACAgQAAxkBAANqarTxuueYW1gjMcHlaCaDZJXtJ1EAAkEQaxslQqhR-aYKXskUhHIBAAMCAAN5AAM9BA",
    "work_9": "AgACAgQAAxkBAANsarTx9X_9z_IFk7DvWGmtVGkGB0AAAkIQaxslQqhRUjAa4c-6XLwBAAMCAAN5AAM9BA",
    "work_10": "AgACAgQAAxkBAANuarTyOwkGmkfs6tcNodNBGzujgCwAAkMQaxslQqhRRxnzoph9E4EBAAMCAAN5AAM9BA",
    "work_11": "AgACAgQAAxkBAANwarTyYMpvBUdAvWgxpNDsokdZzAkAAkQQaxslQqhR0jS6MO2oIdQBAAMCAAN5AAM9BA",
    "work_12": "AgACAgQAAxkBAANyarTyuYCz-nKqjilkshH7l-IZl_8AAkUQaxslQqhR_zB2Ple2rxMBAAMCAAN5AAM9BA",
    "work_13": "AgACAgQAAxkBAAN0arTz_Q5l6uW9hJ3uQ1wAARXGq78AAkYQaxslQqhR6m1k_3_5-1wBAAMCAAN5AAM9BA",
    "work_14": "AgACAgQAAxkBAAN2arT0a6YpX7aK5f8v8x5Y1AABAAH8AAkcAaxslQqhR8p9kZ9l_3AEBAAMCAAN5AAM9BA",
    "award_15": "AgACAgQAAxkBAAOBarT63lwTbK1i98T2La7qVD3q4gEAAlQQaxslQqhRbvL3WI2R2JkBAAMCAAN5AAM9BA",
    "award_16": "AgACAgQAAxkBAAODarT69lI0d1-rQQs-AwTKjAO7WQsAAlUQaxslQqhRpgYVe0-1E6QBAAMCAAN5AAM9BA",
    "award_17": "AgACAgQAAxkBAAOFarT7AAH5vKOpDySxkrpJFz3UX-5eAAJWEGsbJUKoUTD95jq44Ny8AQADAgADeQADPQQ",
    "award_18": "AgACAgQAAxkBAAOHarT7Ecmh4vTKQmVMRKyi95ijsXYAAlcQaxslQqhR703ya5-kizwBAAMCAAN5AAM9BA",
    "award_19": "AgACAgQAAxkBAAOJarT7JWk3v6x2f7W4V6_1a8q3b68AAloQaxslQqhR9p1kZ9l_3AEBAAMCAAN5AAM9BA",
    "award_20": "AgACAgQAAxkBAAOLarT7O91v6x2f7W4V6_1a8q3b69AAlsQaxslQqhR5p1kZ9l_3AEBAAMCAAN5AAM9BA"
}

# آمار تفصیلی ربات
stats_data = {
    "total_visits": 0,
    "unique_users": set(),
    "orders_count": 0,
    "messages_count": 0
}

# مراحل مکالمه ConversationHandler برای ثبت سفارش و ارسال پیام به مدیریت
PROJECT_TYPE, USER_NAME, USER_PHONE = range(3)
ADMIN_MESSAGE = range(1)

def get_rotational_photo():
    all_keys = list(PHOTO_IDS.keys())
    day_of_year = datetime.now().timetuple().tm_yday
    selected_key = all_keys[day_of_year % len(all_keys)]
    return PHOTO_IDS.get(selected_key, PHOTO_IDS["logo"])

# منوی اصلی کامل ۱۱ گزینه‌ای (شامل تمامی دکمه‌های درخواستی)
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
        [InlineKeyboardButton("📦 پکیج‌های خدمات", callback_data="services"), InlineKeyboardButton("🎁 هدیه رایگان (راهنما)", callback_data="free_gift")],
        [InlineKeyboardButton("🎬 نمونه کارها و رزومه کامل", callback_data="portfolio"), InlineKeyboardButton("⚙️ فرآیند کار ما", callback_data="workflow")],
        [InlineKeyboardButton("ℹ️ درباره مدیرعامل", callback_data="about"), InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card")],
        [InlineKeyboardButton("✉️ ارسال پیام به مدیریت", callback_data="contact_admin"), InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews")],
        [InlineKeyboardButton("🔔 خبرنامه آموزشی", callback_data="newsletter"), InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)

    welcome_text = (
        f"سلام {user.first_name} عزیز! 🎬\n\n"
        f"به ربات رسمی موسسه هنری بهادر فیلم خوش‌آمدید\n\n"
        f"**به مدیریت علی بهادر** - کارگردان، تهیه‌کننده و نویسنده (دارای کارشناسی ارشد ادبیات نمایشی و کارگردانی از صداوسیما با بیش از چهار دهه تجربه حرفه‌ای در ساخت سریال، مستندهای فاخر، تیزر و انیمیشن)\n\n"
        "لطفاً بخش مورد نظر خود را از منوی زیر انتخاب کنید:"
    )

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    text = (
        "📊 **آمار ربات موسسه هنری بهادر فیلم:**\n\n"
        f"👥 کل بازدیدها: {stats_data['total_visits']}\n"
        f"👤 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🛒 سفارش‌های ثبت شده: {stats_data['orders_count']}\n"
        f"✉️ پیام‌های دریافتی مدیریت: {stats_data['messages_count']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        welcome_text = "🎬 به منوی اصلی موسسه هنری بهادر فیلم خوش آمدید.\nلطفاً بخش مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=get_rotational_photo(),
            caption=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    elif data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("📺 سریال‌ها و فیلم‌های داستانی", callback_data="port_series")],
            [InlineKeyboardButton("🎥 مستندهای تلویزیونی و بین‌المللی", callback_data="port_docs")],
            [InlineKeyboardButton("⛽ پروژه ملی و کتاب مرجع گاز", callback_data="port_gas")],
            [InlineKeyboardButton("🎨 انیمیشن‌های آموزشی و طنز", callback_data="port_anim")],
            [InlineKeyboardButton("🏆 جوایز و لوح‌های سپاس", callback_data="port_awards")],
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"), InlineKeyboardButton("📸 اینستاگرام", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📁 **بخش نمونه‌کارها و رزومه تصویری علی بهادر**\n\nلطفاً حوزه مورد نظر خود را برای مشاهده آثار همراه با پوستر و تصویر انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    elif data == "port_series":
        keyboard = [
            [InlineKeyboardButton("(۱۳۷۲) بهترین تابستان من", callback_data="work_tabestan")],
            [InlineKeyboardButton("(۱۳۸۰-۱۳۷۹) عشق سال‌های جنگ", callback_data="work_eshgh")],
            [InlineKeyboardButton("(۱۳۸۸) شب هزار و یکم", callback_data="work_shab")],
            [InlineKeyboardButton("(۱۳۹۱) قدم زدن در بهشت", callback_data="work_ghadam")],
            [InlineKeyboardButton("(۱۳۹۳) ارثیه پرماجرا", callback_data="work_ershieh")],
            [InlineKeyboardButton("(۱۳۹۳) شاهزاده و گدا", callback_data="work_shahzadeh")],
            [InlineKeyboardButton("(۱۴۰۱) مشتری‌مداری", callback_data="work_moshtari")],
            [InlineKeyboardButton("(۱۳۹۷) برکت", callback_data="work_barakat")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "📺 **سریال‌های تلویزیونی و فیلم‌های داستانی:**\nلطفاً اثر مورد نظر خود را برای مشاهده پوستر و جزئیات انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    elif data == "port_docs":
        keyboard = [
            [InlineKeyboardButton("مستند «زندگی»", callback_data="work_zendegi")],
            [InlineKeyboardButton("(۲۰۱۵) مستند کنگره جهانی گاز پاریس", callback_data="work_paris")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🎥 **مستندهای تلویزیونی و بین‌المللی:**"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش", callback_data="work_gas_book")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "⛽ **پروژه‌های ملی نفت و گاز و کتاب مرجع:**"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_anim":
        keyboard = [
            [InlineKeyboardButton("انیمیشن آموزشی «اسرافی و انصافی»", callback_data="work_esrafi")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🎨 **انیمیشن‌های آموزشی و طنز:**"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_awards":
        keyboard = [
            [InlineKeyboardButton("لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd")],
            [InlineKeyboardButton("تندیس‌ها و لوح‌های تقدیر ویژه", callback_data="award_tandis")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🏆 **افتخارات و جوایز:**"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # نمایش جزئیات و پوسترهای آثار با کلیک روی هر اثر
    elif data in ["work_tabestan", "work_eshgh", "work_shab", "work_ghadam", "work_ershieh", "work_shahzadeh", "work_moshtari", "work_barakat", "work_gas_book", "work_paris", "work_zendegi", "work_esrafi", "award_roshd", "award_tandis"]:
        kb = [[InlineKeyboardButton("🔙 بازگشت به فهرست آثار", callback_data="port_series")]]
        
        captions = {
            "work_tabestan": "⭐ **بهترین تابستان من**\n\nکارگردانی سریال طنز دفاع مقدس؛ پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش.",
            "work_eshgh": "❤️ **عشق سال‌های جنگ**\n\nکارگردانی و تهیه‌کنندگی سریال با موضوع دفاع مقدس و درام اجتماعی.",
            "work_shab": "🌙 **شب هزار و یکم**\n\nکارگردانی سریال تلویزیونی با حضور بازیگران برجسته (محصول شبکه اول سیما).",
            "work_ghadam": "🌿 **قدم زدن در بهشت**\n\nکارگردانی تله‌فیلم با ساختار سینمایی و نوآورانه.",
            "work_ershieh": "💼 **ارثیه پرماجرا**\n\nتهیه‌کنندگی فیلم سینمایی ویدیویی پرمخاطب.",
            "work_shahzadeh": "👑 **شاهزاده و گدا (۱۳۹۳)**\n\nمحصول موسسه هنری بهادر فیلم به تهیه‌کنندگی علی بهادر.",
            "work_moshtari": "🤝 **مشتری‌مداری (۱۴۰۱)**\n\nسریال آموزشی ۳۰ قسمتی به تهیه‌کنندگی و کارگردانی علی بهادر.",
            "work_barakat": "🌾 **برکت (۱۳۹۷)**\n\nتهیه‌کنندگی و کارگردانی مینی‌سریال تولید شده در بنیاد برکت.",
            "work_gas_book": "📖 **کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش**\n\n۱۰۱۸ صفحه، تاریخ شفاهی ۵۰ ساله شرکت ملی گاز ایران.",
            "work_paris": "🌍 **مستند کنگره جهانی گاز پاریس (۲۰۱۵)**\n\nمستند تخصصی، صنعتی و بین‌المللی.",
            "work_zendegi": "🏆 **مستند «زندگی»**\n\nبرنده جوایز متعدد از جشنواره‌های معتبر ملی (رشد و دفاع مقدس).",
            "work_esrafi": "💡 **انیمیشن آموزشی «اسرافی و انصافی»**\n\nمجموعه ۳۰ قسمتی طنز با محوریت ایمنی گاز شهری.",
            "award_roshd": "🎖 **لوح تقدیر جشنواره بین‌المللی فیلم رشد و جشنواره دفاع مقدس**",
            "award_tandis": "🏆 **تندیس‌ها و لوح‌های سپاس و تقدیر ویژه مدیران ارشد**"
        }
        
        photo_key = data if data in PHOTO_IDS else "logo"
        try:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=PHOTO_IDS[photo_key],
                caption=captions.get(data, "جزئیات اثر"),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown"
            )
            await query.message.delete()
        except Exception as e:
            logger.error(f"Error sending photo for {data}: {e}")
            await query.message.reply_text(captions.get(data, "جزئیات اثر"), reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = "📦 **پکیج‌های خدمات موسسه:**\n\n۱. ساخت سریال‌های داستانی و تلویزیونی\n۲. تولید مستندهای فاخر صنعتی و تاریخی\n۳. ساخت تیزرهای تبلیغاتی و آگهی‌های بازرگانی\n۴. تولید انیمیشن‌های آموزشی و طنز"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "free_gift":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = "🎁 **هدیه رایگان (فایل راهنما):**\n\nبه زودی فایل‌های آموزشی، مقالات و راهنمای تخصصی کارگردانی توسط علی بهادر منتشر خواهد شد."
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "workflow":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = "⚙️ **فرآیند کار ما:**\n\n۱. ثبت درخواست و مشاوره اولیه\n۲. بررسی فیلمنامه، طرح یا ایده\n۳. عقد قرارداد و پیش‌تولید\n۴. تولید و فیلم‌برداری\n۵. پس‌تولید، تدوین و اصلاح رنگ\n۶. تحویل نهایی اثر"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "newsletter":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = "🔔 **خبرنامه آموزشی:**\n\nجهت دریافت آخرین مقالات آموزشی، یادداشت‌های سینمایی و اخبار تولیدات موسسه به وب‌سایت رسمی سر بزنید."
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        about_text = (
            "ℹ️ **درباره علی بهادر و موسسه هنری بهادر فیلم**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و کارگردانی از صداوسیما\n"
            "• **سوابق اجرایی:** مدیر گروه حماسه و دفاع شبکه یک سیما، مدیر واحد دوبلاژ شبکه یک، شروع فعالیت از سال ۱۳۶۰ در واحد خبر همدان، بیش از ۱۸ ماه حضور در پوشش رسانه‌ای دفاع مقدس\n"
            "• **مدیرعامل:** موسسه هنری بهادر فیلم\n\n"
            "هدف ما به تصویر کشیدن فرهنگ، هنر و تاریخ پربار ایران عزیز است."
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        card_text = "💳 **کارت ویزیت دیجیتال:**\n\n👤 مدیرعامل: علی بهادر\n🎯 تخصص: کارگردانی، تهیه‌کنندگی و نویسندگی\n🌐 وب‌سایت: alibahador.ir"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(card_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("مصاحبه روزنامه اطلاعات", callback_data="view_ettelaat_img")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📰 **مصاحبه‌ها و رسانه:**\nبرای مشاهده پوشش رسانه‌ای و گفتگوهای علی بهادر انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "view_ettelaat_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = "📰 **مصاحبه با روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)**\n\n[مشاهده آنلاین در سایت اطلاعات](https://www.ettelaat.com/news/161537)"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        faq_text = "❓ **پرسش‌های متداول (FAQ):**\n\n• **چگونه پروژه ثبت کنیم؟** از طریق دکمه ثبت سفارش.\n• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه ارسال پیام به مدیریت."
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(faq_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Conversation Handler برای ثبت سفارش
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("سریال و فیلم داستانی", callback_data="p_series")],
        [InlineKeyboardButton("ساخت مستند", callback_data="p_documentary")],
        [InlineKeyboardButton("تیزر تبلیغاتی", callback_data="p_teaser")],
        [InlineKeyboardButton("انیمیشن", callback_data="p_anim")],
        [InlineKeyboardButton("انصراف", callback_data="back_to_menu")]
    ]
    text = "🛒 **ثبت سفارش جدید - مرحله ۱ از ۳**\n\nلطفاً نوع پروژه مورد نظر خود را انتخاب کنید:"
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return PROJECT_TYPE

async def receive_project_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mapping = {
        "p_series": "سریال یا فیلم داستانی",
        "p_documentary": "مستند",
        "p_teaser": "تیزر تبلیغاتی",
        "p_anim": "انیمیشن"
    }
    context.user_data['project_type'] = mapping.get(query.data, "نامشخص")
    text = "🛒 **ثبت سفارش جدید - مرحله ۲ از ۳**\n\nلطفاً **نام و نام خانوادگی خود را ارسال کنید:**"
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.message.reply_text(text, parse_mode="Markdown")
    return USER_NAME

async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    text = "🛒 **ثبت سفارش جدید - مرحله ۳ از ۳**\n\nلطفاً **شماره تماس خود را ارسال کنید** تا همکاران ما با شما تماس بگیرند:"
    await update.message.reply_text(text, parse_mode="Markdown")
    return USER_PHONE

async def receive_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_phone'] = update.message.text
    stats_data["orders_count"] += 1
    
    p_type = context.user_data.get('project_type')
    u_name = context.user_data.get('user_name')
    u_phone = context.user_data.get('user_phone')
    user = update.effective_user
    
    summary = (
        "✅ **سفارش شما با موفقیت ثبت شد**\n\n"
        f"🔹 نوع پروژه: {p_type}\n"
        f"👤 نام: {u_name}\n"
        f"📞 شماره تماس: {u_phone}\n\n"
        "کارشناسان موسسه هنری بهادر فیلم به زودی با شما تماس خواهند گرفت."
    )
    
    admin_order_notification = (
        "🚨 **سفارش جدید ثبت شد!**\n\n"
        f"🔹 نوع پروژه: {p_type}\n"
        f"👤 نام کاربر: {u_name}\n"
        f"📞 شماره تماس: {u_phone}\n"
        f"🌐 آیدی تلگرام: @{user.username if user.username else 'ندارد'} (ID: {user.id})"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_order_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send order notification to admin: {e}")
        
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

# Conversation Handler برای ارسال پیام به مدیریت
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("انصراف", callback_data="back_to_menu")]]
    text = "✉️ **ارسال پیام به مدیریت**\n\nلطفاً پیام، نظر یا درخواست خود را بنویسید تا برای مدیریت ارسال شود:"
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ADMIN_MESSAGE

async def receive_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_data["messages_count"] += 1
    user_msg = update.message.text
    user = update.effective_user
    
    forward_text = (
        "✉️ **پیام جدید از مخاطب ربات:**\n\n"
        f"👤 فرستنده: {user.full_name}\n"
        f"🔗 نام کاربری: @{user.username if user.username else 'ندارد'} (ID: {user.id})\n\n"
        f"💬 متن پیام:\n{user_msg}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=forward_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to forward message to admin: {e}")
        
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text("✅ پیام شما با موفقیت به مدیریت موسسه هنری بهادر فیلم ارسال شد.", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=get_main_menu())
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type, pattern="^p_")],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(start, pattern="^back_to_menu$")],
    )
    
    contact_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(start, pattern="^back_to_menu$")],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(order_conv_handler)
    application.add_handler(contact_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bahador Film Bot is starting and polling for updates...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    main()
