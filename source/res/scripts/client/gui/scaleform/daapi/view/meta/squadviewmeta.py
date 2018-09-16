# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):

    def leaveSquad(self):
        self._printOverrideError('leaveSquad')

    def as_updateBattleTypeS(self, data):
        """
        :param data: Represented by SquadViewHeaderVO (AS)
        """
        return self.flashObject.as_updateBattleType(data) if self._isDAAPIInited() else None

    def as_isFalloutS(self, isFallout):
        return self.flashObject.as_isFallout(isFallout) if self._isDAAPIInited() else None

    def as_updateInviteBtnStateS(self, isEnabled):
        return self.flashObject.as_updateInviteBtnState(isEnabled) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, timer):
        return self.flashObject.as_setCoolDownForReadyButton(timer) if self._isDAAPIInited() else None

    def as_setSimpleTeamSectionDataS(self, data):
        """
        :param data: Represented by SimpleSquadTeamSectionVO (AS)
        """
        return self.flashObject.as_setSimpleTeamSectionData(data) if self._isDAAPIInited() else None
