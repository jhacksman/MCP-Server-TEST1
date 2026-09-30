"""Offline checks for Gemini view credential configuration."""

import os
from pathlib import Path
import runpy
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class TestGeminiApiKey(unittest.TestCase):
    def load_view(self, view):
        genai = ModuleType("google.genai")
        genai.Client = Mock()
        genai.Client.return_value.models.generate_content.return_value = (
            SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[]))])
        )
        genai.types = SimpleNamespace(GenerateContentConfig=Mock())
        google = ModuleType("google")
        google.genai = genai
        pil = ModuleType("PIL")
        pil.Image = SimpleNamespace(open=Mock())
        with patch.dict("sys.modules", {"google": google, "google.genai": genai, "PIL": pil}):
            module = runpy.run_path(str(Path(__file__).parent / "gemini" / f"{view}_view.py"))
        return module[f"generate_{view}_view"], genai, pil.Image

    def test_missing_or_blank_key_fails_before_client_or_image_access(self):
        for view in ("front", "back", "left", "right"):
            for value in (None, "", " \t\n"):
                with self.subTest(view=view, value=value):
                    generate, genai, image = self.load_view(view)
                    env = {} if value is None else {"GOOGLE_API_KEY": value}
                    with patch.dict(os.environ, env, clear=True):
                        with self.assertRaisesRegex(ValueError, "GOOGLE_API_KEY environment variable must be set"):
                            generate("unused.png")
                    genai.Client.assert_not_called()
                    image.open.assert_not_called()

    def test_configured_key_is_passed_to_client(self):
        for view in ("front", "back", "left", "right"):
            with self.subTest(view=view):
                generate, genai, image = self.load_view(view)
                with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-placeholder"}, clear=True):
                    self.assertIsNone(generate("input.png"))
                genai.Client.assert_called_once_with(api_key="test-placeholder")
                image.open.assert_called_once_with("input.png")
                genai.Client.return_value.models.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
