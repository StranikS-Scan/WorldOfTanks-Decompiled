# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: survey/scripts/client/SurveyPersonality.py
from survey.gui.game_control.SurveyChannelHandler import SurveyChannelHandler
from gui.shared.system_factory import registerAwardControllerHandler

def preInit():
    registerAwardControllerHandler(SurveyChannelHandler)


def init():
    pass


def start():
    pass


def fini():
    pass
