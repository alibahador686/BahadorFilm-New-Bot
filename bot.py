import os
import random
import threading
from flask import Flask, request
from datetime import datetime
import telebot
from telebot import types

# === راه‌اندازی سرور وب Flask برای سازگاری ۱۰۰٪ با Render و UptimeRobot ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bahador Film Bot is running live and active!"

# === توکن ربات و آیدی ادمین ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8584661357:AAFN7Sl0_H0bOG-M8Og9tyYIDexQKu_0N_k")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "198728977"))

bot = telebot.TeleBot(TOKEN)

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

# === آمار ربات ===
stats_data = {
    "total_visits": 0,
    "unique_users": set(),
    "orders_count": 0,
    "messages_count": 0
}

# === نگاشت عکس‌ها و شناسه‌های تلگرامی (File IDs) ===
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
    "award_16": "AgACAgQAAxkBAAODarT69lI0d1-rQQs-AwTKjAO7WQsAAlUQaxslQqhRpgYVe0-1E6QBAAMCAAN5AAM9BA"
}

def get_rotational_photo():
    all_keys = list(PHOTO_IDS.keys())
    day_of_year = datetime.now().timetuple().tm_yday
    selected_key = all_keys[day_of_year % len(all_keys)]
    return PHOTO_IDS.get(selected_key, PHOTO_IDS["logo"])

# === منوی اصلی شیشه‌ای (Inline Keyboard) شکیل و حرفه‌ای ===
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🛒 ثبت سفارش و درخواست مشاوره", callback_data="start_order"),
        types.InlineKeyboardButton("📺 نمونه کارها و رزومه تصویری", callback_data="portfolio"),
        types.InlineKeyboardButton("ℹ️ درباره مدیرعامل و موسسه", callback_data="about"),
        types.InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card"),
        types.InlineKeyboardButton("✉️️ ارسال پیام به مدیریت", callback_data="contact_admin"),
        types.InlineKeyboardButton("📋 خدمات و تعرفه‌ها", callback_data="services"),
        types.InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews"),
        types.InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")
    )
    return markup

# === دستور استارت ===
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = message.from_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    
    welcome_text = (
        f"سلام {user.first_name} عزیز! 🎬\n\n"
        "**به ربات رسمی موسسه هنری بهادر فیلم خوش آمدید**\n\n"
        "به مدیریت **علی بهادر** - کارگردان، تهیه‌کننده و نویسنده (دارای کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما با بیش از چهار دهه تجربه حرفه‌ای در ساخت سریال، مستندهای فاخر تلویزیونی، تیزر، آگهی و انیمیشن).\n\n"
        "لطفاً بخش مورد نظر خود را از منوی زیر انتخاب کنید:"
    )
    
    header_photo = get_rotational_photo()
    try:
        bot.send_photo(chat_id, header_photo, caption=welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# === دستور آمار (فقط برای ادمین) ===
@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_CHAT_ID:
        return
    text = (
        "📊 **آمار ربات مؤسسه هنری بهادر فیلم:**\n\n"
        f"👥 کل بازدیدها: {stats_data['total_visits']}\n"
        f"👤 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🛒 سفارش‌های ثبت شده: {stats_data['orders_count']}\n"
        f"✉️ پیام‌های دریافتی مدیریت: {stats_data['messages_count']}"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# === مدیریت کلیک دکمه‌های شیشه‌ای (Callback Queries) ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    
    if data == "back_to_menu":
        welcome_text = "🎬 به منوی اصلی موسسه هنری بهادر فیلم خوش آمدید.\nلطفاً بخش مورد نظر را انتخاب کنید:"
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
        bot.send_photo(chat_id, get_rotational_photo(), caption=welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        
    elif data == "portfolio":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📺 سریال‌ها و فیلم‌های داستانی", callback_data="port_series"),
            types.InlineKeyboardButton("🎥 مستندهای تلویزیونی و بین‌المللی", callback_data="port_docs"),
            types.InlineKeyboardButton("⛽ پروژه ملی و کتاب مرجع گاز", callback_data="port_gas"),
            types.InlineKeyboardButton("🎨 انیمیشن‌های آموزشی و طنز", callback_data="port_anim"),
            types.InlineKeyboardButton("🏆 جوایز و لوح‌های سپاس", callback_data="port_awards"),
            types.InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"),
            types.InlineKeyboardButton("📸 اینستاگرام", url="https://instagram.com"),
            types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")
        ]
        text = "📁 **بخش نمونه‌کارها و رزومه تصویری علی بهادر**\n\nلطفاً حوزه مورد نظر خود را برای مشاهده آثار همراه با پوستر و تصویر انتخاب کنید:"
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
            
    elif data == "port_series":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("(۱۳۷۲) بهترین تابستان من", callback_data="work_tabestan"),
            types.InlineKeyboardButton("(۱۳۸۰-۱۳۷۹) عشق سال‌های جنگ", callback_data="work_eshgh"),
            types.InlineKeyboardButton("(۱۳۸۸) شب هزار و یکم", callback_data="work_shab"),
            types.InlineKeyboardButton("(۱۳۹۱) قدم زدن در بهشت", callback_data="work_ghadam"),
            types.InlineKeyboardButton("(۱۳۹۳) ارثیه پرماجرا", callback_data="work_ershieh"),
            types.InlineKeyboardButton("(۱۳۹۳) شاهزاده و گدا", callback_data="work_shahzadeh"),
            types.InlineKeyboardButton("(۱۴۰۱) مشتری‌مداری", callback_data="work_moshtari"),
            types.InlineKeyboardButton("(۱۳۹۷) برکت", callback_data="work_barakat"),
            types.InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")
        ]
        text = "📺 **سریال‌های تلویزیونی و فیلم‌های داستانی:**\nلطفاً اثر مورد نظر خود را برای مشاهده پوستر و جزئیات انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "port_docs":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("مستند «زندگی»", callback_data="work_zendegi"),
            types.InlineKeyboardButton("(۲۰۱۵) مستند کنگره جهانی گاز پاریس", callback_data="work_paris"),
            types.InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")
        ]
        text = "🎥 **مستندهای تلویزیونی و بین‌المللی:**\nلطفاً مستند مورد نظر خود را انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "port_gas":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش", callback_data="work_gas_book"),
            types.InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")
        ]
        text = "⛽ **پروژه‌های ملی نفت و گاز و کتاب مرجع:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "port_anim":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("انیمیشن آموزشی «اسرافی و انصافی»", callback_data="work_esrafi"),
            types.InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")
        ]
        text = "🎨 **انیمیشن‌های آموزشی و طنز:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "port_awards":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd"),
            types.InlineKeyboardButton("لوح‌ها و تندیس‌های تقدیر ویژه", callback_data="award_tandis"),
            types.InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")
        ]
        text = "🏆 **افتخارات، جوایز و لوح‌های سپاس:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data in ["work_tabestan", "work_eshgh", "work_shab", "work_ghadam", "work_ershieh", "work_shahzadeh", "work_moshtari", "work_barakat", "work_gas_book", "work_paris", "work_zendegi", "work_esrafi", "award_roshd", "award_tandis"]:
        mapping = {
            "work_tabestan": ("work_1", "⭐ **بهترین تابستان من**\n\nکارگردانی سریال طنز دفاع مقدس؛ پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش.", "port_series"),
            "work_eshgh": ("work_3", "❤️ **عشق سال‌های جنگ**\n\nکارگردانی و تهیه‌کنندگی سریال با موضوع دفاع مقدس و درام اجتماعی.", "port_series"),
            "work_shab": ("work_13", "🌙 **شب هزار و یکم**\n\nکارگردانی سریال تلویزیونی با حضور بازیگران برجسته (محصول شبکه اول سیما).", "port_series"),
            "work_ghadam": ("work_4", "🌿 **قدم زدن در بهشت**\n\nکارگردانی تله‌فیلم با ساختار سینمایی و نوآورانه.", "port_series"),
            "work_ershieh": ("work_5", "💼 **ارثیه پرماجرا**\n\nتهیه‌کنندگی فیلم سینمایی ویدیویی پرمخاطب با حضور بازیگران سرشناس.", "port_series"),
            "work_shahzadeh": ("work_6", "👑 **شاهزاده و گدا (۱۳۹۳)**\n\nمحصول موسسه هنری بهادر فیلم به تهیه‌کنندگی علی بهادر.", "port_series"),
            "work_moshtari": ("work_8", "🤝 **مشتری‌مداری (۱۴۰۱)**\n\nسریال آموزشی ۳۰ قسمتی به تهیه‌کنندگی و کارگردانی علی بهادر.", "port_series"),
            "work_barakat": ("work_12", "🌾 **برکت (۱۳۹۷)**\n\nتهیه‌کنندگی و کارگردانی مینی‌سریال تولید شده در بنیاد برکت.", "port_series"),
            "work_gas_book": ("work_11", "📖 **کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش**\n\n۱۰۱۸ صفحه، تاریخ شفاهی ۵۰ ساله شرکت ملی گاز ایران.", "port_gas"),
            "work_paris": ("work_14", "🌍 **مستند کنگره جهانی گاز پاریس (۲۰۱۵)**\n\nمستند تخصصی، صنعتی و بین‌المللی.", "port_docs"),
            "work_zendegi": ("work_2", "🏆 **مستند «زندگی»**\n\nبرنده جوایز متعدد از جشنواره‌های معتبر ملی (جشنواره رشد و دفاع مقدس).", "port_docs"),
            "work_esrafi": ("work_7", "💡 **انیمیشن آموزشی «اسرافی و انصافی»**\n\nمجموعه ۳۰ قسمتی طنز با محوریت ایمنی گاز شهری و مشاوره شخصیت حکیمانه انصافی.", "port_anim"),
            "award_roshd": ("award_15", "🎖 **لوح تقدیر جشنواره بین‌المللی فیلم رشد و جشنواره دفاع مقدس**", "port_awards"),
            "award_tandis": ("award_16", "🏆 **تندیس‌ها و لوح‌های سپاس و تقدیر ویژه مدیران ارشد**", "port_awards")
        }
        photo_key, caption, back_target = mapping[data]
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data=back_target))
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
        bot.send_photo(chat_id, PHOTO_IDS[photo_key], caption=caption, reply_markup=kb, parse_mode="Markdown")
        
    elif data == "interviews":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("مصاحبه روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", callback_data="view_ettelaat_img"),
            types.InlineKeyboardButton("مصاحبه هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)", callback_data="view_sedavasima_img"),
            types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")
        )
        text = "📰 **بخش مصاحبه‌ها و پوشش رسانه‌ای:**\nبرای مشاهده تصاویر و جزئیات مصاحبه‌های علی بهادر روی گزینه‌های زیر کلیک کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "view_ettelaat_img":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews"))
        caption_text = (
            "📰 **مصاحبه با روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)**\n\n"
            "عنوان: «سینمای مستند به مدیرانی جسور نیاز دارد» (گفتگو با نژلا پیکانیان)\n\n"
            "[مشاهده آنلاین در سایت اطلاعات](https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF)"
        )
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
        try:
            bot.send_photo(chat_id, "https://www.ettelaat.com/files/fa/news/1405/5/20/161537_485.jpg", caption=caption_text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, caption_text, reply_markup=markup, parse_mode="Markdown")
            
    elif data == "view_sedavasima_img":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews"))
        caption_text = (
            "📰 **مصاحبه با هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)**\n\n"
            "عنوان: «تصویر مقاومت در آیینه رسانه؛ نیم قرن تلاش برای هنر و وطن» (گفتگو با عبدالرحمن شلیبیان)"
        )
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, caption_text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "about":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu"))
        about_text = (
            "ℹ️ **درباره علی بهادر و مؤسسه هنری بهادر فیلم**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما\n"
            "• **سوابق اجرایی:** مدیر گروه حماسه و دفاع شبکه یک سیما، مدیر واحد دوبلاژ شبکه یک، شروع فعالیت حرفه‌ای از سال ۱۳۶۰ در واحد خبر همدان، بیش از ۱۸ ماه حضور در پوشش رسانه‌ای دوران دفاع مقدس (صداوسیما)\n"
            "• **مدیرعامل:** مؤسسه فرهنگی و هنری بهادر فیلم\n\n"
            "📋 **رزومه تفکیک‌شده و سوابق هنری:**\n\n"
            "🎬 **بخش آثار نمایشی و سریال‌ها:**\n"
            "• کارگردانی سریال «بهترین تابستان من» (۱۳۷۵ - شبکه ۱)\n"
            "• کارگردانی سریال «عشق سال‌های جنگ» (۱۳۸۰ - شبکه ۳)\n"
            "• کارگردانی سریال «شب هزار و یکم» (۱۳۸۷-۱۳۸۸ - شبکه ۱)\n"
            "• کارگردانی فیلم‌های تلویزیونی (تله‌فیلم): «قدم زدن در بهشت»، «ارثیه پرماجرا»، «شاهزاده و گدا»\n"
            "• کارگردانی مجموعه‌ها و مینی‌‌سریال‌ها: «برکت»، «مشتری‌مداری»\n\n"
            "🎥 **بخش مستندها و پروژه‌های ملی:**\n"
            "• کارگردانی مستند «زندگی» (۱۳۷۰ - برنده جوایز جشنواره‌های دفاع مقدس، رشد و همدان)\n"
            "• تولید و کارگردانی مستندهای برون‌مرزی «نوروز در ازبکستان» (برنده ۲ جایزه از جشنواره‌های برون‌مرزی IRIB) و «بدخشان بام جهان» (تاجیکستان)\n"
            "• تألیف و تدوین کتاب مرجع و ۱۰۱۸ صفحه‌ای «گاز؛ انرژی پاک با نیم قرن تلاش» همراه با تولید مجموعه مستند ۶۳ قسمتی (۱۳۹۵)\n\n"
            "هدف ما به تصویر کشیدن فرهنگ، هنر و تاریخ پربار ایران عزیز است."
        )
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, about_text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "digital_card":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"),
            types.InlineKeyboardButton("📸 اینستاگرام موسسه", url="https://instagram.com"),
            types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")
        )
        card_text = (
            "💳 **کارت ویزیت دیجیتال مؤسسه هنری بهادر فیلم**\n\n"
            "👤 **مدیرعامل:** علی بهادر\n"
            "🎯 **تخصص:** کارگردانی، تهیه‌کنندگی و نویسندگی\n"
            "🌐 **وب‌سایت:** alibahador.ir"
        )
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, card_text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "services":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu"))
        services_text = (
            "📋 **خدمات و تعرفه‌ها:**\n\n"
            "۱. ساخت سریال‌های داستانی و تلویزیونی\n"
            "۲. تولید مستندهای فاخر صنعتی و تاریخی\n"
            "۳. ساخت تیزرهای تبلیغاتی و آگهی‌های بازرگانی\n"
            "۴. تولید انیمیشن‌های آموزشی و طنز"
        )
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, services_text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "faq":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu"))
        faq_text = (
            "❓ **پرسش‌های متداول (FAQ):**\n\n"
            "• **چگونه پروژه ثبت کنیم؟** از طریق دکمه «ثبت سفارش و درخواست مشاوره» در منوی اصلی.\n"
            "• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه «ارسال پیام به مدیریت»."
        )
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, faq_text, reply_markup=markup, parse_mode="Markdown")
        
    elif data == "start_order":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("سریال و فیلم داستانی", callback_data="p_series"),
            types.InlineKeyboardButton("ساخت مستند", callback_data="p_documentary"),
            types.InlineKeyboardButton("تیزر تبلیغاتی", callback_data="p_teaser"),
            types.InlineKeyboardButton("انیمیشن", callback_data="p_anim"),
            types.InlineKeyboardButton("انصراف", callback_data="back_to_menu")
        )
        text = "🛒 **ثبت سفارش جدید - مرحله ۱ از ۳**\n\nلطفاً نوع پروژه مورد نظر خود را انتخاب کنید:"
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
    elif data in ["p_series", "p_documentary", "p_teaser", "p_anim"]:
        mapping = {
            "p_series": "سریال یا فیلم داستانی",
            "p_documentary": "مستند",
            "p_teaser": "تیزر تبلیغاتی",
            "p_anim": "انیمیشن"
        }
        proj_name = mapping[data]
        msg = bot.edit_message_text(f"🛒 نوع پروژه انتخابی: **{proj_name}**\n\nلطفاً **نام و نام خانوادگی خود را ارسال کنید:**", chat_id, message_id, parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_user_name, proj_name)
        
    elif data == "contact_admin":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("انصراف", callback_data="back_to_menu"))
        msg = bot.edit_message_text("✉️ **ارسال پیام به مدیریت**\n\nلطفاً پیام، نظر یا درخواست خود را بنویسید تا برای مدیریت ارسال شود:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_admin_message)

def process_user_name(message, proj_name):
    chat_id = message.chat.id
    user_name = message.text
    msg = bot.send_message(chat_id, f"👤 نام ثبت شد: {user_name}\n\nلطفاً **شماره تماس خود را ارسال کنید** تا همکاران ما با شما تماس بگیرند:")
    bot.register_next_step_handler(msg, process_user_phone, proj_name, user_name)

def process_user_phone(message, proj_name, user_name):
    chat_id = message.chat.id
    user_phone = message.text
    stats_data["orders_count"] += 1
    user = message.from_user
    
    summary = (
        "✅ **سفارش شما با موفقیت ثبت شد**\n\n"
        f"🔹 نوع پروژه: {proj_name}\n"
        f"👤 نام: {user_name}\n"
        f"📞 شماره تماس: {user_phone}\n\n"
        "کارشناسان مؤسسه هنری بهادر فیلم به زودی با شما تماس خواهند گرفت."
    )
    
    admin_order_notification = (
        "🚨 **سفارش جدید ثبت شد!**\n\n"
        f"🔹 نوع پروژه: {proj_name}\n"
        f"👤 نام کاربر: {user_name}\n"
        f"📞 شماره تماس: {user_phone}\n"
        f"🌐 آیدی تلگرام: @{user.username if user.username else 'ندارد'} (ID: {user.id})"
    )
    
    try:
        bot.send_message(ADMIN_CHAT_ID, admin_order_notification, parse_mode="Markdown")
    except Exception:
        pass
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu"))
    bot.send_message(chat_id, summary, reply_markup=markup, parse_mode="Markdown")

def process_admin_message(message):
    chat_id = message.chat.id
    user_msg = message.text
    stats_data["messages_count"] += 1
    user = message.from_user
    
    forward_text = (
        "✉️ **پیام جدید از مخاطب ربات:**\n\n"
        f"👤 فرستنده: {user.full_name}\n"
        f"🔗 نام کاربری: @{user.username if user.username else 'ندارد'} (ID: {user.id})\n\n"
        f"💬 متن پیام:\n{user_msg}"
    )
    
    try:
        bot.send_message(ADMIN_CHAT_ID, forward_text, parse_mode="Markdown")
    except Exception:
        pass
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu"))
    bot.send_message(chat_id, "✅ پیام شما با موفقیت به مدیریت مؤسسه هنری بهادر فیلم ارسال شد.", reply_markup=markup)

if __name__ == '__main__':
    # اجرای Flask در یک ترد (Thread) جداگانه برای پاسخ به مانیتورینگ Render و UptimeRobot
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    # تنظیم خودکار وب‌هوک برای اتصال به تلگرام
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print(f"Webhook set successfully to {RENDER_URL}/{TOKEN}")
        
    print("Bahador Film Bot with pyTelegramBotAPI & Webhook is running successfully...")
    # چون از وب‌هوک استفاده می‌کنیم، نیازی به polling نیست و سرور Flask درخواست‌ها را دریافت می‌کند
    import time
    while True:
        time.sleep(1)
