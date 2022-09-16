# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattlePage.py
import base64
import cPickle as pickle
from typing import TYPE_CHECKING
import BigWorld
import SoundGroups
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampConstants import UI_STATE, CONSUMABLE_ERROR_MESSAGES, HINT_TYPE, HINT_NAMES
from bootcamp.BootcampGUI import BootcampMarkersComponent
from bootcamp.BootcampSettings import getBattleSettings
from constants import ARENA_PERIOD
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.bootcamp.battle.bc_finish_sound_player import BCFinishSoundPlayer
from gui.Scaleform.daapi.view.meta.BCBattlePageMeta import BCBattlePageMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import avatar_getter, minimap_utils
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
if TYPE_CHECKING:
    from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
_BOOTCAMP_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, BootcampMarkersComponent)
_BOOTCAMP_MINIMAP_SIZE_SETTINGS_KEY = 'bootcampMinimapSize'

class _BCComponentsConfig(ComponentsConfig):
    BC_FINISH_SOUND_PLAYER = 'bcFinishSoundPlayer'

    def __init__(self):
        super(_BCComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           self.BC_FINISH_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, self.BC_FINISH_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (self.BC_FINISH_SOUND_PLAYER, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, BATTLE_VIEW_ALIASES.PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((self.BC_FINISH_SOUND_PLAYER, BCFinishSoundPlayer), (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


_BC_COMPONENTS_CONFIG = _BCComponentsConfig()

class BootcampAccountSettings(AccountSettings):
    __SCREEN_WIDTH = 1920
    __SCREEN_HEIGHT = 1080

    @staticmethod
    def _getValue(name, setting, force=False):
        if name == _BOOTCAMP_MINIMAP_SIZE_SETTINGS_KEY and setting == KEY_SETTINGS:
            fds = AccountSettings._readSection(AccountSettings._readUserSection(), setting)
            if not fds.has_key(name):
                value = 2 if BigWorld.screenWidth() < BootcampAccountSettings.__SCREEN_WIDTH and BigWorld.screenHeight() < BootcampAccountSettings.__SCREEN_HEIGHT else 3
                fds.write(name, base64.b64encode(pickle.dumps(value)))
                return value
        return AccountSettings._getValue(name, setting, force)

    @staticmethod
    def _setValue(name, value, setting, force=False):
        if name == _BOOTCAMP_MINIMAP_SIZE_SETTINGS_KEY and setting == KEY_SETTINGS:
            fds = AccountSettings._readSection(AccountSettings._readUserSection(), setting)
            fds.write(name, base64.b64encode(pickle.dumps(value)))
            AccountSettings.onSettingsChanging(name, value)
        else:
            AccountSettings._setValue(name, value, setting, force)


class BootcampTargetPlugin(common.EntriesPlugin):

    def addTarget(self, markerID, position):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(markerID, settings.ENTRY_SYMBOL_NAME.BOOTCAMP_TARGET, settings.CONTAINER_NAME.ICONS, matrix=matrix, active=True)
        return model is not None

    def delTarget(self, markerID):
        return self._delEntryEx(markerID)


class BootcampMinimapSettingsPlugin(GlobalSettingsPlugin):
    _AccountSettingsClass = BootcampAccountSettings

    def __init__(self, *args, **kwargs):
        super(BootcampMinimapSettingsPlugin, self).__init__(*args, **kwargs)
        self._changeSizeSettings(_BOOTCAMP_MINIMAP_SIZE_SETTINGS_KEY)


class BootcampMinimapDisablePlugin(GlobalSettingsPlugin):

    def start(self):
        pass

    def stop(self):
        pass


class BootcampMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BootcampMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['bootcamp'] = BootcampTargetPlugin
        setup['settings'] = BootcampMinimapSettingsPlugin
        try:
            lessonId = arenaVisitor.getArenaExtraData()['lessonId']
            if BATTLE_VIEW_ALIASES.MINIMAP in getBattleSettings(lessonId).hiddenPanels:
                setup['settings'] = BootcampMinimapDisablePlugin
        except KeyError:
            LOG_ERROR_BOOTCAMP("Extra data doesn't contain lessonId")

        return setup


class BCBattlePage(BCBattlePageMeta):

    def __init__(self, ctx=None):
        super(BCBattlePage, self).__init__(_BC_COMPONENTS_CONFIG, external=_BOOTCAMP_EXTERNAL_COMPONENTS)
        self._fullStatsAlias = BATTLE_VIEW_ALIASES.FULL_STATS
        self._onAnimationsCompleteCallback = None
        self.__hideOnCountdownPanels = set()
        return

    def reload(self):
        g_bootcamp.getUI().reload()
        super(BCBattlePage, self).reload()

    @property
    def topHint(self):
        return self.getComponent(BATTLE_VIEW_ALIASES.BOOTCAMP_BATTLE_TOP_HINT)

    def getExternalByAlias(self, alias):
        for external in self._external:
            if external.alias == alias:
                return external

    def onAnimationsComplete(self):
        LOG_DEBUG_DEV_BOOTCAMP('onAnimationsComplete')
        if self._onAnimationsCompleteCallback is not None:
            self._onAnimationsCompleteCallback()
            self._onAnimationsCompleteCallback = None
        return

    def _populate(self):
        g_bootcampEvents.onUIStateChanged(UI_STATE.INIT)
        super(BCBattlePageMeta, self)._populate()
        g_bootcampEvents.onBattleComponentVisibility += self.__onComponentVisibilityEvent
        g_bootcampEvents.hideGUIForWinMessage += self.__hideGUIForWinMessage
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _dispose(self):
        self._onAnimationsCompleteCallback = None
        self.__hideOnCountdownPanels.clear()
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_bootcampEvents.hideGUIForWinMessage -= self.__hideGUIForWinMessage
        g_bootcampEvents.onBattleComponentVisibility -= self.__onComponentVisibilityEvent
        super(BCBattlePageMeta, self)._dispose()
        return

    def _onBattleLoadingStart(self):
        if not self._blToggling:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        self._setComponentsVisibility(visible=set(), hidden=self._blToggling)
        introVideoData = g_bootcamp.getIntroVideoData()
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO), ctx=introVideoData), EVENT_BUS_SCOPE.BATTLE)
        SoundGroups.g_instance.restoreWWISEVolume()

    def _onBattleLoadingFinish(self):
        super(BCBattlePageMeta, self)._onBattleLoadingFinish()
        battleSettings = getBattleSettings(g_bootcamp.getLessonNum())
        visiblePanels, hiddenPanels = battleSettings.visiblePanels, battleSettings.hiddenPanels
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        inCountdown = periodCtrl.getPeriod() in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE)
        if inCountdown and BATTLE_VIEW_ALIASES.PLAYERS_PANEL in visiblePanels:
            self.__hideOnCountdownPanels.add(BATTLE_VIEW_ALIASES.PLAYERS_PANEL)
        self._setComponentsVisibility(visible=set(visiblePanels).difference(self.__hideOnCountdownPanels), hidden=set(hiddenPanels).union(self.__hideOnCountdownPanels))
        self.__setComponentEnabled(BATTLE_VIEW_ALIASES.SIXTH_SENSE, BATTLE_VIEW_ALIASES.SIXTH_SENSE in visiblePanels)
        uselessConsumable = HINT_NAMES[HINT_TYPE.HINT_USELESS_CONSUMABLE]
        if uselessConsumable in battleSettings.hints:
            errorMessages = self.getComponent(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES)
            if errorMessages is not None:
                errorMessages.ignoreKeys = CONSUMABLE_ERROR_MESSAGES
        return

    def _toggleRadialMenu(self, enable):
        pass

    def __onComponentVisibilityEvent(self, name, isVisible):
        if isVisible:
            self._setComponentsVisibility(visible={name}, hidden=set())
        else:
            self._setComponentsVisibility(visible=set(), hidden={name})
        self.__setComponentEnabled(name, isVisible)

    def __setComponentEnabled(self, name, enable):
        if name == BATTLE_VIEW_ALIASES.SIXTH_SENSE:
            component = self.getComponent(BATTLE_VIEW_ALIASES.SIXTH_SENSE)
            if component is not None:
                component.enabled = enable
        return

    def __onArenaPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.BATTLE and self.__hideOnCountdownPanels:
            self._setComponentsVisibility(visible=self.__hideOnCountdownPanels, hidden=set())

    def __hideGUIForWinMessage(self):
        hideSet = set(self.as_getComponentsVisibilityS())
        hideSet.difference_update([BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL])
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL}, hidden=hideSet)
        self.fireEvent(events.GameEvent(events.GameEvent.GUI_VISIBILITY, {'visible': False}), scope=EVENT_BUS_SCOPE.BATTLE)
        avatar_getter.setComponentsVisibility(False)
