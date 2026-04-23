# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles_personality.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.missions.mission_utils import extendMissionInfoMap
from gui.shared.system_factory import registerIngameHelpPagesBuilder, registerLobbyTooltipsBuilders
from helpers import dependency
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS, KEY_NOTIFICATIONS
from constants_utils import initCommonTypes, initSquadCommonTypes, addBattleEventTypesFromExtension, addQueueTypeByUnitMgrRoster, addRosterTypeToClass, addUnitMgrFlagToQueueType, addInvitationTypeFromArenaBonusTypeMapping, addPrbTypeByUnitMgrRosterExt
from historical_battles.gui.impl.lobby.mode_selector.items.historical_battles_mode_selector_item import HistoricalBattlesModeSelectorItem
from historical_battles.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addHistoricalBattlesType, addHistoricalBattlesSquadType
from AvatarInputHandler import control_modes, _CTRL_TYPE, OVERWRITE_CTRLS_DESC_MAP
from aih_constants import CTRL_MODE_NAME as _CTRL_MODE
from chat_shared import SYS_MESSAGE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS as ORIGIN_VIEW_ALIAS, VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from historical_battles.gui.Scaleform.daapi.view.lobby.missions.hb_missions_helper import HBMissionInfo, HBDetailedMissionInfo
from historical_battles.gui.ingame_help.hb_help_pages import HBPagesBuilder
from historical_battles.gui.prb_control.entities.pre_queue.entity import HistoricalBattlesEntity, HistoricalBattlesEntryPoint
from historical_battles_common import hb_constants_extension
from historical_battles.gui.battle_control.hb_battle_constants import FEEDBACK_EVENT_ID
from historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview.hb_vehicle_preview import isPreviewAvailable
from historical_battles.gui.battle_control.arena_info.hb_squad_finder import HBTeamScopeNumberingFinder
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.prb_control import prb_config
from historical_battles.gui import gui_constants
from historical_battles.gui.Scaleform.daapi.settings.config_utils import addExtPreviewAliasItem
from historical_battles.messenger.formatters.service_channel import HBShopBundlePurchasedSysMessageFormatter, HBCouponsBundlePurchasedSysMessageFormatter, HBTankModuleBundlePurchasedSysMessageFormatter, HBBattleResultsFormatter, MainPrizeVehicleBundlePurchased, HBDivisionUpgradePurchasedSysMessageFormatter, HBOrderInvoiceSysMessageFormatter
from historical_battles.gui.hangar_presets import registerHistoricalBattlesHangarPresets
from historical_battles_common.hb_constants import ACCOUNT_DEFAULT_SETTINGS, DEFAULT_NOTIFICATIONS, HB_BATTLE_QUESTS_PREFIX
from system_events import g_systemEvents
from historical_battles.gui.shared import personality as gui_personality
from gui.battle_control.controllers import consumables
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.battle_control.controllers.equipments import registerHBEquipmentCtrls
from constants import HAS_DEV_RESOURCES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

@dependency.replace_none_kwargs(ctrl=IGameEventController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isEnabled()


@dependency.replace_none_kwargs(ctrl=IGameEventController)
def isEnabled(ctrl=None):
    return ctrl.isEnabled()


class ClientHistoricalBattlesBattleMode(hb_constants_extension.HistoricalBattlesBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.HISTORICAL_BATTLES
    _CLIENT_PRB_ACTION_NAME = prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES
    _CLIENT_PRB_ACTION_NAME_SQUAD = prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES_SQUAD
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = HANGAR_ALIASES.SE22_EVENT_ENTRY_POINT

    @property
    def _client_prbEntityClass(self):
        return HistoricalBattlesEntity

    @property
    def _client_canSelectPrbEntity(self):
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        return HistoricalBattlesEntryPoint

    @property
    def _client_bannerEntryPointLUIRule(self):
        from gui.limited_ui.lui_rules_storage import LuiRules
        return LuiRules.HB_ENTRY_POINT

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        return isEnabled

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 1)

    @property
    def _client_selectorItemsCreator(self):
        return addHistoricalBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        return HistoricalBattlesModeSelectorItem

    @property
    def _client_battleRequiredLibraries(self):
        return ['historical_battles|historical_battles_battle.swf']

    @property
    def _client_prbSquadEntityClass(self):
        from historical_battles.gui.prb_control.entities.squad.entity import HistoricalBattleSquadEntity
        return HistoricalBattleSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from historical_battles.gui.prb_control.entities.squad.entity import HistoricalBattleSquadEntryPoint
        return HistoricalBattleSquadEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        return addHistoricalBattlesSquadType

    @property
    def _client_squadFinderClass(self):
        return HBTeamScopeNumberingFinder

    @property
    def _client_platoonViewClass(self):
        from historical_battles.gui.impl.lobby.platoon.platoon_members_view import HistoricalBattlesMembersView
        return HistoricalBattlesMembersView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.historical_battles.lobby.MembersWindow(), MembersWindow))]

    def registerScaleformRequiredLibraries(self):
        if self._client_lobbyRequiredLibraries:
            from gui.Scaleform.required_libraries_config import addLobbyRequiredLibraries
            addLobbyRequiredLibraries(self._client_lobbyRequiredLibraries, self._personality)
        if self._client_battleRequiredLibraries:
            from gui.Scaleform.required_libraries_config import addBattleRequiredLibraries
            for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
                addBattleRequiredLibraries(self._client_battleRequiredLibraries, arenaGuiType, self._personality)

    def registerClientSelector(self):
        from gui.prb_control import prb_utils
        prb_utils.addBattleItemToColumnSelector(self._CLIENT_PRB_ACTION_NAME, self._client_selectorColumn, self._personality)
        prb_utils.addBattleSelectorItem(self._CLIENT_PRB_ACTION_NAME, self._client_selectorItemsCreator, self._personality)
        prb_utils.addModeSelectorItem(self._CLIENT_PRB_ACTION_NAME, self._client_modeSelectorItemsClass, self._personality)
        prb_utils.addSupportedEntryByAction(self._CLIENT_PRB_ACTION_NAME, self._client_prbEntryPointClass, self._personality)
        for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
            prb_utils.addSupportedQueues(queueType, self._client_prbEntityClass, self._client_canSelectPrbEntity, self._personality)

    def registerClient(self):
        from gui.prb_control import prb_utils
        from gui.Scaleform.daapi.settings.views import addViewBattlePageAliasByArenaGUIType
        queueType = hb_constants_extension.QUEUE_TYPE.HB_OFFENCE
        arenaGuiType = hb_constants_extension.ARENA_GUI_TYPE.HB_OFFENCE
        prb_utils.addArenaGUITypeByQueueType(queueType, arenaGuiType, self._personality)
        prb_utils.addQueueTypeToPrbType(queueType, self._PREBATTLE_TYPE, self._personality)
        prb_utils.addPrbTypeToQueueType(queueType, self._PREBATTLE_TYPE, self._personality)
        addViewBattlePageAliasByArenaGUIType(arenaGuiType, self._CLIENT_BATTLE_PAGE, self._personality)
        queueType = hb_constants_extension.QUEUE_TYPE.HB_DEFENCE
        arenaGuiType = hb_constants_extension.ARENA_GUI_TYPE.HB_DEFENCE
        prb_utils.addArenaGUITypeByQueueType(queueType, arenaGuiType, self._personality)
        prb_utils.addQueueTypeToPrbType(queueType, self._PREBATTLE_TYPE, self._personality)
        prb_utils.addPrbTypeToQueueType(queueType, self._PREBATTLE_TYPE, self._personality)
        addViewBattlePageAliasByArenaGUIType(arenaGuiType, self._CLIENT_BATTLE_PAGE, self._personality)

    def registerClientPlatoon(self):
        from gui.impl.lobby.platoon import platoon_config
        for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
            platoon_config.addQueueTypeToPrbSquadActionName(queueType, self._CLIENT_PRB_ACTION_NAME_SQUAD, self._personality)

        platoon_config.addPlatoonViewByPrbType(self._PREBATTLE_TYPE, self._client_platoonViewClass, self._personality)
        platoon_config.addPlatoonLayoutData(self._PREBATTLE_TYPE, self._client_platoonLayouts, self._personality)

    def registerClientSquadSelector(self):
        from gui.prb_control import prb_utils
        from constants import PREBATTLE_TYPE
        prb_utils.addSupportedUnitEntryByAction(self._CLIENT_PRB_ACTION_NAME_SQUAD, self._client_prbSquadEntryPointClass, self._personality)
        prb_utils.addSupportedUnitEntryByType(self._PREBATTLE_TYPE, self._client_prbSquadEntryPointClass, self._personality)
        prb_utils.addSupportedUnitByType(self._PREBATTLE_TYPE, self._client_prbSquadEntityClass, self._personality)
        prb_utils.addBattleSelectorSquadItem(self._CLIENT_PRB_ACTION_NAME_SQUAD, self._client_selectorSquadItemsCreator, self._personality)
        for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
            prb_utils.addSquadFinder(arenaGuiType, self._client_squadFinderClass, self._personality)

        prb_utils.addPrbClientCombinedIds(self._PREBATTLE_TYPE, PREBATTLE_TYPE.UNIT, self._personality)

    def registerBattleControllersRepository(self):
        from gui.shared.system_factory import registerBattleControllerRepo
        from historical_battles.gui.battle_control.controllers.repositories import HBControllersRepository
        for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
            registerBattleControllerRepo(arenaGuiType, HBControllersRepository)

    def registerClientBattleResultsComposer(self):
        from gui.shared.system_factory import registerBattleResultsComposer
        from historical_battles.gui.battle_results.composer import HistoryBattleStatsComposer
        for bonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
            registerBattleResultsComposer(bonusType, HistoryBattleStatsComposer)

    def registerBattleResultsConfig(self):
        super(ClientHistoricalBattlesBattleMode, self).registerBattleResultsConfig()
        from gui.battle_results.reusable import ReusableInfoFactory
        from historical_battles.gui.battle_results.reusable import HBAvatarInfo
        ReusableInfoFactory.setAvatarInfoForBonusType(self._ARENA_BONUS_TYPE, HBAvatarInfo)

    @property
    def _client_gameControllers(self):
        from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
        from historical_battles.gui.game_control.progression_controller import HBProgressionController
        from historical_battles.skeletons.gui.hb_notifications_controller import IHBEventNotifications
        from historical_battles.gui.hb_event_notifications import HBEventNotifications
        from historical_battles.gui.server_events.game_event.hb_game_event_controller import HBGameEventController
        from historical_battles.skeletons.gui.quests_controller import IHBQuestsController
        from historical_battles.gui.hb_quests_controller import HBQuestsController
        return [(IGameEventController, HBGameEventController, False),
         (IHBProgressionOnTokensController, HBProgressionController, False),
         (IHBEventNotifications, HBEventNotifications, False),
         (IHBQuestsController, HBQuestsController, False)]

    @property
    def _client_messengerServerFormatters(self):
        return {SYS_MESSAGE_TYPE.hbBattleResults.index(): HBBattleResultsFormatter(),
         SYS_MESSAGE_TYPE.hbShopBundlePurchased.index(): HBShopBundlePurchasedSysMessageFormatter(),
         SYS_MESSAGE_TYPE.hbCouponsBundlePurchased.index(): HBCouponsBundlePurchasedSysMessageFormatter(),
         SYS_MESSAGE_TYPE.hbTankModuleBundlePurchased.index(): HBTankModuleBundlePurchasedSysMessageFormatter(),
         SYS_MESSAGE_TYPE.hbMainPrizeVehiclePurchased.index(): MainPrizeVehicleBundlePurchased(),
         SYS_MESSAGE_TYPE.hbDivisionUpgradeFinancialSuccess.index(): HBDivisionUpgradePurchasedSysMessageFormatter(),
         SYS_MESSAGE_TYPE.HBOrderInvoice.index(): HBOrderInvoiceSysMessageFormatter()}

    @property
    def _client_messengerClientFormatters(self):
        from historical_battles.messenger.formatters.service_channel import HBArenaBanSystemMessageFormatter, HBArenaWarningSystemMessageFormatter, HBStateMessageFormatter, HBDivisionLevelUpSysMessageFormatter, HBBattleQuestsSystemMessageFormatter
        from historical_battles.messenger.formatters.service_channel import HBProgressionSystemMessageFormatter
        return {gui_constants.SCH_CLIENT_MSG_TYPE.HB_ARENA_BAN_NOTIFICATIONS: HBArenaBanSystemMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS: HBArenaWarningSystemMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.HB_FRONT_STATE_NOTIFICATION: HBStateMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.HB_PROGRESSION_NOTIFICATIONS: HBProgressionSystemMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.HB_DIVISION_LEVEL_UP: HBDivisionLevelUpSysMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.HB_BATTLE_QUESTS_NOTIFICATIONS: HBBattleQuestsSystemMessageFormatter()}

    @property
    def _client_tokenQuestsSubFormatters(self):
        from historical_battles.messenger.formatters.service_channel import HBMainVehiclePrizeMessageFormatter, HBMainVehiclePrizeCompensationMessageFormatter
        return (HBMainVehiclePrizeMessageFormatter(), HBMainVehiclePrizeCompensationMessageFormatter())

    @property
    def _client_notificationActionHandlers(self):
        from historical_battles.notification.actions_handlers import ShowHBFairPlayActionHandler, ShowHBWarningFairPlayActionHandler, ShowHBProgressionActionHandler, ShowHBEventStartHandler
        return (ShowHBFairPlayActionHandler,
         ShowHBWarningFairPlayActionHandler,
         ShowHBProgressionActionHandler,
         ShowHBEventStartHandler)


BATTLE_EXT_PACKAGES = {hb_constants_extension.ARENA_GUI_TYPE.HB_OFFENCE: ('historical_battles.gui.Scaleform.daapi.view.battle.offence', 'historical_battles.gui.Scaleform.daapi.view.battle.shared'),
 hb_constants_extension.ARENA_GUI_TYPE.HB_DEFENCE: ('historical_battles.gui.Scaleform.daapi.view.battle.defence', 'historical_battles.gui.Scaleform.daapi.view.battle.shared')}
HB_PREVIEW_ALIAS_ITEM = (VIEW_ALIAS.HB_VEHICLE_PREVIEW, isPreviewAvailable)
LOBBY_EXT_PACKAGES = ('historical_battles.gui.Scaleform.daapi.view.lobby', 'historical_battles.gui.Scaleform.daapi.view.lobby.hangar', 'historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview')

def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    initCommonTypes(hb_constants_extension, __name__)
    initSquadCommonTypes(hb_constants_extension, __name__)
    from gui.prb_control.prb_utils import initGuiTypes
    initGuiTypes(prb_config, __name__)
    from historical_battles_common.hb_roster_config import HistoricalBattlesRoster
    battleMode = ClientHistoricalBattlesBattleMode(__name__)
    battleMode.registerGameControllers()
    battleMode.registerClient()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerClientSelector()
    battleMode.registerClientBattleResultsComposer()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerClientSquadSelector()
    battleMode.registerClientPlatoon()
    battleMode.registerBattleControllersRepository()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientNotificationHandlers()
    from historical_battles.gui.game_control import registerHBProgressionAwardControllers
    registerHBProgressionAwardControllers()
    for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
        unitMgrFlag, rosterType = hb_constants_extension.QUEUE_TYPE_TO_UNIT_DATA[queueType]
        addQueueTypeByUnitMgrRoster(queueType, rosterType, __name__)
        addUnitMgrFlagToQueueType(unitMgrFlag, queueType, __name__)

    addPrbTypeByUnitMgrRosterExt(hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, hb_constants_extension.HB_ROSTER_TYPE_GENERAL_MASK, __name__)
    addRosterTypeToClass(hb_constants_extension.ROSTER_TYPE.HB_OFFENCE, HistoricalBattlesRoster, __name__)
    addRosterTypeToClass(hb_constants_extension.ROSTER_TYPE.HB_DEFENCE, HistoricalBattlesRoster, __name__)
    for arenaBonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        addInvitationTypeFromArenaBonusTypeMapping(arenaBonusType, hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, __name__)

    addBattleEventTypesFromExtension(hb_constants_extension.BATTLE_EVENT_TYPE, __name__)
    from gui.battle_control.controllers import feedback_events
    from HBBattleFeedbackComponent import HBBattleFeedbackComponent
    feedback_events._BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({hb_constants_extension.BATTLE_EVENT_TYPE.HB_ACTION_APPLIED: FEEDBACK_EVENT_ID.HB_ACTION_APPLIED})
    feedback_events._PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEEDBACK_EVENT_ID.HB_ACTION_APPLIED: HBBattleFeedbackComponent.unpackHBActionApplied})
    registerLobbyTooltipsBuilders(LOBBY_TOOLTIPS_BUILDERS_PATHS)
    addExtPreviewAliasItem(HB_PREVIEW_ALIAS_ITEM, __name__)
    VIEW_ALIAS.inject(__name__)
    ORIGIN_VIEW_ALIAS.BATTLE_PAGES += (VIEW_ALIAS.HISTORICAL_BATTLES,)
    extendMissionInfoMap(HB_BATTLE_QUESTS_PREFIX, HBMissionInfo, HBDetailedMissionInfo)
    from historical_battles.avatar_input_handler.hb_map_case_mode import HBMapCaseControlMode
    for bonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        OVERWRITE_CTRLS_DESC_MAP[bonusType] = {_CTRL_MODE.RESPAWN_DEATH: (control_modes.PostMortemControlMode, 'postMortemMode', _CTRL_TYPE.USUAL),
         _CTRL_MODE.MAP_CASE: (HBMapCaseControlMode, 'strategicMode', _CTRL_TYPE.USUAL)}

    from historical_battles.services_config import updateServicesConfig
    g_systemEvents.onDependencyConfigReady += updateServicesConfig
    from historical_battles.gui.battle_control.controllers import equipments
    for arenaBonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        consumables.updateEquipmentControllers(arenaBonusType, equipments.HBEquipmentController)
        consumables.updateReplayEquipmentControllers(arenaBonusType, equipments.HBReplayEquipmentController)

    registerHBEquipmentCtrls()
    registerHistoricalBattlesHangarPresets()
    registerIngameHelpPagesBuilder(HBPagesBuilder)


LOBBY_TOOLTIPS_BUILDERS_PATHS = [('historical_battles.gui.Scaleform.daapi.view.tooltips.event_builders', _TOOLTIPS.HISTORICAL_BATTLES_SET)]

def init():
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, LOBBY_EXT_PACKAGES)
    for bonusType, package in BATTLE_EXT_PACKAGES.iteritems():
        g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, package, bonusType)

    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, DEFAULT_NOTIFICATIONS)
    if HAS_DEV_RESOURCES:
        from historical_battles.gui.prb_control import prb_dev
        g_playerEvents.onAccountShowGUI += prb_dev.prbDevSubscribe
    arenaGuiType = hb_constants_extension.ARENA_GUI_TYPE
    from dyn_objects_cache import registerDynObjCache
    from historical_battles.hb_dyn_objects_cache import HistoricalBattlesDynObjects
    for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
        registerDynObjCache(arenaGuiType, HistoricalBattlesDynObjects)

    for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
        VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE.update({arenaGuiType: VIEW_ALIAS.HISTORICAL_BATTLES})

    from arena_component_system.assembler_helper import COMPONENT_ASSEMBLER
    from historical_battles.hb_battle_component_assembler import HBBattleComponentAssembler
    for arenaBonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        COMPONENT_ASSEMBLER.update({arenaBonusType: HBBattleComponentAssembler})

    gui_personality.init()


def start():
    pass


def fini():
    from historical_battles.services_config import updateServicesConfig
    g_systemEvents.onDependencyConfigReady -= updateServicesConfig
    if HAS_DEV_RESOURCES:
        from historical_battles.gui.prb_control import prb_dev
        g_playerEvents.onAccountShowGUI -= prb_dev.prbDevUnsubscribe
    gui_personality.fini()
