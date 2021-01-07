# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/sound_model.py
from frameworks.wulf import ViewModel

class SoundModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SoundModel, self).__init__(properties=properties, commands=commands)

    def getIsVoiceDisabled(self):
        return self._getBool(0)

    def setIsVoiceDisabled(self, value):
        self._setBool(0, value)

    def getIsMutedByUser(self):
        return self._getBool(1)

    def setIsMutedByUser(self, value):
        self._setBool(1, value)

    def getIsSpeaking(self):
        return self._getBool(2)

    def setIsSpeaking(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(SoundModel, self)._initialize()
        self._addBoolProperty('isVoiceDisabled', False)
        self._addBoolProperty('isMutedByUser', False)
        self._addBoolProperty('isSpeaking', False)
