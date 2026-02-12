import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import handlers
import keyboards


def _extract_callback_data(markup) -> list[str]:
    result = []
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data:
                result.append(button.callback_data)
    return result


class ScoutScopeNavigationTests(unittest.IsolatedAsyncioTestCase):
    def test_back_buttons_for_scoutscope_use_dedicated_callback(self):
        instruction_menu = keyboards.scout_scope_instruction_menu()
        plans_menu = keyboards.scout_scope_pro_plans_menu()
        demo_menu = keyboards.demo_platform_menu("scout_scope")

        self.assertIn("back_to_scout_scope", _extract_callback_data(instruction_menu))
        self.assertIn("back_to_scout_scope", _extract_callback_data(plans_menu))
        self.assertIn("back_to_scout_scope", _extract_callback_data(demo_menu))

    def test_demo_menu_for_other_products_stays_on_prod_callback(self):
        demo_menu = keyboards.demo_platform_menu("crm")
        self.assertIn("prod_crm", _extract_callback_data(demo_menu))

    async def test_show_product_for_scoutscope_includes_instruction_and_demo_when_available(self):
        callback = SimpleNamespace(answer=AsyncMock())
        product = {
            "name": "ScoutScope",
            "description": "desc",
            "version": "1.0.0",
            "version_mac": None,
            "db_version": None,
            "file_id": "file-win",
            "file_id_mac": None,
        }

        with patch.object(handlers.db, "get_product", new=AsyncMock(return_value=product)):
            with patch.object(handlers, "_render_product_view", new=AsyncMock()) as render_mock:
                await handlers._show_product(callback, "scout_scope")

        call = render_mock.await_args
        self.assertEqual(call.args[3], "scoutscope_logo.png")

        markup = call.args[2]
        callbacks = _extract_callback_data(markup)
        self.assertIn("scout_scope_instruction", callbacks)
        self.assertIn("demo_select_scout_scope", callbacks)

    async def test_show_product_for_scoutscope_keeps_instruction_without_demo(self):
        callback = SimpleNamespace(answer=AsyncMock())
        product = {
            "name": "ScoutScope",
            "description": "desc",
            "version": "1.0.0",
            "version_mac": None,
            "db_version": None,
            "file_id": None,
            "file_id_mac": None,
        }

        with patch.object(handlers.db, "get_product", new=AsyncMock(return_value=product)):
            with patch.object(handlers, "_render_product_view", new=AsyncMock()) as render_mock:
                await handlers._show_product(callback, "scout_scope")

        markup = render_mock.await_args.args[2]
        callbacks = _extract_callback_data(markup)
        self.assertIn("scout_scope_instruction", callbacks)
        self.assertNotIn("demo_select_scout_scope", callbacks)

    async def test_back_to_scout_scope_handler_renders_product_and_answers_callback(self):
        callback = SimpleNamespace(answer=AsyncMock())

        with patch.object(handlers, "_show_product", new=AsyncMock(return_value=True)) as show_product_mock:
            await handlers.back_to_scout_scope(callback)

        show_product_mock.assert_awaited_once_with(callback, "scout_scope")
        callback.answer.assert_awaited_once()

    async def test_back_to_scout_scope_handler_shows_alert_when_product_missing(self):
        callback = SimpleNamespace(answer=AsyncMock())

        with patch.object(handlers, "_show_product", new=AsyncMock(return_value=False)):
            await handlers.back_to_scout_scope(callback)

        callback.answer.assert_awaited_once_with("Продукт не найден", show_alert=True)

    def test_build_product_text_uses_html_and_premium_platform_emojis(self):
        product = {
            "name": "ScoutScope <Pro>",
            "description": "desc & details",
            "version": "1.0.0_beta",
            "version_mac": "2.0*mac",
            "db_version": "db<3",
        }

        text = handlers._build_product_text("scout_scope", product)
        self.assertIn("📦 <b>ScoutScope &lt;Pro&gt;</b>", text)
        self.assertIn("desc &amp; details", text)
        self.assertIn('<tg-emoji emoji-id="5936226607931854504"></tg-emoji> Windows версия: 1.0.0_beta', text)
        self.assertIn('<tg-emoji emoji-id="5352762486250545420"></tg-emoji> macOS версия: 2.0*mac', text)
        self.assertIn("🗄️ Версия БД: db&lt;3", text)


if __name__ == "__main__":
    unittest.main()
