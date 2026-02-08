from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, ContentType, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
import database as db
from config import ADMIN_IDS

router = Router()

SCOUT_SCOPE_DEMO_INFO = (
    "*Демоверсия* — это демонстрация продукта без полного функционала.\n\n"
    "*Что доступно в ScoutScope Pro и недоступно в демоверсии:*\n"
    "• Актуальные базы данных\n"
    "• Просмотр возраста игроков\n"
    "• Просмотр Faceit-профилей\n"
    "• AI-ассистент для сравнения игроков"
)

SCOUT_SCOPE_INSTRUCTION_TEXT = (
    "📘 *Как пользоваться ScoutScope*\n\n"
    "1. Скачайте и установите приложение ScoutScope.\n"
    "2. Выберите базу данных для работы:\n"
    "• Можно скачать и использовать нашу актуальную базу данных в боте.\n"
    "• Также можно использовать собственную базу данных.\n"
    "3. Запустите ScoutScope и загрузите выбранную базу данных.\n"
    "4. Используйте поиск и карточки игроков для анализа.\n\n"
    "Если потребуется помощь с настройкой, напишите в поддержку 👩‍💻"
)

SCOUT_SCOPE_PLANS = {
    "basic": {
        "title": "Базовый",
        "price": "3000 рублей",
        "updates": "обновление базы раз в 24 часа",
        "details": "Полный функционал",
    },
    "standard": {
        "title": "Стандарт",
        "price": "5000 рублей",
        "updates": "обновление базы раз в 12 часов",
        "details": "Полный функционал",
    },
    "3m": {
        "title": "Премиум",
        "price": "7000 рублей",
        "updates": "обновление базы раз в 12 часов",
        "details": "Полный функционал",
    },
}

class AdminStates(StatesGroup):
    waiting_for_product_selection = State()
    waiting_for_file_type = State()
    waiting_for_platform = State()
    waiting_for_version = State()
    waiting_for_broadcast_action = State()
    waiting_for_notification_text = State()
    waiting_for_notification_target = State()

class SupportStates(StatesGroup):
    waiting_for_request = State()


def get_demo_platform_text(product_key: str) -> str:
    if product_key == "scout_scope":
        return f"{SCOUT_SCOPE_DEMO_INFO}\n\nВыберите ОС для демоверсии:"
    return "Выберите ОС для демоверсии:"


async def show_demo_platform_message(callback: CallbackQuery, text: str, markup):
    if not callback.message:
        return

    try:
        # Для стабильного показа экрана демоверсии отправляем отдельное сообщение,
        # а предыдущее (если возможно) убираем.
        await callback.message.delete()
    except Exception:
        pass

    try:
        await callback.message.answer(text, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        pass


def _escape_markdown(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("_", "\\_")
        .replace("*", "\\*")
        .replace("`", "\\`")
        .replace("[", "\\[")
    )


def _build_product_text(product_key: str, product) -> str:
    text = f"📦 *{product['name']}*\n\n{product['description']}"

    if product_key in ("scout_scope", "crm"):
        if product["version"]:
            text += f"\n\n🪟 Windows версия: {_escape_markdown(product['version'])}"
        if product["version_mac"]:
            text += f"\n🍎 macOS версия: {_escape_markdown(product['version_mac'])}"
        if product["db_version"]:
            text += f"\n🗄️ Версия БД: {_escape_markdown(product['db_version'])}"
    elif product["version"]:
        text += f"\n\nВерсия: {_escape_markdown(product['version'])}"

    return text


async def _render_product_view(callback: CallbackQuery, text: str, markup, photo_path: str | None = None):
    if not callback.message:
        return

    if photo_path:
        if callback.message.photo:
            try:
                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=markup,
                    parse_mode="Markdown",
                )
            except Exception:
                await callback.message.edit_caption(caption=text, reply_markup=markup)
            return

        try:
            await callback.message.delete()
        except Exception:
            pass

        try:
            await callback.message.answer_photo(
                photo=FSInputFile(photo_path),
                caption=text,
                reply_markup=markup,
                parse_mode="Markdown",
            )
        except Exception:
            await callback.message.answer(text, reply_markup=markup)
        return

    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        await callback.message.edit_text(text, reply_markup=markup)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    # Отправляем логотип
    try:
        photo = FSInputFile('logo.png')
        await message.answer_photo(
            photo=photo,
            caption=(
                "Приветствуем тебя в нашем боте! 🚀\n\n"
                "Ты в правильном месте, если хочешь:\n"
                "✔️ Быстро и удобно оформить заказ\n"
                "✔️ Получить актуальную информацию о продуктах\n\n"
                "Выбери нужный раздел в меню ниже 👇"
            ),
            reply_markup=kb.main_menu()
        )
    except FileNotFoundError:
        # Если файл не найден, отправляем текст без изображения
        await message.answer(
            "Приветствуем тебя в нашем боте! 🚀\n\n"
            "Ты в правильном месте, если хочешь:\n"
            "✔️ Быстро и удобно оформить заказ\n"
            "✔️ Получить актуальную информацию о продуктах\n\n"
            "Выбери нужный раздел в меню ниже 👇",
            reply_markup=kb.main_menu()
        )

@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_admin(message: Message):
    await message.answer(
        "🔐 *Админ-панель*\n\n"
        "Выберите действие:",
        reply_markup=kb.admin_menu(),
        parse_mode="Markdown"
    )

# --- Admin Panel ---

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔐 *Админ-панель*\n\n"
        "Выберите действие:",
        reply_markup=kb.admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_upload")
async def admin_upload_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📤 *Загрузка файлов*\n\n"
        "Отправьте файл (приложение или базу данных):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_view_products")
async def admin_view_products(callback: CallbackQuery):
    products = await db.get_all_products()
    
    text = "📊 *Текущие продукты:*\n\n"
    for product in products:
        text += f"📦 *{product['name']}* (`{product['key']}`)\n"
        if product['key'] in ('scout_scope', 'crm'):
            if product['version']:
                text += f"   └ Windows версия: `{product['version']}`\n"
            else:
                text += f"   └ Windows версия: не загружено\n"
            if product['version_mac']:
                text += f"   └ macOS версия: `{product['version_mac']}`\n"
            else:
                text += f"   └ macOS версия: не загружено\n"
        else:
            if product['version']:
                text += f"   └ Версия приложения: `{product['version']}`\n"
            else:
                text += f"   └ Приложение: не загружено\n"
        
        if product['key'] in ('scout_scope', 'crm'):
            if product['db_version']:
                text += f"   └ Версия БД: `{product['db_version']}`\n"
            else:
                text += f"   └ База данных: не загружена\n"
        text += "\n"
    
    await callback.message.edit_text(text, reply_markup=kb.admin_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_send_notification")
async def admin_send_notification_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 *Создание уведомления*\n\n"
        "Введите текст уведомления:",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_notification_text)
    await callback.answer()

@router.message(AdminStates.waiting_for_notification_text)
async def admin_notification_text_received(message: Message, state: FSMContext):
    await state.update_data(notification_text=message.text)
    await message.answer(
        "📢 *Кому отправить уведомление?*",
        reply_markup=kb.notification_products_menu(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_notification_target)

@router.callback_query(AdminStates.waiting_for_notification_target, F.data.startswith("notify_"))
async def admin_notification_target_selected(callback: CallbackQuery, state: FSMContext):
    target = callback.data.split("_", 1)[1]
    data = await state.get_data()
    notification_text = data['notification_text']
    
    # Предпросмотр
    preview_text = (
        f"📢 *Предпросмотр уведомления:*\n\n"
        f"{notification_text}\n\n"
        f"📨 Получатели: "
    )
    
    if target == "all":
        user_count = await db.get_user_count()
        preview_text += f"Все пользователи ({user_count} чел.)"
    else:
        preview_text += f"Пользователи продукта {target}"
    
    preview_text += "\n\nОтправить?"
    
    await state.update_data(target=target)
    await callback.message.edit_text(preview_text, reply_markup=kb.confirm_broadcast_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "confirm_yes", AdminStates.waiting_for_notification_target)
async def admin_confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    notification_text = data['notification_text']
    
    users = await db.get_all_users()
    count = 0
    failed = 0
    
    await callback.message.edit_text("📤 Отправка уведомлений...")
    
    for user_id in users:
        try:
            await callback.bot.send_message(user_id, f"📢 {notification_text}")
            count += 1
        except Exception:
            failed += 1
    
    await callback.message.answer(
        f"✅ *Рассылка завершена!*\n\n"
        f"Доставлено: {count}\n"
        f"Не доставлено: {failed}",
        reply_markup=kb.admin_menu(),
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "confirm_no")
async def admin_cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ Рассылка отменена",
        reply_markup=kb.admin_menu()
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    user_count = await db.get_user_count()
    products = await db.get_all_products()
    
    uploaded_files = 0
    for p in products:
        if p['file_id']:
            uploaded_files += 1
        if p['file_id_mac']:
            uploaded_files += 1
        if p['db_file_id']:
            uploaded_files += 1
    
    text = (
        f"📈 *Статистика бота*\n\n"
        f"👥 Всего пользователей: {user_count}\n"
        f"📦 Продуктов: {len(products)}\n"
        f"📁 Загружено файлов: {uploaded_files}\n"
    )
    
    await callback.message.edit_text(text, reply_markup=kb.admin_menu(), parse_mode="Markdown")
    await callback.answer()

# --- Admin File Upload Logic ---

@router.message(F.document, F.from_user.id.in_(ADMIN_IDS))
async def admin_upload_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    await state.update_data(file_id=file_id)
    await message.answer(
        "Файл получен. К какому продукту он относится?",
        reply_markup=kb.products_menu()
    )
    await state.set_state(AdminStates.waiting_for_product_selection)

@router.callback_query(AdminStates.waiting_for_product_selection, F.data.startswith("prod_"))
async def admin_select_product(callback: CallbackQuery, state: FSMContext):
    product_key = callback.data.split("_", 1)[1]
    await state.update_data(product_key=product_key)
    
    if product_key in ('scout_scope', 'crm'):
        await callback.message.answer("Что вы загружаете?", reply_markup=kb.file_type_menu())
        await state.set_state(AdminStates.waiting_for_file_type)
    else:
        await callback.message.answer("Введите версию продукта (например, 1.0.5):")
        await state.update_data(file_type='app', platform='win')
        await state.set_state(AdminStates.waiting_for_version)
    await callback.answer()

@router.callback_query(AdminStates.waiting_for_file_type, F.data.startswith("file_type_"))
async def admin_select_file_type(callback: CallbackQuery, state: FSMContext):
    file_type = callback.data.split("_", 2)[2]
    await state.update_data(file_type=file_type)
    
    if file_type == 'app':
        await callback.message.answer("Для какой платформы загружается приложение?", reply_markup=kb.platform_menu())
        await state.set_state(AdminStates.waiting_for_platform)
    else:
        await callback.message.answer("Введите версию базы данных (например, 2.1.0):")
    await callback.answer()

@router.callback_query(AdminStates.waiting_for_platform, F.data.startswith("platform_"))
async def admin_select_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.split("_", 1)[1]
    await state.update_data(platform=platform)
    platform_name = "Windows" if platform == "win" else "macOS"
    await callback.message.answer(f"Введите версию приложения для {platform_name} (например, 1.0.5):")
    await state.set_state(AdminStates.waiting_for_version)
    await callback.answer()

@router.message(AdminStates.waiting_for_version)
async def admin_set_version(message: Message, state: FSMContext):
    version = message.text
    await state.update_data(version=version)
    
    data = await state.get_data()
    file_type = data.get('file_type', 'app')
    file_type_name = "приложения" if file_type == 'app' else "базы данных"
    platform = data.get('platform')
    platform_note = ""
    if file_type == 'app' and platform in ('win', 'mac'):
        platform_name = "Windows" if platform == "win" else "macOS"
        platform_note = f" ({platform_name})"
    
    await message.answer(
        f"📝 Версия {file_type_name}{platform_note}: `{version}`\n\n"
        f"Что делать дальше?",
        reply_markup=kb.upload_action_menu(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_broadcast_action)

@router.callback_query(AdminStates.waiting_for_broadcast_action, F.data == "upload_broadcast")
async def admin_broadcast_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    version = data['version']
    file_type = data.get('file_type', 'app')
    platform = data.get('platform', 'win')
    
    # Сохраняем в БД
    if file_type == 'app':
        if platform == 'mac':
            await db.update_product_file_mac(data['product_key'], data['file_id'], version)
        else:
            await db.update_product_file(data['product_key'], data['file_id'], version)
        file_desc = "приложения"
    else:
        await db.update_product_db(data['product_key'], data['file_id'], version)
        file_desc = "базы данных"
    
    await callback.message.edit_text(f"✅ {file_desc.capitalize()} сохранено!\n📤 Начинаю рассылку...")
    
    # Рассылка
    users = await db.get_all_users()
    product = await db.get_product(data['product_key'])
    count = 0
    
    for user_id in users:
        try:
            if file_type == 'app':
                platform_name = "Windows" if platform == "win" else "macOS"
                caption = (
                    f"🔥 Вышло обновление {product['name']}!\n\n"
                    f"📦 Приложение ({platform_name}) версия: {version}"
                )
                await callback.bot.send_document(user_id, data['file_id'], caption=caption)
            else:
                caption = f"🔥 Обновление базы данных {product['name']}!\n\n🗄️ База данных версия: {version}"
                await callback.bot.send_document(user_id, data['file_id'], caption=caption)
            
            # Если это ScoutScope и есть оба файла, отправим второй
            if data['product_key'] in ('scout_scope', 'crm'):
                if file_type == 'app' and product['db_file_id']:
                    try:
                        db_caption = f"🗄️ База данных версия: {product['db_version']}"
                        await callback.bot.send_document(user_id, product['db_file_id'], caption=db_caption)
                    except:
                        pass
                elif file_type == 'db' and product['file_id']:
                    try:
                        app_caption = f"📦 Приложение версия: {product['version']}"
                        await callback.bot.send_document(user_id, product['file_id'], caption=app_caption)
                    except:
                        pass
                elif file_type == 'db' and product['file_id_mac']:
                    try:
                        app_caption = f"📦 Приложение версия: {product['version_mac']}"
                        await callback.bot.send_document(user_id, product['file_id_mac'], caption=app_caption)
                    except:
                        pass
            
            count += 1
        except Exception:
            pass
    
    await callback.message.answer(
        f"✅ *Готово!*\n\n"
        f"Рассылка завершена.\n"
        f"Доставлено: {count} пользователям.",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(AdminStates.waiting_for_broadcast_action, F.data == "upload_save_only")
async def admin_save_only(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    version = data['version']
    file_type = data.get('file_type', 'app')
    platform = data.get('platform', 'win')
    
    # Сохраняем в БД
    if file_type == 'app':
        if platform == 'mac':
            await db.update_product_file_mac(data['product_key'], data['file_id'], version)
        else:
            await db.update_product_file(data['product_key'], data['file_id'], version)
        file_desc = "приложения"
    else:
        await db.update_product_db(data['product_key'], data['file_id'], version)
        file_desc = "базы данных"
    
    await callback.message.edit_text(
        f"✅ *{file_desc.capitalize()} сохранено!*\n\n"
        f"Версия: `{version}`\n"
        f"Рассылка не производилась.",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(AdminStates.waiting_for_broadcast_action, F.data == "upload_cancel")
async def admin_cancel_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Загрузка отменена")
    await state.clear()
    await callback.answer()

# --- Shop Logic ---

@router.message(F.text == "Магазин 🛍️")
async def show_shop(message: Message):
    await message.answer("Выберите продукт:", reply_markup=kb.products_menu())

@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery):
    if callback.message.photo:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer("Выберите продукт:", reply_markup=kb.products_menu())
    else:
        await callback.message.edit_text("Выберите продукт:", reply_markup=kb.products_menu())
    await callback.answer()


async def _show_product(callback: CallbackQuery, product_key: str) -> bool:
    product = await db.get_product(product_key)
    if not product:
        return False

    text = _build_product_text(product_key, product)
    markup = None
    photo_path = None

    if product_key == "scout_scope":
        has_demo = bool(product["file_id"] or product["file_id_mac"])
        markup = kb.scout_scope_menu(has_file=has_demo)
        photo_path = "scoutscope_logo.png"
    elif product_key == "crm":
        has_demo = bool(product["file_id"] or product["file_id_mac"])
        markup = kb.crm_menu(has_file=has_demo)
        photo_path = "Performance.jpg"
    elif product_key == "cis_bot":
        markup = kb.cis_bot_menu()

    await _render_product_view(callback, text, markup, photo_path)
    return True


@router.callback_query(F.data == "back_to_scout_scope")
async def back_to_scout_scope(callback: CallbackQuery):
    is_shown = await _show_product(callback, "scout_scope")
    if is_shown:
        await callback.answer()
    else:
        await callback.answer("Продукт не найден", show_alert=True)


@router.callback_query(F.data.startswith("prod_"))
async def show_product(callback: CallbackQuery):
    product_key = callback.data.split("_", 1)[1]
    is_shown = await _show_product(callback, product_key)
    if is_shown:
        await callback.answer()
    else:
        await callback.answer("Продукт не найден", show_alert=True)

@router.callback_query(F.data.startswith("demo_select_"))
async def demo_select_platform(callback: CallbackQuery):
    product_key = callback.data.split("_", 2)[2]
    text = get_demo_platform_text(product_key)
    markup = kb.demo_platform_menu(product_key)
    await show_demo_platform_message(callback, text, markup)
    await callback.answer()

@router.callback_query(F.data == "scout_scope_instruction")
async def show_scout_scope_instruction(callback: CallbackQuery):
    markup = kb.scout_scope_instruction_menu()
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=SCOUT_SCOPE_INSTRUCTION_TEXT,
            reply_markup=markup,
            parse_mode="Markdown",
        )
    else:
        await callback.message.edit_text(
            SCOUT_SCOPE_INSTRUCTION_TEXT,
            reply_markup=markup,
            parse_mode="Markdown",
        )
    await callback.answer()

@router.callback_query(F.data == "demo_scout_scope")
async def demo_select_platform_legacy(callback: CallbackQuery):
    product_key = "scout_scope"
    text = get_demo_platform_text(product_key)
    markup = kb.demo_platform_menu(product_key)
    await show_demo_platform_message(callback, text, markup)
    await callback.answer()

@router.callback_query(F.data.startswith("demo_download_"))
async def send_demo(callback: CallbackQuery):
    payload = callback.data[len("demo_download_"):]
    product_key, platform = payload.rsplit("_", 1)
    product = await db.get_product(product_key)
    if not product:
        await callback.answer("Продукт не найден", show_alert=True)
        return

    file_id = product['file_id'] if platform == 'win' else product['file_id_mac']
    version = product['version'] if platform == 'win' else product['version_mac']
    platform_name = "Windows" if platform == "win" else "macOS"

    if file_id:
        caption = f"📦 Демоверсия {product['name']} ({platform_name})"
        if version:
            caption += f"\nВерсия приложения: {version}"
        await callback.message.answer_document(file_id, caption=caption)
        
        if product['db_file_id']:
            db_caption = f"🗄️ База данных для {product['name']}"
            if product['db_version']:
                db_caption += f"\nВерсия БД: {product['db_version']}"
            await callback.message.answer_document(product['db_file_id'], caption=db_caption)
        
        await callback.answer()
    else:
        await callback.answer(f"Файл для {platform_name} временно недоступен", show_alert=True)

@router.callback_query(F.data == "buy_scout_scope")
async def show_scout_scope_plans(callback: CallbackQuery):
    text = (
        "💎 *ScoutScope Pro*\n\n"
        "Выберите тариф:\n"
        "• *Базовый* — полный функционал, 3000 рублей, обновление базы раз в 24 часа.\n"
        "• *Стандарт* — полный функционал, 5000 рублей, обновление базы раз в 12 часов.\n"
        "• *Премиум* — 7000 рублей, обновление базы раз в 12 часов."
    )
    markup = kb.scout_scope_pro_plans_menu()
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode="Markdown")
    else:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("plan_scout_scope_"))
async def scout_scope_plan_request(callback: CallbackQuery, bot: Bot):
    plan_key = callback.data.split("plan_scout_scope_", 1)[1]
    plan = SCOUT_SCOPE_PLANS.get(plan_key)
    if not plan:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    user = callback.from_user
    plan_line = f"{plan['title']} — {plan['details']}, {plan['price']}, {plan['updates']}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💰 *Запрос Pro версии*\n\n"
                f"Продукт: ScoutScope\n"
                f"Тариф: {plan_line}\n"
                f"Пользователь: {user.full_name} (@{user.username})\n"
                f"ID: {user.id}",
                parse_mode="Markdown"
            )
        except:
            pass

    await callback.answer(
        "Заявка отправлена администратору! 🚀\nАдминистратор скоро свяжется с вами.",
        show_alert=True,
    )

@router.callback_query(F.data.startswith("buy_"))
async def buy_request(callback: CallbackQuery, bot: Bot):
    product_key = callback.data.split("_", 1)[1]
    if product_key == "scout_scope":
        return
    user = callback.from_user
    
    # Notify Admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💰 *Запрос Pro версии*\n\n"
                f"Продукт: {product_key}\n"
                f"Пользователь: {user.full_name} (@{user.username})\n"
                f"ID: {user.id}",
                parse_mode="Markdown"
            )
        except:
            pass
            
    await callback.answer(
        "Заявка отправлена администратору! 🚀\nАдминистратор скоро свяжется с вами.",
        show_alert=True,
    )

# --- Social Networks ---
@router.message(F.text == "Соц.Сети 🌐")
async def show_social_networks(message: Message):
    await message.answer(
        "🌐 *Наши социальные сети:*\n\n"
        "Подпишись и следи за новостями проекта!",
        reply_markup=kb.social_networks_menu(),
        parse_mode="Markdown"
    )

# --- Support ---
@router.message(F.text == "Поддержка 👩‍💻")
async def support_start(message: Message, state: FSMContext):
    await state.set_state(SupportStates.waiting_for_request)
    await message.answer(
        "Опишите ваш вопрос одним сообщением.\n\n"
        "Например: что не работает, на каком этапе и какая ошибка появляется.\n"
        "Чтобы отменить, отправьте: Отмена"
    )

@router.message(SupportStates.waiting_for_request, F.text)
async def support_submit(message: Message, state: FSMContext, bot: Bot):
    request_text = message.text.strip()
    if not request_text:
        await message.answer("Напишите, пожалуйста, текст запроса или отправьте «Отмена».")
        return
    if request_text.lower() == "отмена":
        await state.clear()
        await message.answer("Запрос в поддержку отменен.")
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "не указан"
    admin_message = (
        "🆘 Новый запрос в поддержку\n\n"
        f"Пользователь: {user.full_name}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n\n"
        "Сообщение:\n"
        f"{request_text}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_message)
        except Exception:
            pass

    await state.clear()
    await message.answer("Спасибо! Поддержка уже спешит на помощь 🚀")

@router.message(SupportStates.waiting_for_request)
async def support_submit_non_text(message: Message):
    await message.answer("Пожалуйста, отправьте запрос текстом или напишите «Отмена».")

# --- Placeholder Handlers ---
@router.message(F.text == "Отзывы 💡")
async def placeholder(message: Message):
    await message.answer("Этот раздел находится в разработке 🛠️")
