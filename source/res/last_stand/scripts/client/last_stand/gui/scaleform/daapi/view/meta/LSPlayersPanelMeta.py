# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/LSPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class LSPlayersPanelMeta(PlayersPanel):

    def onVoiceChatClick(self):
        self._printOverrideError('onVoiceChatClick')

    def onTalkDown(self):
        self._printOverrideError('onTalkDown')

    def onTalkUp(self):
        self._printOverrideError('onTalkUp')

    def as_setPlayerPanelInfoS(self, data):
        return self.flashObject.as_setPlayerPanelInfo(data) if self._isDAAPIInited() else None

    def as_setPlayerPanelHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_setPlayerPanelHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setVoiceChatBindingsS(self, chatBind, talkBind):
        return self.flashObject.as_setVoiceChatBindings(chatBind, talkBind) if self._isDAAPIInited() else None

    def as_setVoiceChatActivatedS(self, isActivated):
        return self.flashObject.as_setVoiceChatActivated(isActivated) if self._isDAAPIInited() else None

    def as_setVoiceChatAvailableS(self, isAvailable):
        return self.flashObject.as_setVoiceChatAvailable(isAvailable) if self._isDAAPIInited() else None

    def as_setVoiceChatEnabledS(self, isEnabled):
        return self.flashObject.as_setVoiceChatEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setIsTalkS(self, isTalk):
        return self.flashObject.as_setIsTalk(isTalk) if self._isDAAPIInited() else None

    def as_setPlayerDeadS(self, vehID):
        return self.flashObject.as_setPlayerDead(vehID) if self._isDAAPIInited() else None

    def as_setPostmortemS(self, isPostmortem):
        return self.flashObject.as_setPostmortem(isPostmortem) if self._isDAAPIInited() else None
