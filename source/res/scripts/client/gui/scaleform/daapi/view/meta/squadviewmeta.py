# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):

    def leaveSquad(self):
        self._printOverrideError('leaveSquad')

    def as_updateBattleTypeInfoS(self, tooltip, isVisible):
        return self.flashObject.as_updateBattleTypeInfo(tooltip, isVisible) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, isEventEnabled, isNew):
        return self.flashObject.as_updateBattleType(battleTypeName, isEventEnabled, isNew) if self._isDAAPIInited() else None

    def as_isFalloutS(self, isFallout):
        return self.flashObject.as_isFallout(isFallout) if self._isDAAPIInited() else None

    def as_updateInviteBtnStateS(self, isEnabled):
        return self.flashObject.as_updateInviteBtnState(isEnabled) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, timer):
        return self.flashObject.as_setCoolDownForReadyButton(timer) if self._isDAAPIInited() else None
