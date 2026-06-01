import unittest
from pathlib import Path

from diag.utils.config_loader import load_config


class ConfigPrecedenceTests(unittest.TestCase):
    def test_cli_overrides_local_and_home(self) -> None:
        local = Path("configs/local.yaml")
        try:
            local.write_text("providers:\n  default: local-provider\n", encoding="utf-8")
            config = load_config(
                cli_overrides={"providers": {"default": "cli-provider"}},
                home=Path("tests/fixtures/missing-home-config.yaml"),
            )
            self.assertEqual(config["providers"]["default"], "cli-provider")
        finally:
            if local.exists():
                local.unlink()

    def test_local_overrides_project_configs(self) -> None:
        local = Path("configs/local.yaml")
        try:
            local.write_text("providers:\n  default: local-provider\n", encoding="utf-8")
            config = load_config(home=Path("tests/fixtures/missing-home-config.yaml"))
            self.assertEqual(config["providers"]["default"], "local-provider")
        finally:
            if local.exists():
                local.unlink()


if __name__ == "__main__":
    unittest.main()
