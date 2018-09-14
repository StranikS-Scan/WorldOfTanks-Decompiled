# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyRoomViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyView import BaseRallyView

class BaseRallyRoomViewMeta(BaseRallyView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyView
    null
    """

    def assignSlotRequest(self, slotIndex, playerId):
        """
        :param slotIndex:
        :param playerId:
        :return :
        """
        self._printOverrideError('assignSlotRequest')

    def leaveSlotRequest(self, playerId):
        """
        :param playerId:
        :return :
        """
        self._printOverrideError('leaveSlotRequest')

    def onSlotsHighlihgtingNeed(self, databaseID):
        """
        :param databaseID:
        :return Array:
        """
        self._printOverrideError('onSlotsHighlihgtingNeed')

    def chooseVehicleRequest(self):
        """
        :return :
        """
        self._printOverrideError('chooseVehicleRequest')

    def inviteFriendRequest(self):
        """
        :return :
        """
        self._printOverrideError('inviteFriendRequest')

    def toggleReadyStateRequest(self):
        """
        :return :
        """
        self._printOverrideError('toggleReadyStateRequest')

    def ignoreUserRequest(self, slotIndex):
        """
        :param slotIndex:
        :return :
        """
        self._printOverrideError('ignoreUserRequest')

    def editDescriptionRequest(self, description):
        """
        :param description:
        :return :
        """
        self._printOverrideError('editDescriptionRequest')

    def showFAQWindow(self):
        """
        :return :
        """
        self._printOverrideError('showFAQWindow')

    def as_updateRallyS(self, rally):
        """
        :param rally:
        :return :
        """
        return self.flashObject.as_updateRally(rally) if self._isDAAPIInited() else None

    def as_setMembersS(self, hasRestrictions, slots):
        """
        :param hasRestrictions:
        :param slots:
        :return :
        """
        return self.flashObject.as_setMembers(hasRestrictions, slots) if self._isDAAPIInited() else None

    def as_setMemberStatusS(self, slotIndex, status):
        """
        :param slotIndex:
        :param status:
        :return :
        """
        return self.flashObject.as_setMemberStatus(slotIndex, status) if self._isDAAPIInited() else None

    def as_setMemberOfflineS(self, slotIndex, isOffline):
        """
        :param slotIndex:
        :param isOffline:
        :return :
        """
        return self.flashObject.as_setMemberOffline(slotIndex, isOffline) if self._isDAAPIInited() else None

    def as_setMemberVehicleS(self, slotIdx, slotCost, veh):
        """
        :param slotIdx:
        :param slotCost:
        :param veh:
        :return :
        """
        return self.flashObject.as_setMemberVehicle(slotIdx, slotCost, veh) if self._isDAAPIInited() else None

    def as_setActionButtonStateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setActionButtonState(data) if self._isDAAPIInited() else None

    def as_setCommentS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setComment(value) if self._isDAAPIInited() else None

    def as_getCandidatesDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getCandidatesDP() if self._isDAAPIInited() else None

    def as_highlightSlotsS(self, slotsIdx):
        """
        :param slotsIdx:
        :return :
        """
        return self.flashObject.as_highlightSlots(slotsIdx) if self._isDAAPIInited() else None

    def as_setVehiclesTitleS(self, value, tooltip):
        """
        :param value:
        :param tooltip:
        :return :
        """
        return self.flashObject.as_setVehiclesTitle(value, tooltip) if self._isDAAPIInited() else None
