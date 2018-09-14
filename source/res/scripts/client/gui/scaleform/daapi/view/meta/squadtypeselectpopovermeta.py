# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadTypeSelectPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SquadTypeSelectPopoverMeta(DAAPIModule):

    def selectFight(self, actionName):
        self._printOverrideError('selectFight')

    def getTooltipData(self, itemData):
        self._printOverrideError('getTooltipData')

    def as_updateS(self, items):
        if self._isDAAPIInited():
            return self.flashObject.as_update(items)
