# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels/decorative_crosshairs_panel.py
import typing
from gui.Scaleform.daapi.view.meta.DecorativeCrosshairPanelMeta import DecorativeCrosshairPanelMeta
from gui.Scaleform.genConsts.DECORATIVE_CROSSHAIR_CONSTS import DECORATIVE_CROSSHAIR_CONSTS
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class DecorativeCrosshairPanel(DecorativeCrosshairPanelMeta):
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {VehicleMechanic.CONCENTRATION_MODE: (DECORATIVE_CROSSHAIR_CONSTS.CONCENTRATION,),
     VehicleMechanic.PILLBOX_SIEGE_MODE: (DECORATIVE_CROSSHAIR_CONSTS.PILLBOX_SIEGE,),
     VehicleMechanic.ACCURACY_STACKS: (DECORATIVE_CROSSHAIR_CONSTS.ACCURACY,),
     VehicleMechanic.OVERHEAT_STACKS: (DECORATIVE_CROSSHAIR_CONSTS.OVERHEAT,),
     VehicleMechanic.BATTLE_FURY: (DECORATIVE_CROSSHAIR_CONSTS.FURY,)}

    def _setIsReplay(self, isReplay):
        pass

    def _setIsVisible(self, isVisible):
        self.as_setVisibleS(isVisible)

    def _setCrosshairScaledPosition(self, position):
        self.as_updateLayoutS(*position)

    def _setCrosshairViewID(self, viewID):
        self.as_updateCrosshairTypeS(viewID)

    def _addMechanicUIComponent(self, mechanicComponents):
        for componentName in mechanicComponents:
            self.as_addDecorCrosshairS(componentName)
