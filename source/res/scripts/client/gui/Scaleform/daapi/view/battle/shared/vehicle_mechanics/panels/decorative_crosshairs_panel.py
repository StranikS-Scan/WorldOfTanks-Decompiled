# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels/decorative_crosshairs_panel.py
from __future__ import absolute_import
import typing
from gui.Scaleform.daapi.view.meta.DecorativeCrosshairPanelMeta import DecorativeCrosshairPanelMeta
from gui.Scaleform.genConsts.DECORATIVE_CROSSHAIR_CONSTS import DECORATIVE_CROSSHAIR_CONSTS
from items.vehicle_mechanics_types import VehicleMechanicKeys

class DecorativeCrosshairPanel(DecorativeCrosshairPanelMeta):
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {VehicleMechanicKeys.ACCURACY_STACKS: (DECORATIVE_CROSSHAIR_CONSTS.ACCURACY,),
     VehicleMechanicKeys.BATTLE_FURY: (DECORATIVE_CROSSHAIR_CONSTS.FURY,),
     VehicleMechanicKeys.CONCENTRATION_MODE: (DECORATIVE_CROSSHAIR_CONSTS.CONCENTRATION,),
     VehicleMechanicKeys.OVERHEAT_GUN: (DECORATIVE_CROSSHAIR_CONSTS.TEMPERATURE_GUN_OVERHEAT,),
     VehicleMechanicKeys.OVERHEAT_STACKS: (DECORATIVE_CROSSHAIR_CONSTS.OVERHEAT,),
     VehicleMechanicKeys.PILLBOX_SIEGE_MODE: (DECORATIVE_CROSSHAIR_CONSTS.PILLBOX_SIEGE,)}

    def _setIsReplay(self, isReplay):
        pass

    def _setIsVisible(self, isVisible):
        self.as_setVisibleS(isVisible)

    def _setCrosshairScaledPosition(self, position):
        self.as_updateLayoutS(*position)

    def _setCrosshairViewID(self, viewID):
        self.as_updateCrosshairTypeS(viewID)

    def _addMechanicUIComponents(self, mechanicComponents):
        for componentName in mechanicComponents:
            self.as_addDecorCrosshairS(componentName)
