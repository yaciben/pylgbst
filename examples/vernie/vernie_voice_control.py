from enum import Enum

from vernie import *
import speech_recognition as sr

robot = Vernie(language='fr-FR')

command_filename = "vernie.commands.fr"


class Mode(Enum):
    Converse = "Converse",
    Command = "Command"


def confirmation(command):
    robot.say(" ".join(command))


def send_command(cmd):
    robot.interpret_command(cmd, confirmation)


def read_commands_from_file(command_filename):
    with open(os.path.join(os.path.dirname(__file__), command_filename)) as fhd:
        commands = fhd.read()
    return commands


def get_speech():
    global text, response
    with microphone as source:
        text = "Je t'écoute"
        print(text)
        say(text)
        recognizer.adjust_for_ambient_noise(source)
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


if __name__ == '__main__':
    language = 'fr-FR'
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    finished = False
    mode = Mode.Converse

    robot.say("Bonjour ! Dis le mot \"commande\" pour me controler")

    while not finished:

        # if command == "MARCHE":
        #     pass

        response = get_speech()

        if response["success"] and (response["transcription"] is not None):
            text = "Tu as dis : \"{}\"".format(response["transcription"])
            print(text)
        else:
            text = "Je suis désolé, je n'ai pas compris. Peux-tu répéter s'il te plait ?"
            print(text)

        say(text=text)

        if response["success"] and response["transcription"] is not None and response["transcription"].lower() == "terminer":
            text = "Au revoir ! Terminé !"
            print(text)
            say(text)
            finished = True

