# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStatsViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationStatsViewMeta(DAAPIModule):

    def selectSeason(self, index):
        self._printOverrideError('selectSeason')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setStatsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setStats(data)
