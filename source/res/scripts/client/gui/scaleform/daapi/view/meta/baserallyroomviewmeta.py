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
        if self._isDAAPIInited():
            return self.flashObject.as_updateRally(rally)

    def as_setMembersS(self, hasRestrictions, slots):
        if self._isDAAPIInited():
            return self.flashObject.as_setMembers(hasRestrictions, slots)

    def as_setMemberStatusS(self, slotIndex, status):
        if self._isDAAPIInited():
            return self.flashObject.as_setMemberStatus(slotIndex, status)

    def as_setMemberOfflineS(self, slotIndex, isOffline):
        if self._isDAAPIInited():
            return self.flashObject.as_setMemberOffline(slotIndex, isOffline)

    def as_setMemberVehicleS(self, slotIdx, slotCost, veh):
        if self._isDAAPIInited():
            return self.flashObject.as_setMemberVehicle(slotIdx, slotCost, veh)

    def as_setActionButtonStateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setActionButtonState(data)

    def as_setCommentS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setComment(value)

    def as_getCandidatesDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getCandidatesDP()

    def as_highlightSlotsS(self, slotsIdx):
        if self._isDAAPIInited():
            return self.flashObject.as_highlightSlots(slotsIdx)

    def as_setVehiclesTitleS(self, value, tooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehiclesTitle(value, tooltip)
