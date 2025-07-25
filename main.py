import logging
import os
import django

# Django sozlamalarini yuklash
# 'config.settings' bu sizning loyihangizning settings.py fayliga yo'l.
# Agar sizning settings.py faylingiz boshqa joyda bo'lsa, shu yo'lni to'g'irlang.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Django muhiti sozlangandan so'ng, Telegram kutubxonalarini import qilish
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, BotCommand  # BotCommand ni import qildik

# config.py faylidan bot tokenini import qilish
from telegramBot.config import TELEGRAM_TOKEN

# login.py faylidan handler funksiyalarini import qilish
from telegramBot.login import (
    get_conversation_handler,
    help_command,
    unknown_message,
)

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def setup_handlers(application: Application):
    """
    Application obyektiga barcha handler'larni qo'shish.
    :param application: Telegram.ext.Application obyekti.
    """
    try:
        # Asosiy conversation handler
        application.add_handler(get_conversation_handler())

        # Mustaqil buyruqlar (agar conversation ichida bo'lmasa ham ishlaydi)
        application.add_handler(CommandHandler("help", help_command))

        # Noma'lum xabarlar uchun fallback (oxirgi bo'lishi kerak)
        application.add_handler(MessageHandler(filters.ALL, unknown_message))

        logger.info("Bot handler'lari muvaffaqiyatli sozlandi.")

    except Exception as e:
        logger.error(f"Handler'larni sozlashda xatolik: {e}")
        raise


async def set_bot_commands(application: Application):
    """
    Botning menyu buyruqlarini Telegramga o'rnatish.
    """
    commands = [
        BotCommand("start", "Yangi foydalanuvchilar uchun ro'yxatdan o'tish"),
        BotCommand("login", "Mavjud foydalanuvchilar uchun kod yangilash"),
        BotCommand("help", "Bot imkoniyatlari haqida ma'lumot"),
        BotCommand("cancel", "Joriy jarayonni to'xtatish"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot buyruqlari muvaffaqiyatli o'rnatildi.")


async def post_init(application: Application):
    """
    Bot ishga tushganda chaqiriladi.
    :param application: Telegram.ext.Application obyekti.
    """
    logger.info("Telegram bot muvaffaqiyatli ishga tushdi!")
    await set_bot_commands(application)  # Bot buyruqlarini o'rnatish
    # Bu yerda bot ishga tushganda bajarilishi kerak bo'lgan boshqa amallarni qo'shishingiz mumkin
    # Masalan, bot haqida ma'lumot olish: await application.bot.get_me()


async def post_shutdown(application: Application):
    """
    Bot to'xtaganda chaqiriladi.
    :param application: Telegram.ext.Application obyekti.
    """
    logger.info("Telegram bot to'xtatildi!")
    # Bu yerda bot to'xtaganda bajarilishi kerak bo'lgan tozalash amallarini qo'shishingiz mumkin


def create_bot_application(token: str) -> Application:
    """
    Telegram bot application obyektini yaratish.
    :param token: Botning API tokeni.
    :return: Telegram.ext.Application obyekti.
    """
    try:
        # Application yaratish
        application = Application.builder().token(token).build()

        # Handler'larni sozlash
        setup_handlers(application)

        # Post init va shutdown handler'lar
        application.post_init = post_init
        application.post_shutdown = post_shutdown

        return application

    except Exception as e:
        logger.error(f"Bot yaratishda xatolik: {e}")
        raise


if __name__ == "__main__":
    # Bot application yaratish
    app = create_bot_application(TELEGRAM_TOKEN)

    # Botni ishga tushirish (polling rejimida)
    logger.info("Bot ishga tushirilmoqda...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)