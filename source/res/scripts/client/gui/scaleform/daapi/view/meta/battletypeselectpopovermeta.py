# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTypeSelectPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleTypeSelectPopoverMeta(DAAPIModule):

    def selectFight(self, actionName):
        self._printOverrideError('selectFight')

    def as_updateS(self, items):
        if self._isDAAPIInited():
            return self.flashObject.as_update(items)
