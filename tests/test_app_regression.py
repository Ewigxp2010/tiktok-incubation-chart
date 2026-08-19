import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "tiktok.py"


class SimulatorRegressionTests(unittest.TestCase):
    def start_setup(self):
        app = AppTest.from_file(str(APP_PATH)).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key="n_skus_input").value, 5)
        self.assertEqual(app.button(key="generate_simulator_btn").key, "generate_simulator_btn")
        return app

    def generate(self, app):
        next(button for button in app.button if button.label == "Generate Simulator").click().run(timeout=45)
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["has_generated"])
        self.assertTrue(app.session_state["_applied_signature"])
        return app

    def test_generation_phase_and_chart_mode_are_single_click(self):
        app = self.generate(self.start_setup())

        app.button(key="selected_phase_view__btn__1").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["selected_phase_view"], "phase2")

        app.button(key="phase_chart_mode_phase2__btn__1").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["phase_chart_mode_phase2"], "total")

    def test_draft_changes_require_explicit_apply(self):
        app = self.generate(self.start_setup())
        original_signature = app.session_state["_applied_signature"]
        original_outcomes = dict(app.session_state["_model_current_outcomes"])

        app.button(key="back_to_client_view_btn").click().run(timeout=45)
        aov = app.number_input(key="aov_0")
        aov.set_value(float(aov.value) + 1).run(timeout=45)

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["_applied_signature"], original_signature)
        self.assertNotEqual(app.session_state["_draft_signature"], original_signature)
        self.assertEqual(dict(app.session_state["_model_current_outcomes"]), original_outcomes)
        self.assertEqual(app.button(key="apply_model_changes_btn").key, "apply_model_changes_btn")

        app.button(key="apply_model_changes_btn").click().run(timeout=45)
        self.assertFalse(app.exception)
        self.assertNotEqual(app.session_state["_applied_signature"], original_signature)
        self.assertEqual(app.session_state["_applied_signature"], app.session_state["_draft_signature"])
        self.assertNotEqual(dict(app.session_state["_model_current_outcomes"]), original_outcomes)

    def test_empty_sku_name_and_language_switches_remain_stable(self):
        app = self.start_setup()
        app.text_input(key="sku_name_0").set_value("").run(timeout=30)
        self.generate(app)

        self.assertEqual(app.session_state["_applied_product_df"].iloc[0]["SKU"], "A")
        app.button(key="selected_phase_view__btn__2").click().run(timeout=30)
        for language in ("zh", "de", "nl", "en"):
            app.selectbox(key="language_input").set_value(language).run(timeout=45)
            self.assertFalse(app.exception)
            self.assertTrue(app.session_state["has_generated"])
            self.assertEqual(app.session_state["selected_phase_view"], "phase3")

    def test_category_change_keeps_subcategory_valid(self):
        app = self.generate(self.start_setup())
        app.button(key="back_to_client_view_btn").click().run(timeout=45)
        category = app.selectbox(key="category_0")
        replacement = next(option for option in category.options if option != category.value)
        category.set_value(replacement).run(timeout=45)

        self.assertFalse(app.exception)
        subcategory = app.selectbox(key="subcategory_0")
        self.assertIn(app.session_state["subcategory_0"], subcategory.options)
        self.assertEqual(app.button(key="apply_model_changes_btn").key, "apply_model_changes_btn")


if __name__ == "__main__":
    unittest.main()
