# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTypeSelectPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleTypeSelectPopoverMeta(DAAPIModule):

    def selectFight(self, actionName):
        self._printOverrideError('selectFight')

    def demoClick(self):
        self._printOverrideError('demoClick')

    def as_updateS(self, items, isShowDemonstrator, demonstratorEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_update(items, isShowDemonstrator, demonstratorEnabled)

    def as_setDemonstrationEnabledS(self, demonstratorEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_setDemonstrationEnabled(demonstratorEnabled)
