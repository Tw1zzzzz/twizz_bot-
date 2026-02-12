from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

WINDOWS_PREMIUM_EMOJI = '<tg-emoji emoji-id="5936226607931854504"></tg-emoji>'
APPLE_PREMIUM_EMOJI = '<tg-emoji emoji-id="5352762486250545420"></tg-emoji>'
WINDOWS_PLATFORM_LABEL = f"{WINDOWS_PREMIUM_EMOJI} Windows"
MACOS_PLATFORM_LABEL = f"{APPLE_PREMIUM_EMOJI} macOS"

def main_menu():
    kb = [
        [KeyboardButton(text="Магазин 🛍️"), KeyboardButton(text="Отзывы 💡")],
        [KeyboardButton(text="Соц.Сети 🌐"), KeyboardButton(text="Поддержка 👩‍💻")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def products_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="ScoutScope", callback_data="prod_scout_scope")
    builder.button(text="PerformanceCoach CRM", callback_data="prod_crm")
    builder.button(text="CIS FINDER BOT", callback_data="prod_cis_bot")
    builder.adjust(1)
    return builder.as_markup()

def scout_scope_menu(has_file=False):
    builder = InlineKeyboardBuilder()
    if has_file:
        builder.button(text="Демоверсия", callback_data="demo_select_scout_scope", style="success")
    builder.button(text="Pro Версия 🌟", callback_data="buy_scout_scope", style="primary")
    builder.button(text="Инструкция 📘", callback_data="scout_scope_instruction")
    builder.button(text="Назад 🔙", callback_data="back_to_shop")
    builder.adjust(1)
    return builder.as_markup()

def scout_scope_instruction_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад к ScoutScope 🔙", callback_data="back_to_scout_scope")
    builder.adjust(1)
    return builder.as_markup()

def scout_scope_pro_plans_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Минимум — 1500 рублей", callback_data="plan_scout_scope_minimum", style="success")
    builder.button(text="Базовый — 3000 рублей", callback_data="plan_scout_scope_basic", style="primary")
    builder.button(text="Стандарт — 5000 рублей", callback_data="plan_scout_scope_standard", style="primary")
    builder.button(text="Премиум — 7000 рублей", callback_data="plan_scout_scope_3m", style="danger")
    builder.button(text="Назад 🔙", callback_data="back_to_scout_scope")
    builder.adjust(1)
    return builder.as_markup()

def crm_menu(has_file=False):
    builder = InlineKeyboardBuilder()
    if has_file:
        builder.button(text="Демоверсия", callback_data="demo_select_crm", style="success")
    builder.button(text="Pro Версия 🌟", callback_data="buy_crm", style="primary")
    builder.button(text="Назад 🔙", callback_data="back_to_shop")
    builder.adjust(1)
    return builder.as_markup()

def cis_bot_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти к боту 🤖", url="https://t.me/Cisfinderofficial_bot")
    builder.button(text="Назад 🔙", callback_data="back_to_shop")
    builder.adjust(1)
    return builder.as_markup()

def file_type_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Приложение", callback_data="file_type_app")
    builder.button(text="🗄️ База данных", callback_data="file_type_db")
    builder.adjust(1)
    return builder.as_markup()

def platform_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text=WINDOWS_PLATFORM_LABEL, callback_data="platform_win")
    builder.button(text=MACOS_PLATFORM_LABEL, callback_data="platform_mac")
    builder.adjust(2)
    return builder.as_markup()

def demo_platform_menu(product_key: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=WINDOWS_PLATFORM_LABEL, callback_data=f"demo_download_{product_key}_win")
    builder.button(text=MACOS_PLATFORM_LABEL, callback_data=f"demo_download_{product_key}_mac")
    back_callback = "back_to_scout_scope" if product_key == "scout_scope" else f"prod_{product_key}"
    builder.button(text="Назад 🔙", callback_data=back_callback)
    builder.adjust(2)
    return builder.as_markup()

def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Загрузить файлы", callback_data="admin_upload")
    builder.button(text="🗑️ Удалить загруженное", callback_data="admin_delete_upload")
    builder.button(text="📊 Просмотр продуктов", callback_data="admin_view_products")
    builder.button(text="📢 Отправить уведомление", callback_data="admin_send_notification")
    builder.button(text="📈 Статистика", callback_data="admin_stats")
    builder.adjust(1)
    return builder.as_markup()

def admin_delete_products_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="ScoutScope", callback_data="admin_del_prod_scout_scope")
    builder.button(text="PerformanceCoach CRM", callback_data="admin_del_prod_crm")
    builder.button(text="CIS FINDER BOT", callback_data="admin_del_prod_cis_bot")
    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def admin_delete_targets_menu(product_key: str, product):
    builder = InlineKeyboardBuilder()

    if product_key in ("scout_scope", "crm"):
        if product["file_id"] or product["version"]:
            builder.button(text="🗑️ Приложение Windows", callback_data="admin_del_target_app_win")
        if product["file_id_mac"] or product["version_mac"]:
            builder.button(text="🗑️ Приложение macOS", callback_data="admin_del_target_app_mac")
        if product["db_file_id"] or product["db_version"]:
            builder.button(text="🗑️ База данных", callback_data="admin_del_target_db")
    else:
        if product["file_id"] or product["version"]:
            builder.button(text="🗑️ Приложение", callback_data="admin_del_target_app_win")

    builder.button(text="🔙 К продуктам", callback_data="admin_delete_back_products")
    builder.button(text="❌ Отмена", callback_data="admin_delete_cancel")
    builder.adjust(1)
    return builder.as_markup()

def upload_action_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Сохранить и разослать", callback_data="upload_broadcast")
    builder.button(text="💾 Только сохранить", callback_data="upload_save_only")
    builder.button(text="❌ Отменить", callback_data="upload_cancel")
    builder.adjust(1)
    return builder.as_markup()

def notification_products_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="ScoutScope", callback_data="notify_scout_scope")
    builder.button(text="PerformanceCoach CRM", callback_data="notify_crm")
    builder.button(text="CIS FINDER BOT", callback_data="notify_cis_bot")
    builder.button(text="📢 Всем пользователям", callback_data="notify_all")
    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def confirm_broadcast_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, отправить", callback_data="confirm_yes")
    builder.button(text="❌ Отменить", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()

def social_networks_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Telegram 📱", url="https://t.me/tw1zz_project")
    builder.button(text="Сайт 🌐", url="https://twizz-project.ru/")
    builder.button(text="VK 💬", url="https://vk.com/tw1zz_manager")
    builder.adjust(1)
    return builder.as_markup()
