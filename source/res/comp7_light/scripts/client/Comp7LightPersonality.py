# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/Comp7LightPersonality.py
import comp7_light.gui.comp7_light_constants as gui_constants
from comp7_core.gui import initCoreGuiTypes
from comp7_light.gui.Scaleform import registerComp7LightScaleform
from comp7_light.gui.comp7_light_constants import COMP7_LIGHT_ENTRY_POINT_ALIAS
from comp7_light.gui.impl.battle import registerComp7LightBattle
from comp7_light.gui.impl.lobby import registerComp7LightLobby
from comp7_light.gui.prb_control import registerComp7LightOthersPrbParams
from comp7_light_battle_mode import Comp7LightBattleMode
from comp7_light_common import injectConsts, injectSquadConsts
from comp7_light_constants import ARENA_GUI_TYPE, GameSeasonType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes
_LOBBY_EXT_PACKAGES = ['comp7_light.gui.impl.lobby.hangar']
_BATTLE_EXT_PACKAGES = ['comp7_light.gui.Scaleform.daapi.view.battle.shared']

class ClientComp7LightBattleMode(Comp7LightBattleMode):
    _CLIENT_PRB_ACTION_NAME = gui_constants.PREBATTLE_ACTION_NAME.COMP7_LIGHT
    _CLIENT_PRB_ACTION_NAME_SQUAD = gui_constants.PREBATTLE_ACTION_NAME.COMP7_LIGHT_SQUAD
    _CLIENT_REPLAY_MODE_TAG = 'OnslaughtLight'
    _CLIENT_GAME_SEASON_TYPE = GameSeasonType.COMP7_LIGHT
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.COMP7_LIGHT_BATTLE_PAGE
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = COMP7_LIGHT_ENTRY_POINT_ALIAS

    @property
    def _client_gameControllers(self):
        from skeletons.gui.game_control import IComp7LightController
        from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
        from comp7_light.gui.game_control.comp7_light_controller import Comp7LightController
        from comp7_light.gui.game_control.comp7_light_progression_controller import Comp7LightProgressionController
        return ((IComp7LightController, Comp7LightController, True), (IComp7LightProgressionController, Comp7LightProgressionController, False))

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_2, 10)

    @property
    def _client_selectorItemsCreator(self):
        from comp7_light.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addComp7LightBattleType
        return addComp7LightBattleType

    @property
    def _client_modeSelectorItemsClass(self):
        from comp7_light.gui.impl.lobby.mode_selector.items.comp7_light_mode_selector_item import Comp7LightModeSelectorItem
        return Comp7LightModeSelectorItem

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from comp7_light.gui.impl.lobby.comp7_light_event_banner import Comp7LightEventBanner
        return Comp7LightEventBanner.isEntryPointAvailable

    @property
    def _client_hangarEventBannerType(self):
        from comp7_light.gui.impl.lobby.comp7_light_event_banner import Comp7LightEventBanner
        return Comp7LightEventBanner

    @property
    def _client_prbEntryPointClass(self):
        from comp7_light.gui.prb_control.entities.pre_queue.entity import Comp7LightEntryPoint
        return Comp7LightEntryPoint

    @property
    def _client_prbEntityClass(self):
        from comp7_light.gui.prb_control.entities.pre_queue.entity import Comp7LightEntity
        return Comp7LightEntity

    @property
    def _client_canSelectPrbEntity(self):

        def canSelectComp7LightPrbEntity():
            return True

        return canSelectComp7LightPrbEntity

    @property
    def _client_hangarPresetsGetter(self):
        from comp7_light.gui.hangar_presets.hangar_presets_getters import Comp7LightPresetsGetter
        return Comp7LightPresetsGetter

    @property
    def _client_providerBattleQueue(self):
        from comp7_light.gui.Scaleform.daapi.view.lobby.battle_queue import Comp7LightQueueProvider
        return Comp7LightQueueProvider

    @property
    def _client_viewsForMonitoring(self):
        from comp7_light.gui.Scaleform.genConsts.COMP7_LIGHT_HANGAR_ALIASES import COMP7_LIGHT_HANGAR_ALIASES
        return [COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_LOBBY_HANGAR]

    @property
    def _client_prbSquadEntryPointClass(self):
        from comp7_light.gui.prb_control.entities.squad.entity import Comp7LightSquadEntryPoint
        return Comp7LightSquadEntryPoint

    @property
    def _client_prbSquadEntityClass(self):
        from comp7_light.gui.prb_control.entities.squad.entity import Comp7LightSquadEntity
        return Comp7LightSquadEntity

    @property
    def _client_selectorSquadItemsCreator(self):
        from comp7_light.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addComp7LightSquadType
        return addComp7LightSquadType

    @property
    def _client_squadFinderClass(self):
        from comp7_light.gui.battle_control.arena_info.squad_finder import Comp7LightTeamScopeNumberingFinder
        return Comp7LightTeamScopeNumberingFinder

    @property
    def _client_platoonWelcomeViewClass(self):
        from comp7_light.gui.impl.lobby.platoon.view.comp7_light_platoon_welcome_view import Comp7LightWelcomeView
        return Comp7LightWelcomeView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.comp7_light.lobby.MembersWindow(), MembersWindow))]

    @property
    def _client_platoonViewClass(self):
        from comp7_light.gui.impl.lobby.platoon.view.platoon_members_view import Comp7LightMembersView
        return Comp7LightMembersView

    @property
    def _client_LobbyContextMenuOptions(self):
        from comp7_light.gui.Scaleform.daapi.view.lobby.lobby_constants import USER
        from comp7_light.gui.Scaleform.daapi.view.lobby.user_cm_handlers import createComp7LightSquad, addComp7LightSquadInfo
        return ((USER.CREATE_COMP7_LIGHT_SQUAD, addComp7LightSquadInfo, createComp7LightSquad),)

    @property
    def _client_arenaDescrClass(self):
        from comp7_light.gui.battle_control.arena_info.arena_descrs import Comp7LightBattlesDescription
        return Comp7LightBattlesDescription

    @property
    def _client_notificationActionHandlers(self):
        from comp7_light.notification.action_handlers import ShowComp7LightProgressionActionHandler
        return (ShowComp7LightProgressionActionHandler,)

    @property
    def _client_messengerServerFormatters(self):
        from chat_shared import SYS_MESSAGE_TYPE
        from comp7_light.messenger.formatters.service_channel import Comp7LightBattleResultsFormatter
        return {SYS_MESSAGE_TYPE.comp7LightBattleResults.index(): Comp7LightBattleResultsFormatter()}

    @property
    def _client_messengerClientFormatters(self):
        from comp7_light.messenger.formatters.service_channel import Comp7LightProgressionSystemMessageFormatter
        return {gui_constants.SCH_CLIENT_MSG_TYPE.COMP7_LIGHT_PROGRESSION_NOTIFICATIONS: Comp7LightProgressionSystemMessageFormatter()}

    @property
    def _client_DynamicObjectCacheClass(self):
        from comp7_core.comp7_dyn_objects_cache import Comp7DynObjects
        return Comp7DynObjects

    @property
    def _client_battleResultStatsCtrlClass(self):
        from comp7_light.gui.battle_results.composer import Comp7LightStatsComposer
        return Comp7LightStatsComposer

    @property
    def _client_battleResultsReusables(self):
        from gui.battle_results.reusable.extension_utils import ReusableInfoFactory
        from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleDetailedInfo, Comp7CoreVehicleSummarizeInfo
        return {ReusableInfoFactory.Keys.VEHICLE_DETAILED: Comp7CoreVehicleDetailedInfo,
         ReusableInfoFactory.Keys.VEHICLE_SUMMARIZED: Comp7CoreVehicleSummarizeInfo}

    @property
    def _client_battleControllersRepository(self):
        from comp7_light.gui.battle_control.controllers.repositories import Comp7LightControllerRepository
        return Comp7LightControllerRepository

    @property
    def _client_battleRequiredLibraries(self):
        return ['comp7_light|comp7_light_battle.swf', 'comp7_core|minimapEntriesLibrary.swf']


def preInit():
    injectConsts(__name__)
    injectSquadConsts(__name__)
    initCoreGuiTypes(__name__)
    initGuiTypes(gui_constants, __name__)
    battleMode = ClientComp7LightBattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerGameControllers()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerHangarEventBanner()
    battleMode.registerProviderBattleQueue()
    battleMode.registerClientViewsForMonitoring()
    battleMode.registerSquadTypes()
    battleMode.registerClientSquadSelector()
    battleMode.registerClientPlatoon()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsCtrl()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerLobbyContextMenuOptions()
    battleMode.registerDynamicObjectCache()
    battleMode.registerBattleControllersRepository()
    battleMode.registerScaleformRequiredLibraries()
    registerComp7LightScaleform()
    registerComp7LightLobby()
    registerComp7LightOthersPrbParams()
    registerComp7LightBattle()


def init():
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, _LOBBY_EXT_PACKAGES)
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, _BATTLE_EXT_PACKAGES, ARENA_GUI_TYPE.COMP7_LIGHT)


def start():
    pass


def fini():
    pass
