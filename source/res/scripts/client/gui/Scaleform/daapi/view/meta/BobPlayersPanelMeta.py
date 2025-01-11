# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BobPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class BobPlayersPanelMeta(PlayersPanel):

    def onVoiceChatControlClick(self):
        self._printOverrideError('onVoiceChatControlClick')

    def as_setLeftTeamSkillS(self, iconName, title, description):
        return self.flashObject.as_setLeftTeamSkill(iconName, title, description) if self._isDAAPIInited() else None

    def as_setRightTeamSkillS(self, iconName, title, description):
        return self.flashObject.as_setRightTeamSkill(iconName, title, description) if self._isDAAPIInited() else None

    def as_setBattleStartedS(self, value=False):
        return self.flashObject.as_setBattleStarted(value) if self._isDAAPIInited() else None

    def as_setVoiceChatDataS(self, data):
        return self.flashObject.as_setVoiceChatData(data) if self._isDAAPIInited() else None

    def as_setVoiceChatControlVisibleS(self, value):
        return self.flashObject.as_setVoiceChatControlVisible(value) if self._isDAAPIInited() else None

    def as_setVoiceChatControlSelectedS(self, value):
        return self.flashObject.as_setVoiceChatControlSelected(value) if self._isDAAPIInited() else None
