# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/frag_correlation_bar.py
from collections import namedtuple
import typing
from account_helpers.settings_core.settings_constants import ScorePanelStorageKeys, GAME
from constants import ARENA_GUI_TYPE, IS_DEVELOPMENT
from gui.Scaleform.daapi.view.meta.FragCorrelationBarMeta import FragCorrelationBarMeta
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.impl import backport
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import BitmaskHelper
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class _FragBarViewState(BitmaskHelper):
    DEFAULT = 0
    SHOW_HP_VALUES = 1
    SHOW_HP_DIFFERENCE = 2
    SHOW_TIER_GROUPING = 4
    SHOW_VEHICLES_COUNTER = 8
    SHOW_HP_BAR = 16


GuiTypeViewStateBehaviour = namedtuple('GuiTypeViewStateBehaviour', ('allowHPBar', 'allowHPVal', 'allowDiff', 'allowTierGrp', 'allowVehIcons'))
_DEFAULT_GUI_TYPE = GuiTypeViewStateBehaviour(True, True, True, True, True)
_GUI_TYPE_VIEW_STATE_BEHAVIOUR = {ARENA_GUI_TYPE.TRAINING: GuiTypeViewStateBehaviour(True, True, True, IS_DEVELOPMENT, True),
 ARENA_GUI_TYPE.EPIC_RANDOM: GuiTypeViewStateBehaviour(True, True, True, False, False),
 ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING: GuiTypeViewStateBehaviour(True, True, True, False, False)}

class FragCorrelationBar(FragCorrelationBarMeta, IBattleFieldListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(FragCorrelationBar, self).__init__()
        self.__viewSettings = 0

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        pass

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        pass

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        alliesHPPercentage = alliesHP / float(totalAlliesHP) * 100 if totalAlliesHP > 0 else 0
        enemyHPPercentage = enemiesHP / float(totalEnemiesHP) * 100 if totalEnemiesHP > 0 else 0
        differanceValue = ('+' if alliesHP - enemiesHP > 0 else '') + self.__formatValuesToUserPreferences(alliesHP - enemiesHP)
        self.as_updateTeamHealthValuesS(allyTeamHealth=self.__formatValuesToUserPreferences(alliesHP), diffValue=differanceValue, allyTeamHealthPercentage=alliesHPPercentage, enemyTeamHealth=self.__formatValuesToUserPreferences(enemiesHP), enemyTeamHealthPercentage=enemyHPPercentage)

    def _populate(self):
        super(FragCorrelationBar, self)._populate()
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        if self.settingsCore:
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            self.__initializeSettings()

    def _dispose(self):
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        if self.settingsCore:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(FragCorrelationBar, self)._dispose()

    def __formatValuesToUserPreferences(self, value):
        return backport.getIntegralFormat(value)

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self.__initializeSettings()

    def __initializeSettings(self):
        showBar = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_BAR))
        showVeh = bool(self.settingsCore.getSetting(GAME.SHOW_VEHICLES_COUNTER))
        showHp = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_VALUES))
        showDiff = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_DIFFERENCE))
        showTiers = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.ENABLE_TIER_GROUPING))
        mask = 0
        arenaType = self.__getArenaTypeBehaviour()
        mask = self.__changeSetting(mask, arenaType.allowHPBar and showBar, _FragBarViewState.SHOW_HP_BAR)
        mask = self.__changeSetting(mask, arenaType.allowHPVal and showHp and showBar, _FragBarViewState.SHOW_HP_VALUES)
        mask = self.__changeSetting(mask, arenaType.allowDiff and showDiff and showBar, _FragBarViewState.SHOW_HP_DIFFERENCE)
        mask = self.__changeSetting(mask, arenaType.allowTierGrp and showTiers and showVeh, _FragBarViewState.SHOW_TIER_GROUPING)
        mask = self.__changeSetting(mask, arenaType.allowVehIcons and showVeh, _FragBarViewState.SHOW_VEHICLES_COUNTER)
        self.__viewSettings = mask
        self.as_updateViewSettingS(self.__viewSettings)

    def __onSettingsChanged(self, diff):
        showBar = diff.get(ScorePanelStorageKeys.SHOW_HP_BAR)
        showVeh = diff.get(GAME.SHOW_VEHICLES_COUNTER)
        showHp = diff.get(ScorePanelStorageKeys.SHOW_HP_VALUES)
        showDiff = diff.get(ScorePanelStorageKeys.SHOW_HP_DIFFERENCE)
        showTiers = diff.get(ScorePanelStorageKeys.ENABLE_TIER_GROUPING)
        if showVeh is None and showHp is None and showDiff is None and showTiers is None and showBar is None:
            return
        else:
            mask = self.__viewSettings
            arenaType = self.__getArenaTypeBehaviour()
            if showBar is not None or showDiff is not None or showHp is not None:
                if showBar is None:
                    showBar = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_BAR))
                if showDiff is None:
                    showDiff = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_DIFFERENCE))
                if showHp is None:
                    showHp = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.SHOW_HP_VALUES))
                activateHPBar = arenaType.allowHPBar and showBar
                mask = self.__changeSetting(mask, activateHPBar, _FragBarViewState.SHOW_HP_BAR)
                activateHPVal = activateHPBar and arenaType.allowHPVal and showHp
                mask = self.__changeSetting(mask, activateHPVal, _FragBarViewState.SHOW_HP_VALUES)
                activateHPDiff = activateHPBar and arenaType.allowDiff and showDiff
                mask = self.__changeSetting(mask, activateHPDiff, _FragBarViewState.SHOW_HP_DIFFERENCE)
            if showVeh is not None or showTiers is not None:
                if showVeh is None:
                    showVeh = bool(self.settingsCore.getSetting(GAME.SHOW_VEHICLES_COUNTER))
                if showTiers is None:
                    showTiers = bool(self.settingsCore.getSetting(ScorePanelStorageKeys.ENABLE_TIER_GROUPING))
                activateVehIcons = arenaType.allowVehIcons and showVeh
                mask = self.__changeSetting(mask, activateVehIcons, _FragBarViewState.SHOW_VEHICLES_COUNTER)
                activateTierGroup = activateVehIcons and arenaType.allowTierGrp and showTiers
                mask = self.__changeSetting(mask, activateTierGroup, _FragBarViewState.SHOW_TIER_GROUPING)
            if mask != self.__viewSettings:
                self.__viewSettings = mask
                self.as_updateViewSettingS(self.__viewSettings)
            return

    def __getArenaTypeBehaviour(self):
        arenaGuiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
        arenaType = _GUI_TYPE_VIEW_STATE_BEHAVIOUR.get(arenaGuiType, _DEFAULT_GUI_TYPE)
        return arenaType

    def __changeSetting(self, mask, newValue, flag):
        if newValue:
            mask = BitmaskHelper.addIfNot(mask, flag)
        else:
            mask = BitmaskHelper.removeIfHas(mask, flag)
        return mask
