# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush_personality.py
from __future__ import absolute_import
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from constants import HAS_DEV_RESOURCES
from constants_utils import initCommonTypes, initSquadCommonTypes
from debug_utils import LOG_DEBUG
from fort_rush.account_helpers.account_settings import extendAccountSettings
from fort_rush.gui import fort_rush_gui_constants
from fort_rush.gui.battle_results import registerFortRushBattleResultsStatsSorting
from fort_rush.gui.register_aditional_params import registerConditionFormatterIcons
from fort_rush.gui.game_control import registerFortRushAwardControllers, registerFortRushSMTypes, registerControlModeOverrides
from fort_rush_common import fort_rush_constants
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema
from gui.battle_results.reusable import ReusableInfoFactory
from gui.impl.gen import R
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from fort_rush.gui.fort_rush_gui_constants import FUNCTIONAL_FLAG as FORT_RUSH_FUNCTIONAL_FLAG
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes, initBattleCtrlIDs
from gui.shared.system_factory import registerScaleformLobbyPackages, registerIgnoredModeForAutoSelectVehicle
from messenger.m_constants import BATTLE_CHANNEL
from schema_manager import getSchemaManager

class ClientFortRushBattleMode(fort_rush_constants.FortRushBattleMode):
    _CLIENT_BATTLE_PAGE = (fort_rush_gui_constants.VIEW_ALIAS.FORT_RUSH_BATTLE_PAGE,)
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = fort_rush_gui_constants.FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_ENTRY_POINT
    _CLIENT_PRB_ACTION_NAME = fort_rush_gui_constants.PREBATTLE_ACTION_NAME.FORT_RUSH
    _CLIENT_PRB_ACTION_NAME_SQUAD = fort_rush_gui_constants.PREBATTLE_ACTION_NAME.FORT_RUSH_SQUAD
    _CLIENT_GAME_SEASON_TYPE = fort_rush_constants.GameSeasonType.FORT_RUSH

    @property
    def _client_prbEntityClass(self):
        from fort_rush.gui.prb_control.entities.pre_queue.entity import FortRushBattleEntity
        return FortRushBattleEntity

    @property
    def _client_canSelectPrbEntity(self):
        from fort_rush.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from fort_rush.gui.prb_control.entities.pre_queue.entity import FortRushBattleEntryPoint
        return FortRushBattleEntryPoint

    @property
    def _client_hangarEventBannerType(self):
        from fort_rush.gui.impl.lobby.fort_rush_event_banner import FortRushEventBanner
        return FortRushEventBanner

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from fort_rush.gui.impl.lobby.fort_rush_event_banner import isFortRushEntryPointAvailable
        return isFortRushEntryPointAvailable

    @property
    def _client_selectorColumn(self):
        from gui.impl.lobby.mode_selector.items.items_constants import DEFAULT_COLUMN, DEFAULT_PRIORITY
        return (DEFAULT_COLUMN, DEFAULT_PRIORITY)

    @property
    def _client_selectorItemsCreator(self):
        from fort_rush.gui.scaleform.daapi.view.lobby.header.battle_selector_items import addFortRushBattlesType
        return addFortRushBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        from fort_rush.gui.impl.lobby.mode_selector.fort_rush_mode_selector_item import FortRushModeSelectorItem
        return FortRushModeSelectorItem

    @property
    def _client_prbSquadEntityClass(self):
        from fort_rush.gui.prb_control.entities.squad.entity import FortRushSquadEntity
        return FortRushSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from fort_rush.gui.prb_control.entities.squad.entity import FortRushEntryPoint
        return FortRushEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from fort_rush.gui.scaleform.daapi.view.lobby.header.battle_selector_items import addFortRushSquadType
        return addFortRushSquadType

    @property
    def _client_platoonViewClass(self):
        from fort_rush.gui.impl.lobby.platoon.fort_rush_platoon_members_view import FortRushPlatoonMembersView
        return FortRushPlatoonMembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
        return WelcomeView

    @property
    def _client_providerBattleQueue(self):
        from fort_rush.gui.scaleform.daapi.view.lobby.battle_queue_provider import FortRushQueueProvider
        return FortRushQueueProvider

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_arenaDescrClass(self):
        from fort_rush.gui.battle_control.arena_info.arena_descrs import FortRushArenaDescription
        return FortRushArenaDescription

    @property
    def _client_battleResultStatsCtrlClass(self):
        from fort_rush.gui.battle_results.composer import FortRushBattleResultStatsCtrl
        return FortRushBattleResultStatsCtrl

    @property
    def _client_seasonControllerHandler(self):
        from fort_rush.gui.game_control.battle_controller import FortRushBattleController
        return FortRushBattleController

    @property
    def _client_battleRequiredLibraries(self):
        return ['fort_rush|minimapEntriesLibrary.swf']

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['fort_rush|example_ext_lobby.swf']

    @property
    def _client_battleEntry(self):
        return R.entries.fort_rush.battle()

    @property
    def _client_DynamicObjectCacheClass(self):
        from fort_rush_dyn_object_cache import _FortRushDynObjects
        return _FortRushDynObjects

    @property
    def _client_notificationActionHandlers(self):
        from fort_rush.notification.action_handlers import FortRushActionHandler
        from fort_rush.notification.action_handlers import _OpenFRProgressionHandler
        return (FortRushActionHandler, _OpenFRProgressionHandler)

    @property
    def _client_messengerClientFormatters(self):
        from fort_rush.messenger.formatters.service_channel import FortRushEventStatesFormatter
        return {fort_rush_gui_constants.SCH_CLIENT_MSG_TYPE.FORT_RUSH_MSG_TYPE: FortRushEventStatesFormatter()}

    @property
    def _client_messengerServerFormatters(self):
        from fort_rush.messenger.formatters.service_channel import FortRushBattleResultsFormatter
        return {_SM_TYPE.fortRushBattleResults.index(): FortRushBattleResultsFormatter()}

    @property
    def _client_tokenQuestsSubFormatters(self):
        from fort_rush.messenger.formatters.token_quest_subformatters import FortRushProgressionQuestFormatter
        return (FortRushProgressionQuestFormatter(),)

    @property
    def _client_hangarDynamicGuiProvider(self):
        from fort_rush.gui.hangar_presets.fort_rush_dynamic_gui_provider import FortRushHangarDynamicGuiProvider
        return FortRushHangarDynamicGuiProvider

    @property
    def _client_LobbyContextMenuOptions(self):
        from fort_rush.gui.scaleform.daapi.view.lobby.fort_rush_user_cm_handlers import CREATE_FORT_RUSH_SQUAD, fortRushSquadOptionBuilder, createFortRushSquadHandler
        return ((CREATE_FORT_RUSH_SQUAD, fortRushSquadOptionBuilder, createFortRushSquadHandler),)

    @property
    def _client_battleChannelController(self):
        from fort_rush.messenger.gui.Scaleform.channels.bw_chat2.fort_rush_battle_channel_controller import FortRushTeamChannelController
        return (BATTLE_CHANNEL.TEAM, FortRushTeamChannelController)

    @property
    def _client_customizationHangarDisabled(self):
        from fort_rush.gui.shared.event_dispatcher import isCustomizationHangarDisabled
        return isCustomizationHangarDisabled

    @property
    def _client_attackReasonToCode(self):
        return {fort_rush_constants.ATTACK_REASON.getIndex(fort_rush_constants.ATTACK_REASON.EXAMPLE_ATTACK_REASON1): 'EXAMPLE_ATTACK_REASON1'}

    @property
    def _client_gameControllers(self):
        from fort_rush.skeletons.battle_controller import IFortRushBattleController
        from fort_rush.gui.game_control.battle_controller import FortRushBattleController
        controllers = ((IFortRushBattleController, FortRushBattleController, False),)
        return controllers

    @property
    def _client_battleControllersRepository(self):
        from fort_rush.gui.battle_control.controllers.repositories import FortRushControllerRepository
        return FortRushControllerRepository

    @property
    def _client_sharedControllersRepository(self):
        from fort_rush.gui.battle_control.controllers.repositories import FortRushSharedControllersRepository
        return FortRushSharedControllersRepository

    @property
    def _client_battleResultsReusables(self):
        from fort_rush.gui.battle_results.reusable.fort_rush_shared import FortRushVehicleSummarizeInfo, FortRushVehicleDetailedInfo
        return {ReusableInfoFactory.Keys.VEHICLE_SUMMARIZED: FortRushVehicleSummarizeInfo,
         ReusableInfoFactory.Keys.VEHICLE_DETAILED: FortRushVehicleDetailedInfo}


def preInit():
    initCommonTypes(fort_rush_constants, __name__)
    initSquadCommonTypes(fort_rush_constants, __name__)
    initGuiTypes(fort_rush_gui_constants, __name__)
    initScaleformGuiTypes(fort_rush_gui_constants, __name__)
    initBattleCtrlIDs(fort_rush_gui_constants, __name__)
    import score_reasons_common.manager as score_reasons_manager
    score_reasons_manager.init()
    schemaManager = getSchemaManager()
    schemaManager.registerSchema(fortRushBattlesConfigGameParamsSchema)
    battleMode = ClientFortRushBattleMode(__name__)
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleEntry()
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerSquadTypes()
    battleMode.registerHangarEventBanner()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerProviderBattleQueue()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsCtrl()
    registerFortRushBattleResultsStatsSorting()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientSeasonType(fort_rush_constants)
    battleMode.registerGameControllers()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(fort_rush_gui_constants)
    battleMode.registerMessengerServerFormatters()
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerLobbyContextMenuOptions()
    battleMode.registerBattleChannelController()
    battleMode.registerCustomizationHangarDecorator()
    battleMode.registerBattleControllersRepository()
    battleMode.registerDevReplayMode()
    battleMode.registerDynamicObjectCache()
    registerIgnoredModeForAutoSelectVehicle([FORT_RUSH_FUNCTIONAL_FLAG.FORT_RUSH])
    registerFortRushSMTypes()
    registerFortRushAwardControllers()
    registerConditionFormatterIcons()
    registerControlModeOverrides()


def init():
    extendAccountSettings()
    LOG_DEBUG('[FORT_RUSH] --- DEBUG --- init: %s', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['fort_rush.gui.scaleform.daapi.view.lobby'])
    registerScaleformLobbyPackages(('fort_rush.gui.impl.lobby',))
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['fort_rush.gui.scaleform.daapi.view.battle', 'fort_rush.gui.scaleform.daapi.view.battle.shared'], fort_rush_constants.ARENA_GUI_TYPE.FORT_RUSH)
    if HAS_DEV_RESOURCES:
        from fort_rush.gui.development import prb_dev
        prb_dev.prbDevInit()


def start():
    pass


def fini():
    if HAS_DEV_RESOURCES:
        from fort_rush.gui.development import prb_dev
        prb_dev.prbDevFini()
