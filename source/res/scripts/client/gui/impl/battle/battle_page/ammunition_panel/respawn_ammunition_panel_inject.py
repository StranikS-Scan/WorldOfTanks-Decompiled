# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/respawn_ammunition_panel_inject.py
from gui.battle_control.controllers.respawn_ctrl import IRespawnView
from gui.battle_control.controllers.epic_respawn_ctrl import IEpicRespawnView
from gui.veh_post_progression.helpers import getVehicleState, getInstalledShells, updateInvInstalled
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor, hasAliveInject
from gui.shared.gui_items.artefacts import BattleAbility
from gui.shared.gui_items.Vehicle import Vehicle
from gui.impl.battle.battle_page.ammunition_panel.respawn_ammunition_panel_view import RespawnAmmunitionPanelView
from gui.veh_post_progression.sounds import playSound, Sounds
from helpers import dependency
from post_progression_common import EXT_DATA_SLOT_KEY, EXT_DATA_PROGRESSION_KEY
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
        self._injectView.updateViewVehicle(self._vehicle)

    def _onPopulate(self):
        pass

    def _addInjectContentListeners(self):
        self._injectView.onSwitchLayout += self.__onSwitchLayout

    def _removeInjectContentListeners(self):
        self._injectView.onSwitchLayout -= self.__onSwitchLayout

    def _makeInjectView(self, vehicle):
        return RespawnAmmunitionPanelView(vehicle)

    def _updateGuiVehicle(self, vehicleInfo, setupIndexes):
        emptyVehicle = Vehicle(strCompactDescr=vehicleInfo.strCD)
        shellsCDs = [ shell.intCD for shell in emptyVehicle.gun.defaultAmmo ]
        shellsLayoutKey = (emptyVehicle.turret.intCD, emptyVehicle.gun.intCD)
        actualSetupIndexes = vehicleInfo.vehSetupsIndexes.copy()
        actualSetupIndexes.update(setupIndexes)
        invData = {'battleCrewCDs': vehicleInfo.crewDescrs,
         'shells': getInstalledShells(shellsCDs, vehicleInfo.vehSetups['shellsSetups']),
         'shellsLayout': {shellsLayoutKey: vehicleInfo.vehSetups['shellsSetups']},
         'eqsLayout': vehicleInfo.vehSetups['eqsSetups'],
         'boostersLayout': vehicleInfo.vehSetups['boostersSetups'],
         'devicesLayout': vehicleInfo.vehSetups['devicesSetups'],
         'layoutIndexes': actualSetupIndexes}
        updateInvInstalled(invData, actualSetupIndexes)
        extData = {EXT_DATA_SLOT_KEY: vehicleInfo.customRoleSlotTypeId,
         EXT_DATA_PROGRESSION_KEY: getVehicleState(vehicleInfo.vehPostProgression)}
        vehicle = self._vehicle = Vehicle(strCompactDescr=vehicleInfo.strCD, extData=extData.copy(), invData=invData)
        vehicle.installPostProgressionItem(self.__itemsFactory.createVehPostProgression(vehicle.compactDescr, extData[EXT_DATA_PROGRESSION_KEY], vehicle.typeDescr))

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


class EpicRespawnAmmunitionPanelInject(RespawnAmmunitionPanelInject, IEpicRespawnView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def _updateGuiVehicle(self, vehicleInfo, setupIndexes):
        super(EpicRespawnAmmunitionPanelInject, self)._updateGuiVehicle(vehicleInfo, setupIndexes)
        battleAbilities = self.__getBattleAbilities(vehicleInfo.battleAbilities)
        self._vehicle.battleAbilities.setLayout(*battleAbilities)
        self._vehicle.battleAbilities.setInstalled(*battleAbilities)

    def __getBattleAbilities(self, abilitiesCDs):
        amountOfSlots = self.__epicController.getNumAbilitySlots(self._vehicle.typeDescr)
        return [ BattleAbility(abilityCD) for abilityCD in abilitiesCDs ] + [None] * (amountOfSlots - len(abilitiesCDs))
