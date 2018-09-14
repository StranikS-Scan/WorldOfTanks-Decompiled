# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AccountPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class AccountPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def openBoostersWindow(self, slotId):
        """
        :param slotId:
        :return :
        """
        self._printOverrideError('openBoostersWindow')

    def openClanResearch(self):
        """
        :return :
        """
        self._printOverrideError('openClanResearch')

    def openRequestWindow(self):
        """
        :return :
        """
        self._printOverrideError('openRequestWindow')

    def openInviteWindow(self):
        """
        :return :
        """
        self._printOverrideError('openInviteWindow')

    def openClanStatistic(self):
        """
        :return :
        """
        self._printOverrideError('openClanStatistic')

    def openCrewStatistic(self):
        """
        :return :
        """
        self._printOverrideError('openCrewStatistic')

    def openReferralManagement(self):
        """
        :return :
        """
        self._printOverrideError('openReferralManagement')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setClanData(data) if self._isDAAPIInited() else None

    def as_setCrewDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setCrewData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, emblemId):
        """
        :param emblemId:
        :return :
        """
        return self.flashObject.as_setClanEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setCrewEmblemS(self, emblemId):
        """
        :param emblemId:
        :return :
        """
        return self.flashObject.as_setCrewEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setReferralDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setReferralData(data) if self._isDAAPIInited() else None
