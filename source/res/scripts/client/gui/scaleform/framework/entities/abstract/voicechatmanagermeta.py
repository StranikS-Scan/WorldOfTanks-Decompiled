# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/VoiceChatManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VoiceChatManagerMeta(DAAPIModule):

    def isPlayerSpeaking(self, accountDBID):
        self._printOverrideError('isPlayerSpeaking')

    def isVivox(self):
        self._printOverrideError('isVivox')

    def isYY(self):
        self._printOverrideError('isYY')

    def isVOIPEnabled(self):
        self._printOverrideError('isVOIPEnabled')

    def as_onPlayerSpeakS(self, accountDBID, isSpeak, isHimself):
        if self._isDAAPIInited():
            return self.flashObject.as_onPlayerSpeak(accountDBID, isSpeak, isHimself)
