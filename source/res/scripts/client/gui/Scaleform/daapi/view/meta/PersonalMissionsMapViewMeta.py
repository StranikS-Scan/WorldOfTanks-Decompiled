# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsMapViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PersonalMissionsMapViewMeta(BaseDAAPIComponent):

    def onRegionClick(self, id):
        self._printOverrideError('onRegionClick')

    def as_setPlanDataS(self, planData):
        return self.flashObject.as_setPlanData(planData) if self._isDAAPIInited() else None
