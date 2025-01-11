# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/page.py
from aih_constants import CTRL_MODE_NAME
from grinch.gui.Scaleform.daapi.view.battle.battle_hints import GrinchBattleHintsQueue, GrinchBattleHint
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.page import SharedPage
from grinch.gui.battle_control.controllers.equipment_key_binder import GrinchEquipmentKeyBinder
from grinch.gui.Scaleform.daapi.view.battle.manager import GrinchMarkersManager
from grinch.gui.Scaleform.daapi.view.battle import battle_hints
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
from shared_utils import CONST_CONTAINER

class DynamicAliases(CONST_CONTAINER):
    GRINCH_BATTLE_HINT = 'grinchBattleHint'
    GRINCH_EQUIPMENT_BINDER = 'grinchEquipmentBinder'
    GRINCH_HIT_DIRECTION = 'grinchHitDirection'


_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.GRINCH_HUD,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.HINT_PANEL)),
 (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (BATTLE_VIEW_ALIASES.GRINCH_HUD,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.BATTLE_HINTS, (DynamicAliases.GRINCH_BATTLE_HINT,)),
 (BATTLE_CTRL_ID.AMMO, (DynamicAliases.GRINCH_EQUIPMENT_BINDER,))), viewsConfig=((DynamicAliases.GRINCH_BATTLE_HINT, lambda : battle_hints.GrinchBattleHintComponent(DynamicAliases.GRINCH_BATTLE_HINT, BattleHintQueueParams('text', queueClass=GrinchBattleHintsQueue, hintClass=GrinchBattleHint, withFadeOut=False))), (DynamicAliases.GRINCH_EQUIPMENT_BINDER, lambda : GrinchEquipmentKeyBinder(DynamicAliases.GRINCH_EQUIPMENT_BINDER))))
_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, GrinchMarkersManager, KillCamMarkersManager)

class GrinchBattlePage(SharedPage):

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS):
        components = _CONFIG if not components else components + _CONFIG
        super(GrinchBattlePage, self).__init__(components=components, external=external)

    def _processCallout(self, needShow):
        pass

    def _onBattleLoadingStart(self):
        self._isBattleLoading = True
        if not self._blToggling:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        hintPanel = self.getComponent(BATTLE_VIEW_ALIASES.HINT_PANEL)
        if hintPanel and hintPanel.getActiveHint():
            self._blToggling.add(BATTLE_VIEW_ALIASES.HINT_PANEL)
        visible, additionalToggling = set(), set()
        additionalToggling.add(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        visible.add(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        self._blToggling.difference_update(additionalToggling)
        self._setComponentsVisibility(visible=visible, hidden=self._blToggling)
        self._blToggling.update(additionalToggling)

    def _onBattleLoadingFinish(self):
        self._isBattleLoading = False
        self._setComponentsVisibility(visible=self._blToggling, hidden={BATTLE_VIEW_ALIASES.BATTLE_LOADING})
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        if self.sessionProvider.shared.hitDirection is not None:
            self.sessionProvider.shared.hitDirection.setVisible(True)
        return

    def _changeCtrlMode(self, ctrlMode):
        components = self._getComponentsVideoModeSwitching(ctrlMode)
        if ctrlMode == CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden=components)
        else:
            self._setComponentsVisibility(visible=components)
        postmortemPanel = self.getComponent(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        postmortemPanel.changeCtrlMode(ctrlMode)

    def _getComponentsVideoModeSwitching(self, ctrlMode):
        components = set()
        if ctrlMode in (CTRL_MODE_NAME.KILL_CAM, CTRL_MODE_NAME.POSTMORTEM):
            components.add(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        if ctrlMode not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES:
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if vehicle and vehicle.typeDescriptor.hasRocketAcceleration:
                components.add(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR)
        return components

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        pass

    def _handleRadialMenuCmd(self, event):
        pass

    def _handleToggleFullStats(self, event):
        pass

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _handleToggleFullStatsPersonalReserves(self, event):
        pass

    def _handleGUIToggled(self, event):
        self._toggleGuiVisible()

    def _handleHelpEvent(self, event):
        pass

    def _hasBattleMessenger(self):
        return False

    def _canShowPostmortemTips(self):
        return False

    def _onKillCamSimulationStart(self):
        pass

    def _onKillCamSimulationFinish(self):
        pass
