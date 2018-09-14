# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTypeSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class BattleTypeSelectPopoverMeta(SmartPopOverView):

    def selectFight(self, actionName):
        self._printOverrideError('selectFight')

    def demoClick(self):
        self._printOverrideError('demoClick')

    def getTooltipData(self, itemData):
        self._printOverrideError('getTooltipData')

    def as_updateS(self, items, isShowDemonstrator, demonstratorEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_update(items, isShowDemonstrator, demonstratorEnabled)

    def as_setDemonstrationEnabledS(self, demonstratorEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_setDemonstrationEnabled(demonstratorEnabled)

    def as_showMiniClientInfoS(self, description, hyperlink):
        if self._isDAAPIInited():
            return self.flashObject.as_showMiniClientInfo(description, hyperlink)
