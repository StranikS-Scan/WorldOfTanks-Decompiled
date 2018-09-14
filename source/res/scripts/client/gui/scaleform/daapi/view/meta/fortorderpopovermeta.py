# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortOrderPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def requestForCreateOrder(self):
        """
        :return :
        """
        self._printOverrideError('requestForCreateOrder')

    def requestForUseOrder(self):
        """
        :return :
        """
        self._printOverrideError('requestForUseOrder')

    def getLeftTime(self):
        """
        :return Number:
        """
        self._printOverrideError('getLeftTime')

    def getLeftTimeStr(self):
        """
        :return String:
        """
        self._printOverrideError('getLeftTimeStr')

    def getLeftTimeTooltip(self):
        """
        :return String:
        """
        self._printOverrideError('getLeftTimeTooltip')

    def openQuest(self, questID):
        """
        :param questID:
        :return :
        """
        self._printOverrideError('openQuest')

    def openOrderDetailsWindow(self):
        """
        :return :
        """
        self._printOverrideError('openOrderDetailsWindow')

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_disableOrderS(self, daisable):
        """
        :param daisable:
        :return :
        """
        return self.flashObject.as_disableOrder(daisable) if self._isDAAPIInited() else None
