# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/wt_ability_ctrl.py
from helpers import dependency
from wt_settings import g_wt_config
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES

class WTAbilityController(ViewComponentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __SUPPORTED_ABILITIES = {'wt_missile': WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET}

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def getControllerID(self):
        return BATTLE_CTRL_ID.WT_ABILITY_CTRL

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)
        supportedAbility = []
        arenaDP = self.__sessionProvider.getArenaDP()
        playerVehicleID = arenaDP.getPlayerVehicleID()
        vehCD = arenaDP.getVehicleInfo(playerVehicleID).vehicleType.compactDescr
        for abilityName, alias in self.__SUPPORTED_ABILITIES.items():
            if g_wt_config.hasAbility(vehCD, abilityName):
                supportedAbility.append(alias)

        for viewComponent in self._viewComponents:
            for alias in supportedAbility:
                viewComponent.extendComponents(alias)

    def show(self, abilityAlias, useAnim=False):
        for viewComponent in self._viewComponents:
            viewComponent.show(abilityAlias, useAnim)

    def hide(self, abilityAlias, useAnim=False):
        for viewComponent in self._viewComponents:
            viewComponent.hide(abilityAlias, useAnim)

    def update(self, abilityAlias, **kwargs):
        for viewComponent in self._viewComponents:
            viewComponent.update(abilityAlias, **kwargs)
