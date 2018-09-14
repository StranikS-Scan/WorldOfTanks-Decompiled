# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTypeSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class BattleTypeSelectPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def selectFight(self, actionName):
        """
        :param actionName:
        :return :
        """
        self._printOverrideError('selectFight')

    def demoClick(self):
        """
        :return :
        """
        self._printOverrideError('demoClick')

    def getTooltipData(self, itemData):
        """
        :param itemData:
        :return String:
        """
        self._printOverrideError('getTooltipData')

    def as_updateS(self, items, isShowDemonstrator, demonstratorEnabled):
        """
        :param items:
        :param isShowDemonstrator:
        :param demonstratorEnabled:
        :return :
        """
        return self.flashObject.as_update(items, isShowDemonstrator, demonstratorEnabled) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        """
        :param description:
        :param hyperlink:
        :return :
        """
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
