# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TmenXpPanel.py
import logging
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.hangar_presets.hangar_gui_helpers import ifComponentAvailable
from gui.Scaleform.daapi.view.meta.TmenXpPanelMeta import TmenXpPanelMeta
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.utils import decorators
_logger = logging.getLogger(__name__)

class TmenXpPanel(TmenXpPanelMeta):

    def _populate(self):
        super(TmenXpPanel, self)._populate()
        g_currentVehicle.onChanged += self._onVehicleChange
        self._onVehicleChange()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChange
        super(TmenXpPanel, self)._dispose()

    @decorators.adisp_process('updateTankmen')
    def accelerateTmenXp(self, selected):
        vehicle = g_currentVehicle.item
        result = yield VehicleTmenXPAccelerator(vehicle, bool(selected)).request()
        if not result.success:
            self.as_setTankmenXpPanelS(vehicle.isElite, vehicle.isXPToTman)
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @ifComponentAvailable(HANGAR_CONSTS.TANK_MEN_XP)
    def _onVehicleChange(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            self.as_setTankmenXpPanelS(False, False)
            _logger.debug('Do not show TMenXPPanel: No current vehicle')
            return
        else:
            self.as_setTankmenXpPanelS(vehicle.isElite, vehicle.isXPToTman)
            return
