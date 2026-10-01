import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import random
from datetime import datetime

# ایجاد یک سرور بسیار ساده HTTP برای پاسخ به نیاز رندر و UptimeRobot
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

threading.Thread(target=run_http_server, daemon=True).start()

import os
import logging
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات خوانده شده از متغیرهای محیطی رندر (یا جایگذاری مستقیم توکن جدید)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8584661357:AAFN7Sl0_H0bOG-M8Og9tyYIDexQKu_0N_k")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "198728977"))

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

stats_data = {
    "total_visits": 0,
    "unique_users": set(),
    "orders_count": 0,
    "messages_count": 0
}

PROJECT_TYPE, USER_NAME, USER_PHONE = range(3)
ADMIN_MESSAGE = range(1)

def get_rotational_photo():
    all_keys = list(PHOTO_IDS.keys())
    day_of_year = datetime.now().timetuple().tm_yday
    selected_key = all_keys[day_of_year % len(all_keys)]
    return PHOTO_IDS.get(selected_key, PHOTO_IDS["logo"])

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
        [InlineKeyboardButton("📺 نمونه کارها و رزومه تصویری", callback_data="portfolio")],
        [InlineKeyboardButton("ℹ️ درباره مدیرعامل و موسسه", callback_data="about")],
        [InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card")],
        [InlineKeyboardButton("✉ ارسال پیام به مدیریت", callback_data="contact_admin")],
        [InlineKeyboardButton("📋 خدمات و تعرفه‌ها", callback_data="services")],
        [InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews")],
        [InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)

    welcome_text = (
        f"سلام {user.first_name} عزیز! 🎬\n\n"
        f"به ربات رسمی موسسه هنری بهادر فیلم خوش‌آمدید**\n\n"
        f"**به مدیریت علی بهادر** - کارگردان، تهیه‌کننده و نویسنده (دارای کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما با بیش از چهار دهه تجربه حرفه‌ای در ساخت سریال، مستندهای فاخر تلویزیونی، تیزر، آگهی و انیمیشن)\n\n"
        "لطفاً بخش مورد نظر خود را از منوی زیر انتخاب کنید"
    )

    header_photo = get_rotational_photo()

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
            parse_mode="MarkDown"
        )
    elif update.message:
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="MarkDown"
        )
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
        text = "🎥 **مستندهای تلویزیونی و بین‌المللی:**\nلطفاً مستند مورد نظر خود را انتخاب کنید:"
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
        text = "⛽ **پروژه‌های ملی نفت و گاز و کتاب مرجع:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
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
        text = "🎨 **انیمیشن‌های آموزشی و طنز:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "port_awards":
        keyboard = [
            [InlineKeyboardButton("لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd")],
            [InlineKeyboardButton("لوح‌ها و تندیس‌های تقدیر ویژه", callback_data="award_tandis")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🏆 **افتخارات، جوایز و لوح‌های سپاس:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "work_tabestan":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "⭐ **بهترین تابستان من**\n\nکارگردانی سریال طنز دفاع مقدس؛ پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_1"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_eshgh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "❤️ **عشق سال‌های جنگ**\n\nکارگردانی و تهیه‌کنندگی سریال با موضوع دفاع مقدس و درام اجتماعی."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_3"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_shab":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🌙 **شب هزار و یکم**\n\nکارگردانی سریال تلویزیونی با حضور بازیگران برجسته (محصول شبکه اول سیما)."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_13"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_ghadam":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🌿 **قدم زدن در بهشت**\n\nکارگردانی تله‌فیلم با ساختار سینمایی و نوآورانه."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_4"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_ershieh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "💼 **ارثیه پرماجرا**\n\nتهیه‌کنندگی فیلم سینمایی ویدیویی پرمخاطب با حضور بازیگران سرشناس."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_5"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_shahzadeh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "👑 **شاهزاده و گدا (۱۳۹۳)**\n\nمحصول موسسه هنری بهادر فیلم به تهیه‌کنندگی علی بهادر."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_6"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_moshtari":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🤝 **مشتری‌مداری (۱۴۰۱)**\n\nسریال آموزشی ۳۰ قسمتی به تهیه‌کنندگی و کارگردانی علی بهادر."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_8"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_barakat":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🌾 **برکت (۱۳۹۷)**\n\nتهیه‌کنندگی و کارگردانی مینی‌سریال تولید شده در بنیاد برکت."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_12"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_gas_book":
        kb = [[InlineKeyboardButton("🔙 بازگشت به پروژه گاز", callback_data="port_gas")]]
        caption = "📖 **کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش**\n\n۱۰۱۸ صفحه، تاریخ شفاهی ۵۰ ساله شرکت ملی گاز ایران."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_11"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_paris":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        caption = "🌍 **مستند کنگره جهانی گاز پاریس (۲۰۱۵)**\n\nمستند تخصصی، صنعتی و بین‌المللی."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_14"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_zendegi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        caption = "🏆 **مستند «زندگی»**\n\nبرنده جوایز متعدد از جشنواره‌های معتبر ملی (جشنواره رشد و دفاع مقدس)."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_2"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "work_esrafi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به انیمیشن‌ها", callback_data="port_anim")]]
        caption = "💡 **انیمیشن آموزشی «اسرافی و انصافی»**\n\nمجموعه ۳۰ قسمتی طنز با محوریت ایمنی گاز شهری و مشاوره شخصیت حکیمانه انصافی."
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_7"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "award_roshd":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        caption = "🎖 **لوح تقدیر جشنواره بین‌المللی فیلم رشد و جشنواره دفاع مقدس**"
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["award_15"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "award_tandis":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        caption = "🏆 **تندیس‌ها و لوح‌های سپاس و تقدیر ویژه مدیران ارشد**"
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["award_16"], caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("مصاحبه روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", callback_data="view_ettelaat_img")],
            [InlineKeyboardButton("مصاحبه هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)", callback_data="view_sedavasima_img")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📰 **بخش مصاحبه‌ها و پوشش رسانه‌ای:**\nبرای مشاهده تصاویر و جزئیات مصاحبه‌های علی بهادر روی گزینه‌های زیر کلیک کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "view_ettelaat_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = (
            "📰 **مصاحبه با روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)**\n\n"
            "عنوان: «سینمای مستند به مدیرانی جسور نیاز دارد» (گفتگو با نژلا پیکانیان)\n\n"
            "[مشاهده آنلاین در سایت اطلاعات](https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF)"
        )
        try:
            await query.message.reply_photo(
                photo="https://www.ettelaat.com/files/fa/news/1405/5/20/161537_485.jpg",
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            try:
                await query.message.delete()
            except Exception:
                pass
        except Exception:
            await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "view_sedavasima_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = (
            "📰 **مصاحبه با هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)**\n\n"
            "عنوان: «تصویر مقاومت در آیینه رسانه؛ نیم قرن تلاش برای هنر و وطن» (گفتگو با عبدالرحمن شلیبیان)"
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        about_text = (
            "ℹ️ **درباره علی بهادر و موسسه هنری بهادر فیلم**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما\n"
            "• **سوابق اجرایی:** مدیر گروه حماسه و دفاع شبکه یک سیما، مدیر واحد دوبلاژ شبکه یک، شروع فعالیت حرفه‌ای از سال ۱۳۶۰ در واحد خبر همدان، بیش از ۱۸ ماه حضور در پوشش رسانه‌ای دوران دفاع مقدس (صداوسیما)\n"
            "• **مدیرعامل:** موسسه هنری بهادر فیلم\n\n"
            "📋 **رزومه تفکیک‌شده و سوابق هنری:**\n\n"
            "🎬 **بخش آثار نمایشی و سریال‌ها:**\n"
            "• کارگردانی سریال «بهترین تابستان من» (۱۳۷۵ - شبکه ۱)\n"
            "• کارگردانی سریال «عشق سال‌های جنگ» (۱۳۸۰ - شبکه ۳)\n"
            "• کارگردانی سریال «شب هزار و یکم» (۱۳۸۷-۱۳۸۸ - شبکه ۱)\n"
            "• کارگردانی فیلم‌های تلویزیونی (تله‌فیلم): «قدم زدن در بهشت»، «ارثیه پرماجرا»، «شاهزاده و گدا»\n"
            "• کارگردانی مجموعه‌ها و مینی‌سریال‌ها: «برکت»، «مشتری‌مداری»\n\n"
            "🎥 **بخش مستندها و پروژه‌های ملی:**\n"
            "• کارگردانی مستند «زندگی» (۱۳۷۰ - برنده جوایز جشنواره‌های دفاع مقدس، رشد و همدان)\n"
            "• تولید و کارگردانی مستندهای برون‌مرزی «نوروز در ازبکستان» (برنده ۲ جایزه از جشنواره‌های برون‌مرزی IRIB) و «بدخشان بام جهان» (تاجیکستان)\n"
            "• تألیف و تدوین کتاب مرجع و ۱۰۱۸ صفحه‌ای «گاز؛ انرژی پاک با نیم قرن تلاش» همراه با تولید مجموعه مستند ۶۳ قسمتی (۱۳۹۵)\n\n"
            "هدف ما به تصویر کشیدن فرهنگ، هنر و تاریخ پربار ایران عزیز است."
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("📸 اینستاگرام موسسه", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        card_text = (
            "💳 **کارت ویزیت دیجیتال موسسه هنری بهادر فیلم**\n\n"
            "👤 **مدیرعامل:** علی بهادر\n"
            "🎯 **تخصص:** کارگردانی، تهیه‌کنندگی و نویسندگی\n"
            "🌐 **وب‌سایت:** alibahador.ir"
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(card_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        services_text = (
            "📋 **خدمات و تعرفه‌ها:**\n\n"
            "۱. ساخت سریال‌های داستانی و تلویزیونی\n"
            "۲. تولید مستندهای فاخر صنعتی و تاریخی\n"
            "۳. ساخت تیزرهای تبلیغاتی و آگهی‌های بازرگانی\n"
            "۴. تولید انیمیشن‌های آموزشی و طنز"
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(services_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        faq_text = (
            "❓ **پرسش‌های متداول (FAQ):**\n\n"
            "• **چگونه پروژه ثبت کنیم؟** از طریق دکمه «ثبت سفارش و درخواست مشاوره» در منوی اصلی.\n"
            "• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه «ارسال پیام به مدیریت»."
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(faq_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
    if query.data == "back_to_menu":
        await start(update, context)
        return ConversationHandler.END
        
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
    await update.message.reply_text("✅ پیام شما با موفقیت به مدیریت موسسه هنری بهادر فیلم ارسال شد.", reply_markup=keyboard)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=get_main_menu())
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    contact_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(order_conv_handler)
    application.add_handler(contact_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bahador Film Bot is starting and polling for updates...")
    application.run_polling(drop_pending_updates=True)

import asyncio

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    
    main()
