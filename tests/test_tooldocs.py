import tempfile
import unittest
from pathlib import Path

from diag.tooldocs.doc_store import ToolDocStore
from diag.tooldocs.profile_builder import build_profile, suggest_for_scene


class ToolDocsTests(unittest.TestCase):
    def test_profile_builder_extracts_flags(self) -> None:
        profile = build_profile("ss", "Usage: ss [ --tcp -t --listening -l ]", "")
        self.assertIn("--tcp", profile.flags)
        self.assertTrue(profile.likely_readonly)

    def test_doc_store_round_trip_and_suggest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ToolDocStore(Path(tmp) / "tooldocs.json")
            store.put(build_profile("ss", "Usage: ss --tcp", ""))
            profiles = store.load()
        suggestions = suggest_for_scene("service-failed", profiles)
        self.assertTrue(any("ss:" in suggestion for suggestion in suggestions))


if __name__ == "__main__":
    unittest.main()
