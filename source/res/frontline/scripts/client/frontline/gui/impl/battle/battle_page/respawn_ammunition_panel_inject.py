# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/battle/battle_page/respawn_ammunition_panel_inject.py
import BigWorld
from frontline.gui.battle_control.controllers.frontline_respawn_ctrl import IFrontlineRespawnView
from frontline.gui.impl.battle.battle_page.respawn_ammunition_panel_view import RespawnAmmunitionPanelView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor, hasAliveInject
from frontline.gui.battle_control.controllers.base_respawn_ctrl import IRespawnView
from gui.battle_control.gui_vehicle_builder import VehicleBuilder
from gui.shared.gui_items.artefacts import BattleAbility
from gui.veh_post_progression.sounds import playSound, Sounds
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class RespawnAmmunitionPanelInject(InjectComponentAdaptor, IRespawnView):
    __slots__ = ('_vehicle',)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RespawnAmmunitionPanelInject, self).__init__()
        self._vehicle = None
        return

    def show(self, selectedID, vehs, cooldowns, limits=0):
        self._updateGuiVehicle(vehs[selectedID], {})
        self._createInjectView(self._vehicle)

    def hide(self):
        self._destroyInjected()
        self._vehicle = None
        return

    @hasAliveInject()
    def setRespawnInfoExt(self, vehInfo, setupIndexes):
        if not self.__needVehicleInvalidation(vehInfo, setupIndexes):
            return
        self._updateGuiVehicle(vehInfo, setupIndexes)
        self._injectView.updateViewVehicle(self._vehicle, False)

    def _onPopulate(self):
        pass

    def _addInjectContentListeners(self):
        self._injectView.onSwitchLayout += self.__onSwitchLayout

    def _removeInjectContentListeners(self):
        self._injectView.onSwitchLayout -= self.__onSwitchLayout

    def _makeInjectView(self, vehicle):
        return RespawnAmmunitionPanelView(vehicle)

    def _updateGuiVehicle(self, vehicleInfo, setupIndexes):
        builder = VehicleBuilder()
        builder.setStrCD(vehicleInfo.strCD)
        builder.setShells(vehicleInfo.strCD, vehicleInfo.vehSetups)
        builder.setCrew(vehicleInfo.crewDescrs)
        actualSetupIndexes = vehicleInfo.vehSetupsIndexes.copy()
        actualSetupIndexes.update(setupIndexes)
        builder.setAmmunitionSetups(vehicleInfo.vehSetups, actualSetupIndexes)
        builder.setRoleSlot(vehicleInfo.customRoleSlotTypeId)
        builder.setPostProgressionState(vehicleInfo.vehPostProgression, vehicleInfo.disabledSwitchGroupIDs)
        builder.setModifiers(self.__sessionProvider.arenaVisitor.getArenaModifiers())
        self._vehicle = builder.getResult()

    def __onSwitchLayout(self, vehCD, groupID, layoutIdx):
        self.__sessionProvider.dynamic.respawn.switchVehSetupsLayout(vehCD, groupID, layoutIdx)

    def __needVehicleInvalidation(self, vehicleInfo, setupIndexes):
        if vehicleInfo.intCD != self._vehicle.intCD:
            return True
        actualSetupIndexes = vehicleInfo.vehSetupsIndexes.copy()
        actualSetupIndexes.update(setupIndexes)
        if actualSetupIndexes != self._vehicle.setupLayouts.groups:
            playSound(Sounds.GAMEPLAY_SETUP_SWITCH)
            return True
        return False


class FrontlineRespawnAmmunitionPanelInject(RespawnAmmunitionPanelInject, IFrontlineRespawnView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def _updateGuiVehicle(self, vehicleInfo, setupIndexes):
        super(FrontlineRespawnAmmunitionPanelInject, self)._updateGuiVehicle(vehicleInfo, setupIndexes)
        ammoViews = BigWorld.player().ammoViews
        idx = ammoViews['vehTypeCompDescrs'].index(self._vehicle.intCD)
        abilitiesCDs = ammoViews['compDescrs'][idx] if len(ammoViews['compDescrs']) > idx else vehicleInfo.battleAbilities
        battleAbilities = list(((BattleAbility(abilityCD) if abilityCD else None) for abilityCD in abilitiesCDs))
        self._vehicle.battleAbilities.setLayout(*battleAbilities)
        self._vehicle.battleAbilities.setInstalled(*battleAbilities)
