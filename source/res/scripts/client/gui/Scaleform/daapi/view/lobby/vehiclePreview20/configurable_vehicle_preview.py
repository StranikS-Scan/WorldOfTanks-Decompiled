# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/configurable_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
from shared_utils import CONST_CONTAINER

class OptionalBlocks(CONST_CONTAINER):
    BUYING_PANEL = 'buyingPanel'
    CLOSE_BUTTON = 'closeBtn'
    ALL = (BUYING_PANEL, CLOSE_BUTTON)


class ConfigurableVehiclePreview20(VehiclePreview20):

    def __init__(self, ctx):
        super(ConfigurableVehiclePreview20, self).__init__(ctx)
        self.__hiddenBlocks = ctx.get('hiddenBlocks')
        self.__showCloseBtn = OptionalBlocks.CLOSE_BUTTON not in self.__hiddenBlocks

    def setBottomPanel(self):
        if OptionalBlocks.BUYING_PANEL in self.__hiddenBlocks:
            self.as_setBottomPanelS('')
        else:
            super(ConfigurableVehiclePreview20, self).setBottomPanel()

    def _getData(self):
        result = super(ConfigurableVehiclePreview20, self)._getData()
        result.update({'showCloseBtn': self.__showCloseBtn})
        return result
