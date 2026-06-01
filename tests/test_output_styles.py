import json
import unittest

from diag.ui.theme import load_output_style


class OutputStylesTests(unittest.TestCase):
    def test_student_style_loads(self) -> None:
        style = load_output_style("student")
        self.assertEqual(style.name, "student")
        self.assertIn("Student", style.title)


if __name__ == "__main__":
    unittest.main()
