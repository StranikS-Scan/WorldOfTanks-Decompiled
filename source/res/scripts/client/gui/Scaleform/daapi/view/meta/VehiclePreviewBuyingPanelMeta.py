# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewBuyingPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewBuyingPanelMeta(BaseDAAPIComponent):

    def onBuyOrResearchClick(self):
        self._printOverrideError('onBuyOrResearchClick')

    def onCarouselVehilceSelected(self, intCD):
        self._printOverrideError('onCarouselVehilceSelected')

    def showTooltip(self, intCD, itemType):
        self._printOverrideError('showTooltip')

    def as_setBuyDataS(self, data):
        return self.flashObject.as_setBuyData(data) if self._isDAAPIInited() else None

    def as_setSetItemsDataS(self, data):
        return self.flashObject.as_setSetItemsData(data) if self._isDAAPIInited() else None

    def as_setSetVehiclesDataS(self, data):
        return self.flashObject.as_setSetVehiclesData(data) if self._isDAAPIInited() else None

    def as_updateLeftTimeS(self, formattedTime, tooltip='', hasHoursAndMinutes=False):
        return self.flashObject.as_updateLeftTime(formattedTime, tooltip, hasHoursAndMinutes) if self._isDAAPIInited() else None
