# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyWindowMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleWindow import PrebattleWindow

class CompanyWindowMeta(PrebattleWindow):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends PrebattleWindow
    """

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
        return self.flashObject.as_setDivisionsList(data, selected) if self._isDAAPIInited() else None

    def as_setOpenedS(self, isOpened):
        return self.flashObject.as_setOpened(isOpened) if self._isDAAPIInited() else None

    def as_setCommentS(self, comment):
        return self.flashObject.as_setComment(comment) if self._isDAAPIInited() else None

    def as_setDivisionS(self, divisionID):
        return self.flashObject.as_setDivision(divisionID) if self._isDAAPIInited() else None

    def as_setTotalLimitLabelsS(self, totalLevel, levelRange):
        return self.flashObject.as_setTotalLimitLabels(totalLevel, levelRange) if self._isDAAPIInited() else None

    def as_setMaxCountLimitLabelS(self, label):
        return self.flashObject.as_setMaxCountLimitLabel(label) if self._isDAAPIInited() else None

    def as_setClassesLimitsS(self, data):
        return self.flashObject.as_setClassesLimits(data) if self._isDAAPIInited() else None

    def as_setInvalidVehiclesS(self, data):
        return self.flashObject.as_setInvalidVehicles(data) if self._isDAAPIInited() else None

    def as_setChangeSettingCoolDownS(self, coolDown):
        return self.flashObject.as_setChangeSettingCoolDown(coolDown) if self._isDAAPIInited() else None
