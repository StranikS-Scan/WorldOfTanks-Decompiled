# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/VoiceChatManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VoiceChatManagerMeta(BaseDAAPIComponent):

    def isPlayerSpeaking(self, accountDBID):
        self._printOverrideError('isPlayerSpeaking')

    def isVivox(self):
        self._printOverrideError('isVivox')

    def isYY(self):
        self._printOverrideError('isYY')

    def isVOIPEnabled(self):
        self._printOverrideError('isVOIPEnabled')

    def isVOIPAvailable(self):
        self._printOverrideError('isVOIPAvailable')

    def as_onPlayerSpeakS(self, accountDBID, isSpeak, isHimseljoinUnitButtonf):
        return self.flashObject.as_onPlayerSpeak(accountDBID, isSpeak, isHimseljoinUnitButtonf) if self._isDAAPIInited() else None
