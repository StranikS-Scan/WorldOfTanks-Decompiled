# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/voice_chat_settings_model.py
from frameworks.wulf import ViewModel

class VoiceChatSettingsModel(ViewModel):
    __slots__ = ('switchVoiceChat',)

    def __init__(self, properties=1, commands=1):
        super(VoiceChatSettingsModel, self).__init__(properties=properties, commands=commands)

    def getIsVoiceChatEnabled(self):
        return self._getBool(0)

    def setIsVoiceChatEnabled(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(VoiceChatSettingsModel, self)._initialize()
        self._addBoolProperty('isVoiceChatEnabled', False)
        self.switchVoiceChat = self._addCommand('switchVoiceChat')
