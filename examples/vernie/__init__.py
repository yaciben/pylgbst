# coding=utf-8
import hashlib
import os
import re
import subprocess
import time

from pylgbst import *
from pylgbst.hub import MoveHub

try:
    import gtts


    def say(text, language='en'):
        print("%s" % text)
        # if isinstance(text, str):
        #     text = text.decode("utf-8")
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        dir_name = os.path.expanduser("~/tmp/vernie_speech/{}".format(language))
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        fname = "{}/{}.mp3".format(dir_name, md5)
        if not os.path.exists(fname):
            # myre = re.compile('[[A-Za-z]', re.UNICODE)
            # lang = 'en' if myre.match(text) else 'ru'
            # lang = 'fr' if myre.match(text) else 'ru'

            logging.getLogger('requests').setLevel(logging.getLogger('').getEffectiveLevel())
            tts = gtts.gTTS(text=text, lang=language, slow=False)
            tts.save(fname)

        with open(os.devnull, 'w') as fnull:
            subprocess.call("mplayer %s" % fname, shell=True, stderr=fnull, stdout=fnull)
except BaseException:
    def say(text):
        print("%s" % text)

forward = FORWARD = right = RIGHT = 1
backward = BACKWARD = left = LEFT = -1
straight = STRAIGHT = 0

SPEECH_LANG_MAP = {
    'en': {
        'ready': "Vernie the Robot is ready.",
        "commands help": "Available commands are: "
                         "forward, backward, turn left, turn right, "
                         "head left, head right, head straight, shot and say",
        "finished": "Thank you! Robot is now turning off",
        "text is empty": "Please, enter not empty text to say!",
        "unknown command": "Unknown command"
    },
    'fr': {
        'ready': "Vernie le robot est prêt.",
        "commands help": "Les commandes disponibles sont:"
                         "avance, recule, tourne gauche, tourne droite,"
                         "tête gauche, tête droite, feu, dis et fini",
        "finished": "Merci! Le robot s'éteint maintenant",
        "text is empty": "Veuillez saisir un texte non vide pour le dire!",
        "unknown command": "Commande non reconnue"
    },
    'fr-FR': {
        'ready': "Vernie le robot est prêt.",
        "commands help": "Les commandes disponibles sont:"
                         "avance, recule, tourne gauche, tourne droite,"
                         "tête gauche, tête droite, feu, dis et fini",
        "finished": "Merci! Le robot s'éteint maintenant",
        "text is empty": "Veuillez saisir un texte non vide pour le dire!",
        "unknown command": "Commande non reconnue"
    },
    "ru": {
        "ready": "Робот Веернии готов к работе",
        "type commands": "печатайте команды",
        "ok": "хорошо",
        "commands help": "Доступные команды это: вперёд, назад, влево, вправо, "
                         "голову влево, голову вправо, голову прямо, выстрел, скажи",
        "finished": "Робот завершает работу. Спасибо!",
        "commands from file": "Исполняю команды из файла",
        "fire": "Выстрел!",
        "text is empty": "Пожалуйста, наберите не пустой текст!",
        "unknown command": "неизвестная команда"  # FIXME Please confirm translation, as I don't speak Russian
    }
}

VERNIE_TO_MOTOR_DEGREES = 2.6
VERNIE_SINGLE_MOVE = 430


class Vernie(MoveHub):
    def __init__(self, language='en'):
        super(Vernie, self).__init__()
        self.language = language

        while True:
            required_devices = (self.vision_sensor, self.motor_external)
            if None not in required_devices:
                break
            log.debug("Waiting for required devices to appear: %s", required_devices)
            time.sleep(1)

        self._head_position = 0
        self.motor_external.subscribe(self._external_motor_data)

        self._reset_head()
        self.say("ready")
        time.sleep(1)

    def say(self, phrase):
        if phrase in SPEECH_LANG_MAP[self.language]:
            phrase = SPEECH_LANG_MAP[self.language][phrase]
        say(phrase, self.language)

    def _external_motor_data(self, data):
        log.debug("External motor position: %s", data)
        self._head_position = data

    def _reset_head(self):
        self.motor_external.timed(1, -0.2)
        self.head(RIGHT, angle=45)

    def head(self, direction=RIGHT, angle=25, speed=0.1):
        if direction == STRAIGHT:
            angle = -self._head_position
            direction = 1

        self.motor_external.angled(direction * angle, speed)

    def turn(self, direction, degrees=90, speed=0.3):
        self.head(STRAIGHT, speed=0.5)
        self.head(direction, 35, 1)
        self.motor_AB.angled(int(VERNIE_TO_MOTOR_DEGREES * degrees), speed * direction, -speed * direction)
        self.head(STRAIGHT, speed=0.5)

    def move(self, direction, distance=1, speed=0.2):
        self.head(STRAIGHT, speed=0.5)
        self.motor_AB.angled(distance * VERNIE_SINGLE_MOVE, speed * direction, speed * direction)

    def shot(self):
        self.motor_external.timed(0.5)
        self.head(STRAIGHT)
        self.head(STRAIGHT)

    def interpret_command(self, cmd, confirm):
        if cmd is None:
            return
        cmd = cmd.strip().lower().split(' ')
        if cmd[0] in ("head", "голова", "голову", "tête"):
            if cmd[-1] in ("right", "вправо", "направо", "droite"):
                confirm(cmd)
                self.head(RIGHT)
            elif cmd[-1] in ("left", "влево", "налево", "gauche"):
                confirm(cmd)
                self.head(LEFT)
            else:
                confirm(cmd)
                self.head(STRAIGHT)
        elif cmd[0] in ("say", "скажи", "сказать", "dis"):
            if not cmd[1:]:
                self.say("text is empty")
                return
            self.say(phrase=' '.join(cmd[1:]))
        elif cmd[0] in ("fire", "shot", "огонь", "выстрел", "feu"):
            self.say(phrase=cmd)
            self.shot()
        elif cmd[0] in ("end", "finish", "конец", "стоп", "fini"):
            self.say(phrase="finished")
            raise KeyboardInterrupt()
        elif cmd[0] in ("forward", "вперёд", "вперед", "avance"):
            try:
                dist = int(cmd[-1])
            except BaseException:
                dist = 1
            confirm(cmd)
            self.move(FORWARD, distance=dist)
        elif cmd[0] in ("backward", "назад", "recule"):
            try:
                dist = int(cmd[-1])
            except BaseException:
                dist = 1
            confirm(cmd)
            self.move(BACKWARD, distance=dist)
        elif cmd[0] in ("turn", "поворот", 'повернуть', "tourne"):
            if cmd[-1] in ("right", "вправо", "направо", "droite"):
                confirm(cmd)
                self.turn(RIGHT)
            elif cmd[-1] in ("left", "влево", "налево", "gauche"):
                confirm(cmd)
                self.turn(LEFT)
            else:
                confirm(cmd)
                self.turn(RIGHT, degrees=180)
        elif cmd[0] in ("right", "вправо", "направо", "droite"):
            try:
                angle = int(cmd[-1])
            except BaseException:
                angle = 90
            confirm(cmd)
            self.turn(RIGHT, degrees=angle)
        elif cmd[0] in ("left", "влево", "налево", "gauche"):
            try:
                angle = int(cmd[-1])
            except BaseException:
                angle = 90
            confirm(cmd)
            self.turn(LEFT, degrees=angle)
        elif cmd[0]:
            self.say("unknown command")
            # self.say("commands help")
