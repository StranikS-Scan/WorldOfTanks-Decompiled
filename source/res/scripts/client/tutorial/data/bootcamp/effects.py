# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/bootcamp/effects.py
from tutorial.data.effects import EFFECT_TYPE, SimpleEffect, HasTargetEffect

class RequestExclusiveHintEffect(HasTargetEffect):

    def __init__(self, componentID, soundID, conditions=None):
        super(RequestExclusiveHintEffect, self).__init__(componentID, EFFECT_TYPE.REQUEST_EXCLUSIVE_HINT, conditions=conditions)
        self.__soundID = soundID

    def getSoundID(self):
        return self.__soundID


class StartAssistantEffect(SimpleEffect):

    def __init__(self, hints, conditions=None):
        super(StartAssistantEffect, self).__init__(EFFECT_TYPE.START_ASSISTANT, conditions=conditions)
        self.__hints = hints

    def getHints(self):
        return self.__hints
