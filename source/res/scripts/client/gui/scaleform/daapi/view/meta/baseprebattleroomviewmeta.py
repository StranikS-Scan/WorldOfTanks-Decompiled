# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BasePrebattleRoomViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyView import AbstractRallyView

class BasePrebattleRoomViewMeta(AbstractRallyView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractRallyView
    null
    """

    def requestToReady(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('requestToReady')

    def requestToLeave(self):
        """
        :return :
        """
        self._printOverrideError('requestToLeave')

    def showPrebattleSendInvitesWindow(self):
        """
        :return :
        """
        self._printOverrideError('showPrebattleSendInvitesWindow')

    def canSendInvite(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canSendInvite')

    def canKickPlayer(self):
        """
        :return Boolean:
        """
        self._printOverrideError('canKickPlayer')

    def isPlayerReady(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isPlayerReady')

    def isPlayerCreator(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isPlayerCreator')

    def isReadyBtnEnabled(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isReadyBtnEnabled')

    def isLeaveBtnEnabled(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isLeaveBtnEnabled')

    def getClientID(self):
        """
        :return Number:
        """
        self._printOverrideError('getClientID')

    def as_setRosterListS(self, team, assigned, rosters):
        """
        :param team:
        :param assigned:
        :param rosters:
        :return :
        """
        return self.flashObject.as_setRosterList(team, assigned, rosters) if self._isDAAPIInited() else None

    def as_setPlayerStateS(self, team, assigned, data):
        """
        :param team:
        :param assigned:
        :param data:
        :return :
        """
        return self.flashObject.as_setPlayerState(team, assigned, data) if self._isDAAPIInited() else None

    def as_enableLeaveBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableLeaveBtn(value) if self._isDAAPIInited() else None

    def as_enableReadyBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableReadyBtn(value) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCoolDownForReadyButton(value) if self._isDAAPIInited() else None

    def as_resetReadyButtonCoolDownS(self):
        """
        :return :
        """
        return self.flashObject.as_resetReadyButtonCoolDown() if self._isDAAPIInited() else None

    def as_toggleReadyBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_toggleReadyBtn(value) if self._isDAAPIInited() else None

    def as_refreshPermissionsS(self):
        """
        :return :
        """
        return self.flashObject.as_refreshPermissions() if self._isDAAPIInited() else None
