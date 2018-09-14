# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyRoomViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyView import BaseRallyView

class BaseRallyRoomViewMeta(BaseRallyView):

    def assignSlotRequest(self, slotIndex, playerId):
        self._printOverrideError('assignSlotRequest')

    def leaveSlotRequest(self, playerId):
        self._printOverrideError('leaveSlotRequest')

    def onSlotsHighlihgtingNeed(self, databaseID):
        self._printOverrideError('onSlotsHighlihgtingNeed')

    def chooseVehicleRequest(self):
        self._printOverrideError('chooseVehicleRequest')

    def inviteFriendRequest(self):
        self._printOverrideError('inviteFriendRequest')

    def toggleReadyStateRequest(self):
        self._printOverrideError('toggleReadyStateRequest')

    def ignoreUserRequest(self, slotIndex):
        self._printOverrideError('ignoreUserRequest')

    def editDescriptionRequest(self, description):
        self._printOverrideError('editDescriptionRequest')

    def showFAQWindow(self):
        self._printOverrideError('showFAQWindow')

    def as_updateRallyS(self, rally):
        """
        :param rally: Represented by IRallyVO (AS)
        """
        return self.flashObject.as_updateRally(rally) if self._isDAAPIInited() else None

    def as_setMembersS(self, hasRestrictions, slots):
        """
        :param slots: Represented by Array (AS)
        """
        return self.flashObject.as_setMembers(hasRestrictions, slots) if self._isDAAPIInited() else None

    def as_setMemberStatusS(self, slotIndex, status):
        return self.flashObject.as_setMemberStatus(slotIndex, status) if self._isDAAPIInited() else None

    def as_setMemberOfflineS(self, slotIndex, isOffline):
        return self.flashObject.as_setMemberOffline(slotIndex, isOffline) if self._isDAAPIInited() else None

    def as_setMemberVehicleS(self, slotIdx, slotCost, veh):
        """
        :param veh: Represented by VehicleVO (AS)
        """
        return self.flashObject.as_setMemberVehicle(slotIdx, slotCost, veh) if self._isDAAPIInited() else None

    def as_setActionButtonStateS(self, data):
        """
        :param data: Represented by ActionButtonVO (AS)
        """
        return self.flashObject.as_setActionButtonState(data) if self._isDAAPIInited() else None

    def as_setCommentS(self, value):
        return self.flashObject.as_setComment(value) if self._isDAAPIInited() else None

    def as_getCandidatesDPS(self):
        return self.flashObject.as_getCandidatesDP() if self._isDAAPIInited() else None

    def as_highlightSlotsS(self, slotsIdx):
        """
        :param slotsIdx: Represented by Array (AS)
        """
        return self.flashObject.as_highlightSlots(slotsIdx) if self._isDAAPIInited() else None

    def as_setVehiclesTitleS(self, value, tooltip):
        """
        :param tooltip: Represented by TooltipDataVO (AS)
        """
        return self.flashObject.as_setVehiclesTitle(value, tooltip) if self._isDAAPIInited() else None
