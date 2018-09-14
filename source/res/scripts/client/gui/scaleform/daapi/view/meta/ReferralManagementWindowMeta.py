# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReferralManagementWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ReferralManagementWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onInvitesManagementLinkClick(self):
        self._printOverrideError('onInvitesManagementLinkClick')

    def inviteIntoSquad(self, referralID):
        self._printOverrideError('inviteIntoSquad')

    def as_setDataS(self, data):
        """
        :param data: Represented by RefManagementWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTableDataS(self, referrals):
        """
        :param referrals: Represented by DataProvider (AS)
        """
        return self.flashObject.as_setTableData(referrals) if self._isDAAPIInited() else None

    def as_setAwardDataDataS(self, data):
        """
        :param data: Represented by AwardDataDataVO (AS)
        """
        return self.flashObject.as_setAwardDataData(data) if self._isDAAPIInited() else None

    def as_setProgressDataS(self, data):
        """
        :param data: Represented by ComplexProgressIndicatorVO (AS)
        """
        return self.flashObject.as_setProgressData(data) if self._isDAAPIInited() else None

    def as_showAlertS(self, alertStr):
        return self.flashObject.as_showAlert(alertStr) if self._isDAAPIInited() else None
