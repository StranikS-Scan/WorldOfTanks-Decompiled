# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):

    def leaveSquad(self):
        self._printOverrideError('leaveSquad')

    def excludePlayer(self, index):
        self._printOverrideError('excludePlayer')

    def as_updateBattleTypeS(self, data):
        return self.flashObject.as_updateBattleType(data) if self._isDAAPIInited() else None

    def as_updateInviteBtnStateS(self, isEnabled):
        return self.flashObject.as_updateInviteBtnState(isEnabled) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, timer):
        return self.flashObject.as_setCoolDownForReadyButton(timer) if self._isDAAPIInited() else None

    def as_setSimpleTeamSectionDataS(self, data):
        return self.flashObject.as_setSimpleTeamSectionData(data) if self._isDAAPIInited() else None
