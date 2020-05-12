import unittest
from unittest import TestCase

from vernie import vernie_voice_control


class VernieVoiceControlTestCase(unittest.TestCase):
    def test_preprocess_command(self):
        numbers_dict = vernie_voice_control.load_numbers_dict('fr-FR')
        command = vernie_voice_control.preprocess_command("avance cinq", numbers_dict=numbers_dict)
        self.assertEqual("avance 5", command)
        command = vernie_voice_control.preprocess_command("recule dix", numbers_dict=numbers_dict)
        self.assertEqual("recule 10", command)

    def test_notify_listening(self):
        vernie_voice_control.notify_listening()


if __name__ == '__main__':
    unittest.main()

