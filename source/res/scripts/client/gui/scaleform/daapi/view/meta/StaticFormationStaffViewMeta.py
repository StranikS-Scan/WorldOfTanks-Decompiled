# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStaffViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StaticFormationStaffViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def showRecriutmentWindow(self):
        self._printOverrideError('showRecriutmentWindow')

    def showInviteWindow(self):
        self._printOverrideError('showInviteWindow')

    def setRecruitmentOpened(self, opened):
        self._printOverrideError('setRecruitmentOpened')

    def removeMe(self):
        self._printOverrideError('removeMe')

    def removeMember(self, id, userName):
        self._printOverrideError('removeMember')

    def assignOfficer(self, id, userName):
        self._printOverrideError('assignOfficer')

    def assignPrivate(self, id, userName):
        self._printOverrideError('assignPrivate')

    def as_setStaticHeaderDataS(self, data):
        """
        :param data: Represented by StaticFormationStaffViewStaticHeaderVO (AS)
        """
        return self.flashObject.as_setStaticHeaderData(data) if self._isDAAPIInited() else None

    def as_updateHeaderDataS(self, data):
        """
        :param data: Represented by StaticFormationStaffViewHeaderVO (AS)
        """
        return self.flashObject.as_updateHeaderData(data) if self._isDAAPIInited() else None

    def as_updateStaffDataS(self, data):
        """
        :param data: Represented by StaticFormationStaffViewStaffVO (AS)
        """
        return self.flashObject.as_updateStaffData(data) if self._isDAAPIInited() else None

    def as_setRecruitmentAvailabilityS(self, available):
        return self.flashObject.as_setRecruitmentAvailability(available) if self._isDAAPIInited() else None
