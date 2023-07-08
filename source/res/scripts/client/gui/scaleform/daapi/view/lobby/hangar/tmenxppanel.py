# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TmenXpPanel.py
import logging
from CurrentVehicle import g_currentVehicle
from gui.hangar_presets.hangar_gui_helpers import ifComponentAvailable
from gui.Scaleform.daapi.view.meta.TmenXpPanelMeta import TmenXpPanelMeta
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
_logger = logging.getLogger(__name__)

class TmenXpPanel(TmenXpPanelMeta):

    def _populate(self):
        super(TmenXpPanel, self)._populate()
        g_currentVehicle.onChanged += self._onVehicleChange
        self._onVehicleChange()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChange
        super(TmenXpPanel, self)._dispose()

    @ifComponentAvailable(HANGAR_CONSTS.TANK_MEN_XP)
    def _onVehicleChange(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            self.as_setTankmenXpPanelS(False)
            _logger.debug('Do not show TMenXPPanel: No current vehicle')
            return
        else:
            self.as_setTankmenXpPanelS(vehicle.isXPToTman)
            return
