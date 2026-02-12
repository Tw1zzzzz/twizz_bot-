import unittest

import keyboards


def inline_buttons(markup):
    return [button for row in markup.inline_keyboard for button in row]


class KeyboardTests(unittest.TestCase):
    def test_main_menu_structure(self):
        markup = keyboards.main_menu()
        texts = [[button.text for button in row] for row in markup.keyboard]

        self.assertEqual(
            texts,
            [
                ["Магазин 🛍️", "Отзывы 💡"],
                ["Соц.Сети 🌐", "Поддержка 👩‍💻"],
            ],
        )

    def test_products_menu_contains_all_products(self):
        markup = keyboards.products_menu()
        callbacks = [button.callback_data for button in inline_buttons(markup)]

        self.assertEqual(
            callbacks,
            ["prod_scout_scope", "prod_crm", "prod_cis_bot"],
        )

    def test_scout_scope_menu_toggles_demo_button(self):
        with_demo = keyboards.scout_scope_menu(has_file=True)
        without_demo = keyboards.scout_scope_menu(has_file=False)

        with_demo_callbacks = [button.callback_data for button in inline_buttons(with_demo)]
        without_demo_callbacks = [button.callback_data for button in inline_buttons(without_demo)]

        self.assertIn("demo_select_scout_scope", with_demo_callbacks)
        self.assertNotIn("demo_select_scout_scope", without_demo_callbacks)

    def test_demo_platform_menu_builds_platform_specific_callbacks(self):
        markup = keyboards.demo_platform_menu("crm")
        buttons = inline_buttons(markup)

        self.assertEqual(buttons[0].text, "Windows")
        self.assertEqual(buttons[1].text, "macOS")
        self.assertEqual(buttons[0].callback_data, "demo_download_crm_win")
        self.assertEqual(buttons[1].callback_data, "demo_download_crm_mac")
        self.assertEqual(buttons[2].callback_data, "prod_crm")

    def test_platform_menu_uses_plain_platform_labels(self):
        markup = keyboards.platform_menu()
        buttons = inline_buttons(markup)

        self.assertEqual(buttons[0].text, "Windows")
        self.assertEqual(buttons[1].text, "macOS")
        self.assertEqual(buttons[0].callback_data, "platform_win")
        self.assertEqual(buttons[1].callback_data, "platform_mac")

    def test_social_networks_links_are_present(self):
        markup = keyboards.social_networks_menu()
        urls = [button.url for button in inline_buttons(markup)]

        self.assertEqual(
            urls,
            [
                "https://t.me/tw1zz_project",
                "https://twizz-project.ru/",
                "https://vk.com/tw1zz_manager",
            ],
        )


if __name__ == "__main__":
    unittest.main()
