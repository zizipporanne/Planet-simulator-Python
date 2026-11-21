import json
import tempfile
import unittest
from pathlib import Path

from core.config import ConfigStore
from core.state import SimulatorState, ViewMode


class SimulatorStateTests(unittest.TestCase):
    def test_texture_cycle_wraps_in_order(self):
        state = SimulatorState()
        self.assertEqual(
            [state.cycle_texture() for _ in range(4)],
            ["Political", "Detailed", "Default", "Political"],
        )

    def test_view_mode_cycle_wraps_in_order(self):
        state = SimulatorState()
        self.assertEqual(
            [state.cycle_view_mode() for _ in range(5)],
            [
                ViewMode.WIREFRAME,
                ViewMode.POINTS,
                ViewMode.NIGHT,
                ViewMode.NORMAL,
                ViewMode.WIREFRAME,
            ],
        )

    def test_config_save_and_load_preserves_existing_json_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "simulator_config.json"
            original = SimulatorState(
                rotation_x=12.5,
                rotation_y=220.0,
                distance=-7.0,
                texture="Detailed",
                view_mode=ViewMode.NIGHT,
                atmosphere_enabled=True,
            ).to_config()
            store = ConfigStore(config_path)

            self.assertTrue(store.save(original))
            saved = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(
                set(saved),
                {
                    "texture", "auto_rotate", "mouse_sensitivity", "last_position",
                    "view_mode", "animation_enabled", "effects_enabled",
                    "sound_enabled", "atmosphere_enabled",
                },
            )

            restored = SimulatorState()
            restored.load_config(store.load())
            self.assertEqual(restored.to_config(), original)

    def test_missing_config_uses_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            config = ConfigStore(Path(directory) / "missing.json").load()
        self.assertEqual(config["texture"], "Default")
        self.assertEqual(config["view_mode"], "Normal")


if __name__ == "__main__":
    unittest.main()
