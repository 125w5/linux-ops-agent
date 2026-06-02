import unittest
from pathlib import Path

from diag.utils.config_loader import load_config


class ConfigPrecedenceTests(unittest.TestCase):
    def test_cli_overrides_local_and_home(self) -> None:
        local = Path("configs/local.yaml")
        original = local.read_text(encoding="utf-8") if local.exists() else None
        try:
            local.write_text("providers:\n  default: local-provider\n", encoding="utf-8")
            config = load_config(
                cli_overrides={"providers": {"default": "cli-provider"}},
                home=Path("tests/fixtures/missing-home-config.yaml"),
            )
            self.assertEqual(config["providers"]["default"], "cli-provider")
        finally:
            if original is None and local.exists():
                local.unlink()
            elif original is not None:
                local.write_text(original, encoding="utf-8")

    def test_local_overrides_project_configs(self) -> None:
        local = Path("configs/local.yaml")
        original = local.read_text(encoding="utf-8") if local.exists() else None
        try:
            local.write_text("providers:\n  default: local-provider\n", encoding="utf-8")
            config = load_config(home=Path("tests/fixtures/missing-home-config.yaml"))
            self.assertEqual(config["providers"]["default"], "local-provider")
        finally:
            if original is None and local.exists():
                local.unlink()
            elif original is not None:
                local.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
