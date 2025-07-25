from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import random
from datetime import timedelta
from django.utils import timezone
from accounts.models import LoginCode
from asgiref.sync import sync_to_async
import logging

from .config import PHONE, WAITING_FOR_CODE

logger = logging.getLogger(__name__)


@sync_to_async
def save_login_code(phone, code):

    try:
        login_code, created = LoginCode.objects.update_or_create(
            phone=phone,
            defaults={
                'code': code,
                'expires_at': timezone.now() + timedelta(days=3),  # 3 kunlik muddat
                'created_at': timezone.now(),
                'is_used': False  # Yangi kod yaratilganda ishlatilmagan deb belgilash
            }
        )
        return login_code, created
    except Exception as e:
        logger.error(f"Database xatolik save_login_code: {e}")
        raise


@sync_to_async
def get_user_code_info(phone):
    try:
        login_code = LoginCode.objects.filter(phone=phone).first()
        if login_code:
            return {
                'exists': True,
                'code': login_code.code,
                'expires_at': login_code.expires_at,
                'is_expired': login_code.expires_at < timezone.now() if login_code.expires_at else True,
                'is_used': login_code.is_used
            }
        return {'exists': False}
    except Exception as e:
        logger.error(f"Database xatolik get_user_code_info: {e}")
        return {'exists': False}


@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        # LoginCode modelida telegram_id field'i bo'lishi kerak
        login_code = LoginCode.objects.filter(telegram_id=telegram_id).first()
        return login_code.phone if login_code else None
    except Exception as e:
        logger.error(f"Database xatolik get_user_by_telegram_id: {e}")
        return None


@sync_to_async
def update_telegram_id(phone, telegram_id):
    try:
        LoginCode.objects.filter(phone=phone).update(telegram_id=telegram_id)
        return True
    except Exception as e:
        logger.error(f"Database xatolik update_telegram_id: {e}")
        return False


@sync_to_async
def mark_code_as_used(phone, code):

    try:
        LoginCode.objects.filter(
            phone=phone,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        return True
    except Exception as e:
        logger.error(f"Database xatolik mark_code_as_used: {e}")
        return False


def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard():
    return ReplyKeyboardRemove()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start komandasi handler'i. Yangi foydalanuvchilarni ro'yxatdan o'tkazishni boshlaydi.
    :param update: Telegram Update obyekti.
    :param context: Telegram ContextTypes.DEFAULT_TYPE obyekti.
    """
    try:
        telegram_id = update.effective_user.id
        username = update.effective_user.username or "Noma'lum"

        existing_phone = await get_user_by_telegram_id(telegram_id)

        if existing_phone:
            # Mavjud foydalanuvchi - login komandasi bilan yo'naltirish
            await update.message.reply_text(
                f"👋 Assalomu alaykum, <b>{username}</b>!\n\n"  # Username qalin (bold) qilib chiqarildi
                f"Siz avval ro'yxatdan o'tgansiz (📱 {existing_phone}).\n\n"
                "Yangi kod olish uchun /login buyrug'ini ishlating.",
                parse_mode="HTML",  # HTML formatlashni yoqish
                reply_markup=remove_keyboard()
            )
            return ConversationHandler.END
        else:
            # Yangi foydalanuvchi
            await update.message.reply_text(
                f"👋 Assalomu alaykum, <b>{username}</b>!\n\n"  
                "Botdan foydalanish uchun telefon raqamingizni yuboring:",
                parse_mode="HTML",  # HTML formatlashni yoqish
                reply_markup=get_contact_keyboard()
            )
            return PHONE

    except Exception as e:
        logger.exception("start_command da xatolik:")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=remove_keyboard()
        )
        return ConversationHandler.END


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Login komandasi handler'i. Mavjud foydalanuvchilar uchun kodni yangilaydi yoki ko'rsatadi.
    :param update: Telegram Update obyekti.
    :param context: Telegram ContextTypes.DEFAULT_TYPE obyekti.
    """
    try:
        telegram_id = update.effective_user.id
        username = update.effective_user.username or "Noma'lum"

        # Foydalanuvchi avval ro'yxatdan o'tganmi tekshirish
        existing_phone = await get_user_by_telegram_id(telegram_id)

        if not existing_phone:
            # Yangi foydalanuvchi - start bilan yo'naltirish
            await update.message.reply_text(
                f"👋 Assalomu alaykum, <b>{username}</b>!\n\n" 
                "Siz hali ro'yxatdan o'tmagansiz.\n\n"
                "Ro'yxatdan o'tish uchun /start buyrug'ini ishlating.",
                parse_mode="HTML",  # HTML formatlashni yoqish
                reply_markup=remove_keyboard()
            )
            return ConversationHandler.END

        # Mavjud kod ma'lumotlarini tekshirish
        code_info = await get_user_code_info(existing_phone)

        if code_info['exists'] and not code_info['is_expired'] and not code_info['is_used']:
            # Kod hali amal qilmoqda va ishlatilmagan
            remaining_time = code_info['expires_at'] - timezone.now()
            days = remaining_time.days
            hours = remaining_time.seconds // 3600

            await update.message.reply_text(
                f"ℹ️ Sizning kodingiz hali amal qilmoqda!\n\n"
                f"📱 Telefon: {existing_phone}\n" 
                f"🔐 Kod: `{code_info['code']}`\n"
                f"⏰ Muddat: {days} kun {hours} soat qoldi\n\n"
                "Bu kodni saytga kiriting.",
                parse_mode="Markdown",
                reply_markup=remove_keyboard()
            )
        else:
            # Yangi kod yaratish (agar mavjud bo'lmasa, muddati tugagan bo'lsa yoki ishlatilgan bo'lsa)
            await generate_new_code(update, existing_phone)

        return ConversationHandler.END

    except Exception as e:
        logger.exception("login_command da xatolik:")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=remove_keyboard()
        )
        return ConversationHandler.END


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        contact = update.message.contact
        telegram_id = update.effective_user.id

        if not contact:
            await update.message.reply_text(
                "❌ Kontakt topilmadi. Iltimos, pastdagi tugma orqali telefon raqamni yuboring.",
                reply_markup=get_contact_keyboard()
            )
            return PHONE

        if contact.user_id != update.effective_user.id:
            await update.message.reply_text(
                "❌ Iltimos, o'zingizning telefon raqamingizni yuboring!",
                reply_markup=get_contact_keyboard()
            )
            return PHONE

        phone = contact.phone_number

        if not phone or len(phone) < 10:
            await update.message.reply_text(
                "❌ Telefon raqami noto'g'ri formatda. Qaytadan urinib ko'ring.",
                reply_markup=get_contact_keyboard()
            )
            return PHONE

        await update_telegram_id(phone, telegram_id)

        await generate_new_code(update, phone)

        return ConversationHandler.END

    except Exception as e:
        logger.exception("handle_contact da xatolik:")
        await update.message.reply_text(
            "❌ Kontakt qayta ishlashda xatolik yuz berdi. Qaytadan urinib ko'ring.",
            reply_markup=remove_keyboard()
        )
        return ConversationHandler.END


async def generate_new_code(update: Update, phone: str):
    """
    Yangi 5 xonali kod yaratish va foydalanuvchiga yuborish.
    :param update: Telegram Update obyekti.
    :param phone: Foydalanuvchi telefon raqami.
    """
    try:
        code = str(random.randint(10000, 99999))

        login_code, created = await save_login_code(phone, code)

        if created:
            status_text = "🆕 Yangi kod yaratildi"
        else:
            status_text = "🔄 Kod yangilandi"

        expires_at = login_code.expires_at

        await update.message.reply_text(
            f"✅ {status_text}!\n\n"
            f"📱 Telefon: {phone}\n"  # Oddiy matn
            f"🔐 Sizning 5 xonali kodingiz: `{code}`\n\n"  # Markdown kod bloki
            f"📅 Amal qilish muddati: 3 kun\n"
            f"📆 Tugash sanasi: {expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            "Bu kodni saytga kiriting yoki botga yuboring. Kod 3 kun davomida amal qiladi.",
            parse_mode="Markdown",  # Markdown formatlashni yoqish
            reply_markup=remove_keyboard()
        )

    except Exception as e:
        logger.exception("generate_new_code da xatolik:")
        await update.message.reply_text(
            "❌ Kod yaratishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=remove_keyboard()
        )


async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanuvchi tomonidan yuborilgan 5 xonali kodni tekshirish.
    :param update: Telegram Update obyekti.
    :param context: Telegram ContextTypes.DEFAULT_TYPE obyekti.
    """
    try:
        text = update.message.text.strip()
        telegram_id = update.effective_user.id

        if not (text.isdigit() and len(text) == 5):
            await update.message.reply_text(
                "❓ Bu buyruqni tushunmadim.\n\n"
                "5 xonali kodni yuborish uchun faqat raqamlarni kiriting.\n"
                "Yordam uchun /help ni bosing.",
                reply_markup=remove_keyboard()
            )
            return

        # Telegram ID orqali telefon topish
        existing_phone = await get_user_by_telegram_id(telegram_id)

        if not existing_phone:
            await update.message.reply_text(
                "❌ Sizning telefon raqamingiz topilmadi.\n\n"
                "Iltimos, avval /start buyrug'i bilan ro'yxatdan o'ting.",
                reply_markup=remove_keyboard()
            )
            return

        code_info = await get_user_code_info(existing_phone)

        if not code_info['exists']:
            await update.message.reply_text(
                "❌ Sizning faol kodingiz topilmadi.\n\n"
                "Yangi kod olish uchun /login buyrug'ini ishlating.",
                reply_markup=remove_keyboard()
            )
            return

        if code_info['is_expired']:
            await update.message.reply_text(
                "⌛ Sizning kodingiz muddati tugagan.\n\n"
                "Yangi kod olish uchun /login buyrug'ini ishlating.",
                reply_markup=remove_keyboard()
            )
            return

        if code_info['is_used']:
            await update.message.reply_text(
                "⚠️ Bu kod allaqachon ishlatilgan.\n\n"
                "Yangi kod olish uchun /login buyrug'ini ishlating.",
                reply_markup=remove_keyboard()
            )
            return

        # Kiritilgan kod to'g'rimi tekshirish
        if text == code_info['code']:
            # Kodni ishlatilgan deb belgilash
            await mark_code_as_used(existing_phone, text)

            await update.message.reply_text(
                "✅ Kod to'g'ri! Muvaffaqiyatli tasdiqlandi.\n\n"
                f"📱 Telefon: {existing_phone}\n"  # Oddiy matn
                f"🔐 Kod: `{text}`\n"  # Markdown kod bloki
                f"✅ Holat: Tasdiqlangan\n"
                f"📅 Tasdiqlangan vaqt: {timezone.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                "Endi saytga kirishingiz mumkin!",
                parse_mode="Markdown",  # Markdown formatlashni yoqish
                reply_markup=remove_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ Kod noto'g'ri!\n\n"
                f"To'g'ri kod: `{code_info['code']}`\n"  # Markdown kod bloki
                f"Siz kiritgan: `{text}`\n\n"  # Markdown kod bloki
                "Iltimos, to'g'ri kodni kiriting yoki /login bilan yangi kod oling.",
                parse_mode="Markdown",  # Markdown formatlashni yoqish
                reply_markup=remove_keyboard()
            )

    except Exception as e:
        logger.exception("handle_code_message da xatolik:")
        await update.message.reply_text(
            "❌ Kod tekshirishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=remove_keyboard()
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Yordam komandasi handler'i. Bot buyruqlari va ishlash tartibi haqida ma'lumot beradi.
    :param update: Telegram Update obyekti.
    :param context: Telegram ContextTypes.DEFAULT_TYPE obyekti.
    """
    help_text = """
🤖 <b>Bot buyruqlari:</b>

/start - Yangi foydalanuvchilar uchun ro'yxatdan o'tish
/login - Mavjud foydalanuvchilar uchun kod yangilash
/help - Bu yordam matnini ko'rsatish
/cancel - Joriy jarayonni to'xtatish

<b>❓ Qanday ishlaydi:</b>

1️⃣ Yangi foydalanuvchi: /start → kontakt yuborish → kod olish
2️⃣ Mavjud foydalanuvchi: /login → yangi kod olish
3️⃣ Kod 3 kun davomida amal qiladi

<b>🆘 Yordam kerakmi?</b>
Muammo bo'lsa, /start yoki /login dan foydalaning.
    """

    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=remove_keyboard()
    )


async def cancel_command(update: Update):

    await update.message.reply_text(
        "❌ Jarayon bekor qilindi.\n\n"
        "Qaytadan boshlash uchun /start yoki /login dan foydalaning.",
        reply_markup=remove_keyboard()
    )
    return ConversationHandler.END


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""

    # Agar 5 xonali kod yuborilgan bo'lsa, uni handle_code_message ga yo'naltirish
    if text.isdigit() and len(text) == 5:
        await handle_code_message(update, context)
        return

    await update.message.reply_text(
        "❓ Bu buyruqni tushunmadim.\n\n"
        "Yordam uchun /help ni bosing yoki:\n"
        "• Yangi foydalanuvchi: /start\n"
        "• Mavjud foydalanuvchi: /login\n"
        "• 5 xonali kodni tekshirish uchun raqamlarni yuboring",
        reply_markup=remove_keyboard()
    )


def get_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("login", login_command),
        ],
        states={
            PHONE: [
                MessageHandler(filters.CONTACT, handle_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message),
            ],

        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("help", help_command),
            # Barcha boshqa xabarlarni unknown_message ga yo'naltirish
            MessageHandler(filters.ALL, unknown_message),
        ],
        per_chat=True,
        per_user=True,
    )
