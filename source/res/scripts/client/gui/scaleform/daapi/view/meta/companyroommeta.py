# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyRoomMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.BasePrebattleRoomView import BasePrebattleRoomView

class CompanyRoomMeta(BasePrebattleRoomView):

    def requestToAssign(self, pID):
        self._printOverrideError('requestToAssign')

    def requestToUnassign(self, pID):
        self._printOverrideError('requestToUnassign')

    def requestToChangeOpened(self, isOpened):
        self._printOverrideError('requestToChangeOpened')

    def requestToChangeComment(self, comment):
        self._printOverrideError('requestToChangeComment')

    def requestToChangeDivision(self, divisionID):
        self._printOverrideError('requestToChangeDivision')

    def getCompanyName(self):
        self._printOverrideError('getCompanyName')

    def canMoveToAssigned(self):
        self._printOverrideError('canMoveToAssigned')

    def canMoveToUnassigned(self):
        self._printOverrideError('canMoveToUnassigned')

    def canMakeOpenedClosed(self):
        self._printOverrideError('canMakeOpenedClosed')

    def canChangeComment(self):
        self._printOverrideError('canChangeComment')

    def canChangeDivision(self):
        self._printOverrideError('canChangeDivision')

    def as_setDivisionsListS(self, data, selected):
        if self._isDAAPIInited():
            return self.flashObject.as_setDivisionsList(data, selected)

    def as_setOpenedS(self, isOpened):
        if self._isDAAPIInited():
            return self.flashObject.as_setOpened(isOpened)

    def as_setCommentS(self, comment):
        if self._isDAAPIInited():
            return self.flashObject.as_setComment(comment)

    def as_setDivisionS(self, divisionID):
        if self._isDAAPIInited():
            return self.flashObject.as_setDivision(divisionID)

    def as_setTotalLimitLabelsS(self, totalLevel):
        if self._isDAAPIInited():
            return self.flashObject.as_setTotalLimitLabels(totalLevel)

    def as_setMaxCountLimitLabelS(self, label):
        if self._isDAAPIInited():
            return self.flashObject.as_setMaxCountLimitLabel(label)

    def as_setInvalidVehiclesS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInvalidVehicles(data)

    def as_setChangeSettingCoolDownS(self, coolDown):
        if self._isDAAPIInited():
            return self.flashObject.as_setChangeSettingCoolDown(coolDown)

    def as_setHeaderDataS(self, viewType, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setHeaderData(viewType, value)
