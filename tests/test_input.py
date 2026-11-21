import unittest

import pygame

from core.input import InputController


class InputControllerTests(unittest.TestCase):
    def test_dispatch_runs_the_selected_action(self):
        calls = []
        controller = InputController({"save_state": lambda: calls.append("saved")})

        self.assertTrue(controller.dispatch("save_state"))
        self.assertEqual(calls, ["saved"])
        self.assertFalse(controller.dispatch("unknown"))

    def test_keyboard_shortcuts_dispatch_registered_actions(self):
        calls = []
        action_names = set(InputController.KEY_ACTIONS.values())
        actions = {name: lambda name=name: calls.append(name) for name in action_names}
        controller = InputController(actions)

        for key in InputController.KEY_ACTIONS:
            self.assertTrue(controller.handle_key(key))

        self.assertEqual(set(calls), action_names)
        self.assertFalse(controller.handle_key(pygame.K_F1))


if __name__ == "__main__":
    unittest.main()
