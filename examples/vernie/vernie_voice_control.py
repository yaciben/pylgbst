import csv
from enum import Enum

from vernie import *
import speech_recognition as sr

csv_dialect = csv.unix_dialect
csv_dialect.quoting = csv.QUOTE_NONE


class Mode(Enum):
    Converse = "Converse",
    Command = "Command",


class Keywords(Enum):
    # Command = "commande"
    # Command = "ok"
    Command = "go"
    Finished = "terminer"


def confirmation(command):
    robot.say(" ".join(command))


def send_command(cmd):
    robot.interpret_command(cmd, confirmation)


def read_commands_from_file(command_filename):
    with open(os.path.join(os.path.dirname(__file__), command_filename)) as fhd:
        commands = fhd.read()
    return commands


def notify_listening(beep=True):
    if beep:
        duration = 55 / 1000  # millis / 1000
        frequency = 500  # Hertz
        os.system('play -n -t alsa synth %s sin %s &>/dev/null' % (duration, frequency))
    else:
        text = "Je t'écoute"
        robot.say(text)


def get_speech():
    global text, response
    with microphone as source:
        notify_listening()
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Prêt")
        audio = recognizer.listen(source, phrase_time_limit=3)
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio, language=language)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def preprocess_command(command, numbers_dict=None):
    new_command = command
    if numbers_dict:
        command_split = command.split(sep=' ')
        if command_split.__len__() == 2:
            if command_split[1] in numbers_dict.keys():
                new_command = ' '.join([command_split[0], numbers_dict.get(command_split[1])])
    return new_command


def load_numbers_dict(language):
    filepath = 'number_2_words_mapping.csv'
    data = {}
    with open(file=filepath, mode='r') as fin:
        reader = csv.reader(fin, skipinitialspace=True, dialect=csv_dialect)
        first_line = True
        for row in reader:
            if first_line:
                # header row
                first_line = False
                language_column = row.index(language.split('-')[0])
            else:
                data[row[language_column].lower()] = row[0]
    return data


if __name__ == '__main__':

    language = 'fr-FR'
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    numbers_dict = load_numbers_dict(language=language)

    robot = Vernie(language=language)

    command_filename = "vernie.commands.fr"

    finished = False
    mode = Mode.Converse

    robot.say(phrase="Bonjour ! Dis le mot \"{}\" pour me contrôler".format(Keywords.Command.value))

    while not finished:

        try:
            response = get_speech()

            transcription_ = response["transcription"]
            success_ = response["success"]

            if mode == Mode.Converse:
                if success_ and (transcription_ is not None):
                    text = "Tu as dis : \"{}\"".format(transcription_)

                    if transcription_.lower() == Keywords.Finished.value:
                        text = ". ".join([text, "Au revoir ! Terminé !"])
                        finished = True

                    if transcription_.lower() == Keywords.Command.value:
                        text = ". ".join([text, "Mode commande activé !"])
                        mode = Mode.Command

                else:
                    text = "Je n'ai pas compris. Peux-tu répéter s'il te plait ?"

                robot.say(phrase=text)

            elif mode == Mode.Command:
                command = preprocess_command(transcription_, numbers_dict=numbers_dict)
                send_command(command)

            else:
                raise Exception("Unsupported mode: {}".format(mode))
        except BaseException as e:
            mode_name = "conversation" if mode is Mode.Converse else "commande"
            robot.say(phrase="Une erreur est survenue, je reprends en mode {}".format(mode_name))
            # mode = Mode.Converse
