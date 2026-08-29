# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTMissile.py
import typing
from helpers import dependency
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES
from white_tiger.gui.shared.events import WTCrosshairVisibilityEvents
if typing.TYPE_CHECKING:
    from white_tiger.gui.battle_control.controllers.wt_ability_ctrl import WTAbilityController

class WTMissile(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        if self.isAbilityActive:
            self.__updateCrosshair()

    def set_isAbilityActive(self, prev):
        self.__updateCrosshair()

    def __updateCrosshair(self):
        abilityCtrl = self.__sessionProvider.dynamic.wtAbilityCtrl
        if self.isAbilityActive:
            self.__updateCrosshairVisibility(False)
            abilityCtrl.show(WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET, True)
        else:
            self.__updateCrosshairVisibility(True)
            abilityCtrl.hide(WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET, True)

    def __updateCrosshairVisibility(self, show):
        event = WTCrosshairVisibilityEvents(WTCrosshairVisibilityEvents.SHOW_CROSSHAIR, {'visible': show})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)
