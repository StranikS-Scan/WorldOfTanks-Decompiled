# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles_personality.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.missions.mission_utils import extendMissionInfoMap
from helpers import dependency
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS, KEY_NOTIFICATIONS
from constants_utils import initCommonTypes, initSquadCommonTypes, addClientUnitCmd, addBattleEventTypesFromExtension, addQueueTypeByUnitMgrRoster, addRosterTypeToClass, addUnitMgrFlagToPrbType, addUnitMgrFlagToInvitationType, addUnitMgrFlagToQueueType, addInvitationTypeFromArenaBonusTypeMapping, addPrbTypeByUnitMgrRosterExt
from AvatarInputHandler import control_modes, _CTRL_TYPE
from aih_constants import CTRL_MODE_NAME as _CTRL_MODE
from chat_shared import SYS_MESSAGE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS as ORIGIN_VIEW_ALIAS, VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE
from gui.Scaleform.daapi.view.lobby.header.battle_type_selector_config import addBattlePopoverTooltip, getBattlePopoverToolTip
from gui.impl.lobby.platoon.platoon_config import initPlatoonControllerConfig, addQueueTypeToPrbSquadActionName
from gui.Scaleform.daapi.settings.config_utils import addTooltipBuilder, addOverwriteCtrlsDescMap, addExtPreviewAliasItem, addCtrlDesc
from gui.shared.system_factory import registerSquadFinder
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initPrbSelector, initPrbSquadSelector, addSupportedQueues, addArenaGUITypeByQueueType, addQueueTypeToPrbType
from historical_battles.gui.Scaleform.daapi.view.lobby.missions.hb_missions_helper import HBMissionInfo, HBDetailedMissionInfo
from historical_battles.hb_constants import CTRL_MODE_NAME
from historical_battles_common import hb_constants_extension
from historical_battles.gui.battle_control.hb_battle_constants import FEEDBACK_EVENT_ID
from historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview.hb_vehicle_preview import isPreviewAvailable
from historical_battles.gui.battle_control.arena_info.hb_squad_finder import HBTeamScopeNumberingFinder
from historical_battles.gui.battle_control.controllers.repositories import HBControllersRepository
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.Scaleform.daapi.view.lobby.hangar.entry_point import addSE22EntryPoint
from historical_battles.gui.prb_control import prb_config
from historical_battles.messenger.formatters.service_channel import HBShopBundlePurchasedSysMessageFormatter, HBCouponsBundlePurchasedSysMessageFormatter, HBTankModuleBundlePurchasedSysMessageFormatter, hbAddExtendedBattleModeForBattleResultsNotification, MainPrizeVehicleBundlePurchased
from historical_battles_common.hb_constants import ACCOUNT_DEFAULT_SETTINGS, DEFAULT_NOTIFICATIONS, HB_BATTLE_QUESTS_PREFIX
from system_events import g_systemEvents
from historical_battles.gui.shared import personality as gui_personality
from gui.battle_control.controllers import consumables
from gui.shared.system_factory import registerBattleControllerRepo
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.battle_control.controllers.equipments import registerHBEquipmentCtrls
from gui.shared.system_factory import registerMessengerServerFormatter
from historical_battles import initProgression
from constants import HAS_DEV_RESOURCES
BATTLE_EXT_PACKAGES = {hb_constants_extension.ARENA_GUI_TYPE.HISTORICAL_BATTLES: ('historical_battles.gui.Scaleform.daapi.view.battle.offence', 'historical_battles.gui.Scaleform.daapi.view.battle.shared')}
HB_PREVIEW_ALIAS_ITEM = (VIEW_ALIAS.HB_VEHICLE_PREVIEW, isPreviewAvailable)
LOBBY_EXT_PACKAGES = ('historical_battles.gui.Scaleform.daapi.view.lobby', 'historical_battles.gui.Scaleform.daapi.view.lobby.hangar', 'historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview')
LOBBY_TOOLTIPS_BUILDERS_PATHS = [('historical_battles.gui.Scaleform.daapi.view.tooltips.event_builders', _TOOLTIPS.HISTORICAL_BATTLES_SET)]

def hbServiceFormatters():
    return {SYS_MESSAGE_TYPE.hbShopBundlePurchased.index(): HBShopBundlePurchasedSysMessageFormatter(),
     SYS_MESSAGE_TYPE.hbCouponsBundlePurchased.index(): HBCouponsBundlePurchasedSysMessageFormatter(),
     SYS_MESSAGE_TYPE.hbTankModuleBundlePurchased.index(): HBTankModuleBundlePurchasedSysMessageFormatter(),
     SYS_MESSAGE_TYPE.hbMainPrizeVehiclePurchased.index(): MainPrizeVehicleBundlePurchased()}


@dependency.replace_none_kwargs(ctrl=IGameEventController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isBattlesEnabled()


def registerHBGameControllers():
    from historical_battles.gui.server_events.game_event.hb_game_event_controller import HBGameEventController
    from gui.shared.system_factory import registerGameControllers
    registerGameControllers([(IGameEventController, HBGameEventController, False)])


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    initCommonTypes(hb_constants_extension, __name__)
    from historical_battles_common.hb_roster_config import HistoricalBattlesRoster
    initSquadCommonTypes(hb_constants_extension, __name__)
    registerHBGameControllers()
    for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
        unitMgrFlag, rosterType = hb_constants_extension.QUEUE_TYPE_TO_UNIT_DATA[queueType]
        addQueueTypeByUnitMgrRoster(queueType, rosterType, __name__)
        addUnitMgrFlagToQueueType(unitMgrFlag, queueType, __name__)

    addRosterTypeToClass(hb_constants_extension.HB_ROSTER_TYPE_GENERAL_MASK, HistoricalBattlesRoster, __name__)
    addPrbTypeByUnitMgrRosterExt(hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, hb_constants_extension.HB_ROSTER_TYPE_GENERAL_MASK, __name__)
    addUnitMgrFlagToPrbType(hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, hb_constants_extension.HB_UNIT_MGR_FLAGS_GENERAL_MASK, __name__)
    addUnitMgrFlagToInvitationType(hb_constants_extension.HB_UNIT_MGR_FLAGS_GENERAL_MASK, hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, __name__)
    for arenaBonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        addInvitationTypeFromArenaBonusTypeMapping(arenaBonusType, hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, __name__)

    addClientUnitCmd(hb_constants_extension.CLIENT_UNIT_CMD, __name__)
    prb_config.PREBATTLE_ACTION_NAME.inject(__name__)
    addArenaGUITypeByQueueType(hb_constants_extension.QUEUE_TYPE.HISTORICAL_BATTLES, hb_constants_extension.ARENA_GUI_TYPE.HISTORICAL_BATTLES, __name__)
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
    from historical_battles.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addHistoricalBattlesType, addHistoricalBattlesSquadType
    from historical_battles.gui.prb_control.entities.pre_queue.entity import HistoricalBattlesEntity, HistoricalBattlesEntryPoint
    from historical_battles.gui.impl.lobby.mode_selector.items.historical_battles_mode_selector_item import HistoricalBattlesModeSelectorItem
    initPrbSelector(prb_config, prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES, (ModeSelectorColumns.COLUMN_1, 10), HistoricalBattlesModeSelectorItem, HistoricalBattlesEntryPoint, addHistoricalBattlesType, __name__)
    for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
        addSupportedQueues(queueType, HistoricalBattlesEntity, canSelectPrbEntity, __name__)
        addQueueTypeToPrbType(queueType, hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, __name__)

    from historical_battles.gui.prb_control.entities.squad.entity import HistoricalBattleSquadEntity
    from historical_battles.gui.prb_control.entities.squad.entity import HistoricalBattleSquadEntryPoint
    initPrbSquadSelector(hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES_SQUAD, HistoricalBattleSquadEntity, HistoricalBattleSquadEntryPoint, addHistoricalBattlesSquadType, __name__)
    from historical_battles.gui.impl.lobby.platoon.platoon_members_view import HistoricalBattlesMembersView
    from gui.impl.gen import R
    from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
    initPlatoonControllerConfig(hb_constants_extension.PREBATTLE_TYPE.HISTORICAL_BATTLES, HistoricalBattlesMembersView, [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.historical_battles.lobby.MembersWindow(), MembersWindow))], __name__)
    for queueType in hb_constants_extension.QUEUE_TYPE.HB_RANGE:
        addQueueTypeToPrbSquadActionName(queueType, prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES_SQUAD, __name__)

    addBattleEventTypesFromExtension(hb_constants_extension.BATTLE_EVENT_TYPE, __name__)
    from gui.battle_control.controllers import feedback_events
    from HBBattleFeedbackComponent import HBBattleFeedbackComponent
    feedback_events._BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({hb_constants_extension.BATTLE_EVENT_TYPE.HB_ACTION_APPLIED: FEEDBACK_EVENT_ID.HB_ACTION_APPLIED})
    feedback_events._PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEEDBACK_EVENT_ID.HB_ACTION_APPLIED: HBBattleFeedbackComponent.unpackHBActionApplied})
    for builderSettings in LOBBY_TOOLTIPS_BUILDERS_PATHS:
        addTooltipBuilder(builderSettings, __name__)

    addBattlePopoverTooltip(prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES, getBattlePopoverToolTip(_TOOLTIPS.ENTRY_POINT_TOOLTIP, isWulf=True))
    for arenaGuiType in hb_constants_extension.ARENA_GUI_TYPE.HB_RANGE:
        registerSquadFinder(arenaGuiType, HBTeamScopeNumberingFinder)
        registerBattleControllerRepo(arenaGuiType, HBControllersRepository)

    addExtPreviewAliasItem(HB_PREVIEW_ALIAS_ITEM, __name__)
    VIEW_ALIAS.inject(__name__)
    ORIGIN_VIEW_ALIAS.BATTLE_PAGES += (VIEW_ALIAS.HISTORICAL_BATTLES,)
    SYS_MESSAGE_TYPE.inject(hb_constants_extension.HB_SYS_MESSAGE_TYPES)
    for index, formatter in hbServiceFormatters().items():
        registerMessengerServerFormatter(index, formatter)

    hbAddExtendedBattleModeForBattleResultsNotification()
    extendMissionInfoMap(HB_BATTLE_QUESTS_PREFIX, HBMissionInfo, HBDetailedMissionInfo)
    from historical_battles.avatar_input_handler.hb_map_case_mode import AoeArcadeMapCaseControlMode
    addCtrlDesc(CTRL_MODE_NAME.AOE_MAP_CASE_ARCADE, (AoeArcadeMapCaseControlMode, 'arcadeModeAOE', _CTRL_TYPE.USUAL))
    for bonusType in hb_constants_extension.ARENA_BONUS_TYPE.HB_RANGE:
        addOverwriteCtrlsDescMap(bonusType, _CTRL_MODE.RESPAWN_DEATH, control_modes.PostMortemControlMode, 'postMortemMode')

    from historical_battles.services_config import updateServicesConfig
    g_systemEvents.onDependencyConfigReady += updateServicesConfig
    from historical_battles.gui.battle_results import initBattleResults
    initBattleResults()
    from historical_battles.gui.battle_control.controllers import equipments
    consumables.updateEquipmentControllers(hb_constants_extension.ARENA_BONUS_TYPE.HISTORICAL_BATTLES, equipments.HBEquipmentController)
    consumables.updateReplayEquipmentControllers(hb_constants_extension.ARENA_BONUS_TYPE.HISTORICAL_BATTLES, equipments.HBReplayEquipmentController)
    registerHBEquipmentCtrls()
    from historical_battles.gui.battle_results.composer import HistoryBattleStatsComposer
    from gui.shared.system_factory import registerBattleResultsComposer
    registerBattleResultsComposer(hb_constants_extension.ARENA_BONUS_TYPE.HISTORICAL_BATTLES, HistoryBattleStatsComposer)
    initProgression()


def init():
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, LOBBY_EXT_PACKAGES)
    for bonusType, package in BATTLE_EXT_PACKAGES.iteritems():
        g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, package, bonusType)

    addSE22EntryPoint()
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, DEFAULT_NOTIFICATIONS)
    if HAS_DEV_RESOURCES:
        from historical_battles.gui.prb_control import prb_dev
        g_playerEvents.onAccountShowGUI += prb_dev.prbDevSubscribe
    arenaGuiType = hb_constants_extension.ARENA_GUI_TYPE
    from dyn_objects_cache import registerDynObjCache
    from historical_battles.hb_dyn_objects_cache import HistoricalBattlesDynObjects
    registerDynObjCache(arenaGuiType.HISTORICAL_BATTLES, HistoricalBattlesDynObjects)
    VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE.update({arenaGuiType.HISTORICAL_BATTLES: VIEW_ALIAS.HISTORICAL_BATTLES})
    from arena_component_system.assembler_helper import COMPONENT_ASSEMBLER
    from historical_battles.hb_battle_component_assembler import HBBattleComponentAssembler
    COMPONENT_ASSEMBLER.update({hb_constants_extension.ARENA_BONUS_TYPE.HISTORICAL_BATTLES: HBBattleComponentAssembler})
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
