# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    null
    """

    def leaveSquad(self):
        """
        :return :
        """
        self._printOverrideError('leaveSquad')

    def as_updateBattleTypeS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateBattleType(data) if self._isDAAPIInited() else None

    def as_isFalloutS(self, isFallout):
        """
        :param isFallout:
        :return :
        """
        return self.flashObject.as_isFallout(isFallout) if self._isDAAPIInited() else None

    def as_updateInviteBtnStateS(self, isEnabled):
        """
        :param isEnabled:
        :return :
        """
        return self.flashObject.as_updateInviteBtnState(isEnabled) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, timer):
        """
        :param timer:
        :return :
        """
        return self.flashObject.as_setCoolDownForReadyButton(timer) if self._isDAAPIInited() else None

    def as_setSimpleTeamSectionDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSimpleTeamSectionData(data) if self._isDAAPIInited() else None
