import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Загружаем .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден! Создай файл .env и добавь туда токен бота."
    )


# Состояния
SINGLE_CALCULATOR = 1
MULTI_CALCULATOR = 2


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def to_binary(number: int) -> str:
    """Переводит число в 8-битный бинарный формат."""
    return format(number, "08b")


def validate_number(value: str):
    """
    Проверяет число:
    - только цифры
    - от 0 до 255
    """
    if not value.isdigit():
        return None

    number = int(value)

    if number < 0 or number > 255:
        return None

    return number


def validate_ip(ip: str):
    """
    Проверяет IP из трёх октетов.

    Например:
    255.0.255
    """
    parts = ip.split(".")

    if len(parts) != 3:
        return None

    numbers = []

    for part in parts:
        number = validate_number(part)

        if number is None:
            return None

        numbers.append(number)

    return numbers


def main_menu():
    """Главное меню бота."""

    keyboard = [
        [
            InlineKeyboardButton(
                "🧮 Одиночный калькулятор",
                callback_data="single"
            )
        ],
        [
            InlineKeyboardButton(
                "🔢 Множественный калькулятор",
                callback_data="multiple"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def back_menu():
    """Кнопка возврата в меню."""

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ Главное меню",
                callback_data="menu"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я IP Binary Calculator.\n\n"
        "Я умею выполнять побитовый AND "
        "для чисел и IP-адресов.\n\n"
        "Выбери калькулятор:",
        reply_markup=main_menu()
    )

    return ConversationHandler.END


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "🏠 Главное меню\n\n"
        "Выбери калькулятор:",
        reply_markup=main_menu()
    )

    return ConversationHandler.END


# =========================
# ОДИНОЧНЫЙ КАЛЬКУЛЯТОР
# =========================

async def single_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "🧮 ОДИНОЧНЫЙ КАЛЬКУЛЯТОР\n\n"
        "Введи два числа через пробел.\n\n"
        "Каждое число должно быть от 0 до 255.\n\n"
        "Например:\n"
        "255 0"
    )

    return SINGLE_CALCULATOR


async def single_calculate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    parts = text.split()

    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Нужно ввести ровно два числа.\n\n"
            "Например:\n"
            "255 0"
        )
        return SINGLE_CALCULATOR

    first = validate_number(parts[0])
    second = validate_number(parts[1])

    if first is None or second is None:
        await update.message.reply_text(
            "❌ Неверное значение!\n\n"
            "Оба числа должны быть от 0 до 255.\n\n"
            "Например:\n"
            "255 0"
        )
        return SINGLE_CALCULATOR

    # Бинарные значения
    first_binary = to_binary(first)
    second_binary = to_binary(second)

    # Побитовый AND
    result = first & second
    result_binary = to_binary(result)

    await update.message.reply_text(
        "🧮 РЕЗУЛЬТАТ\n\n"

        f"1️⃣ Число:\n"
        f"{first}\n"
        f"↓\n"
        f"{first_binary}\n\n"

        f"2️⃣ Число:\n"
        f"{second}\n"
        f"↓\n"
        f"{second_binary}\n\n"

        "🔧 AND:\n"
        f"{first_binary}\n"
        f"{second_binary}\n"
        "────────────────\n"
        f"{result_binary}\n\n"

        "📌 Обычный результат:\n"
        f"{first} & {second} = {result}\n\n"

        "💻 Бинарный результат:\n"
        f"{result_binary}",

        reply_markup=back_menu()
    )

    return ConversationHandler.END


# =========================
# МНОЖЕСТВЕННЫЙ КАЛЬКУЛЯТОР
# =========================

async def multiple_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "🔢 МНОЖЕСТВЕННЫЙ КАЛЬКУЛЯТОР\n\n"

        "Введи два IP по 3 октета.\n\n"

        "Первый — оригинальный IP.\n"
        "Второй — камуфляж.\n\n"

        "Например:\n\n"
        "255.0.255\n"
        "0.255.255\n\n"

        "Можно также написать в одну строку:\n"
        "255.0.255 0.255.255"
    )

    return MULTI_CALCULATOR


async def multiple_calculate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    # Поддержка двух вариантов:
    #
    # 255.0.255
    # 0.255.255
    #
    # или
    #
    # 255.0.255 0.255.255

    parts = text.split()

    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Нужно ввести два IP по 3 октета.\n\n"

            "Например:\n"
            "255.0.255\n"
            "0.255.255"
        )

        return MULTI_CALCULATOR

    original = validate_ip(parts[0])
    camouflage = validate_ip(parts[1])

    if original is None or camouflage is None:

        await update.message.reply_text(
            "❌ Неверный IP!\n\n"

            "Каждый IP должен иметь 3 числа.\n"
            "Каждое число должно быть от 0 до 255.\n\n"

            "Например:\n"
            "255.0.255\n"
            "0.255.255"
        )

        return MULTI_CALCULATOR

    # =========================
    # ПЕРЕВОД В БИНАРНЫЙ ВИД
    # =========================

    original_binary = [
        to_binary(number)
        for number in original
    ]

    camouflage_binary = [
        to_binary(number)
        for number in camouflage
    ]

    # =========================
    # AND КАЖДОГО ОКТЕТА
    # =========================

    results = []

    for i in range(3):
        result = original[i] & camouflage[i]
        results.append(result)

    # Бинарные результаты
    results_binary = [
        to_binary(number)
        for number in results
    ]

    # =========================
    # СОБИРАЕМ IP
    # =========================

    original_ip = ".".join(
        str(number)
        for number in original
    )

    camouflage_ip = ".".join(
        str(number)
        for number in camouflage
    )

    result_ip = ".".join(
        str(number)
        for number in results
    )

    original_binary_ip = ".".join(
        original_binary
    )

    camouflage_binary_ip = ".".join(
        camouflage_binary
    )

    result_binary_ip = ".".join(
        results_binary
    )

    # =========================
    # ОТВЕТ
    # =========================

    await update.message.reply_text(
        "🔢 РЕЗУЛЬТАТ\n\n"

        "🟦 Оригинальный IP:\n"
        f"{original_ip}\n"
        f"{original_binary_ip}\n\n"

        "🟨 Камуфляж:\n"
        f"{camouflage_ip}\n"
        f"{camouflage_binary_ip}\n\n"

        "🔧 ПОБИТОВЫЙ AND:\n\n"

        f"{original_binary_ip}\n"
        f"{camouflage_binary_ip}\n"
        "────────────────────────\n"
        f"{result_binary_ip}\n\n"

        "📌 ОБЫЧНЫЙ РЕЗУЛЬТАТ:\n"
        f"{result_ip}\n\n"

        "💻 БИНАРНЫЙ РЕЗУЛЬТАТ:\n"
        f"{result_binary_ip}",

        reply_markup=back_menu()
    )

    return ConversationHandler.END


# =========================
# ОТМЕНА
# =========================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Операция отменена.",
        reply_markup=main_menu()
    )

    return ConversationHandler.END


# =========================
# ЗАПУСК
# =========================

def main():

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    conversation_handler = ConversationHandler(

        entry_points=[
            CallbackQueryHandler(
                single_start,
                pattern="^single$"
            ),

            CallbackQueryHandler(
                multiple_start,
                pattern="^multiple$"
            ),
        ],

        states={

            SINGLE_CALCULATOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    single_calculate
                )
            ],

            MULTI_CALCULATOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    multiple_calculate
                )
            ],
        },

        fallbacks=[
            CommandHandler(
                "start",
                start
            ),

            CommandHandler(
                "cancel",
                cancel
            ),

            CallbackQueryHandler(
                show_menu,
                pattern="^menu$"
            ),
        ],
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        conversation_handler
    )

    # Кнопка "Главное меню"
    application.add_handler(
        CallbackQueryHandler(
            show_menu,
            pattern="^menu$"
        )
    )

    print("🤖 Бот запущен!")

    application.run_polling()


if __name__ == "__main__":
    main()
