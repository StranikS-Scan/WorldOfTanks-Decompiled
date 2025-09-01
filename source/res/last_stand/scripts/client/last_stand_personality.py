# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand_personality.py
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from constants import HAS_DEV_RESOURCES
from constants_utils import initCommonTypes, initSquadCommonTypes, addBattleEventTypesFromExtension, addAttackReasonTypesFromExtension, addDamageInfoCodes, addDamageResistanceReasonsFromExtension
from debug_utils import LOG_DEBUG
from aih_constants import CTRL_TYPE, CTRL_MODE_NAME
from last_stand.gui.ls_account_settings import ACCOUNT_DEFAULT_SETTINGS
from last_stand.gui.register_additional_params import registerAdditionalParams, initAdditionalGuiTypes
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from last_stand_common import last_stand_constants
from last_stand.gui import ls_gui_constants
from last_stand.gui.battle_control import ls_battle_constants
from last_stand.control_modes import LSArcadeControlMode, LSSniperControlMode
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes, initBattleCtrlIDs
from gui.shared.system_factory import registerScaleformBattlePackages
from messenger.m_constants import BATTLE_CHANNEL
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE

class ClientLastStandBattleMode(last_stand_constants.LastStandBattleMode):
    _CLIENT_BATTLE_PAGE = ls_gui_constants.VIEW_ALIAS.LAST_STAND_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = ls_gui_constants.PREBATTLE_ACTION_NAME.LAST_STAND
    _CLIENT_PRB_ACTION_NAME_SQUAD = ls_gui_constants.PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = LAST_STAND_HANGAR_ALIASES.LS_ENTRY_POINT

    @property
    def _client_prbEntityClass(self):
        from last_stand.gui.prb_control.entities.pre_queue.entity import LastStandEntity
        return LastStandEntity

    @property
    def _client_canSelectPrbEntity(self):
        from last_stand.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from last_stand.gui.impl.lobby.ls_entry_point import isLSEntryPointAvailable
        return isLSEntryPointAvailable

    @property
    def _client_hangarEventBannerType(self):
        from last_stand.gui.impl.lobby.ls_entry_point import LSEventBanner
        return LSEventBanner

    @property
    def _client_prbEntryPointClass(self):
        from last_stand.gui.prb_control.entities.pre_queue.entity import LastStandEntryPoint
        return LastStandEntryPoint

    @property
    def _client_gameControllers(self):
        from last_stand.skeletons.ls_controller import ILSController
        from last_stand.gui.game_control.ls_controller import LSController
        from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
        from last_stand.gui.game_control.difficulty_level_controller import DifficultyLevelController
        from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
        from last_stand.gui.game_control.ls_artefacts_controller import LSArtefactsController
        from last_stand.skeletons.ls_shop_controller import ILSShopController
        from last_stand.gui.game_control.ls_shop_controller import LSShopController
        from last_stand.skeletons.ls_sound_controller import ILSSoundController
        from last_stand.gui.sounds.ls_sound_controller import LSSoundController
        from last_stand.skeletons.ls_global_chat_controller import ILSGlobalChatController
        from last_stand.gui.game_control.ls_global_chat_controller import LSGlobalChatController
        from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
        from last_stand.gui.game_control.ls_difficulty_missions_controller import LSDifficultyMissionsController
        return ((ILSController, LSController, False),
         (IDifficultyLevelController, DifficultyLevelController, False),
         (ILSArtefactsController, LSArtefactsController, False),
         (ILSShopController, LSShopController, False),
         (ILSSoundController, LSSoundController, False),
         (ILSGlobalChatController, LSGlobalChatController, False),
         (ILSDifficultyMissionsController, LSDifficultyMissionsController, False))

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, -1)

    @property
    def _client_selectorItemsCreator(self):
        from last_stand.gui.scaleform.daapi.view.lobby.header.battle_selector_items import addLastStandType
        return addLastStandType

    @property
    def _client_modeSelectorItemsClass(self):
        from last_stand.gui.impl.lobby.mode_selector.ls_selector_item import LSSelectorItem
        return LSSelectorItem

    @property
    def _client_prbSquadEntityClass(self):
        from last_stand.gui.prb_control.entities.squad.entity import LastStandSquadEntity
        return LastStandSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from last_stand.gui.prb_control.entities.squad.entity import LastStandEntryPoint
        return LastStandEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from last_stand.gui.scaleform.daapi.view.lobby.header.battle_selector_items import addLastStandSquadType
        return addLastStandSquadType

    @property
    def _client_platoonViewClass(self):
        from last_stand.gui.impl.lobby.platoon_members_view import ExtMembersView
        return ExtMembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
        return WelcomeView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.last_stand.lobby.MembersWindow(), MembersWindow))]

    @property
    def _client_arenaDescrClass(self):
        from last_stand.gui.battle_control.arena_info.ls_arena_descrs import LSArenaDescription
        return LSArenaDescription

    @property
    def _client_squadFinderClass(self):
        from last_stand.gui.battle_control.arena_info.ls_squad_finder import LSTeamScopeNumberingFinder
        return LSTeamScopeNumberingFinder

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['last_stand|last_stand_lobby.swf', 'last_stand|components.swf']

    @property
    def _client_battleRequiredLibraries(self):
        return ['last_stand|last_stand_battle.swf']

    @property
    def _client_LobbyContextMenuOptions(self):
        from last_stand.gui.scaleform.daapi.view.lobby.ls_user_cm_handlers import CREATE_LS_SQUAD, lsSquadOptionBuilder, createLSSquadHandler
        return ((CREATE_LS_SQUAD, lsSquadOptionBuilder, createLSSquadHandler),)

    @property
    def _client_DynamicObjectCacheClass(self):
        from ls_dyn_object_cache import _LSDynObjects
        return _LSDynObjects

    @property
    def _client_tokenQuestsSubFormatters(self):
        from last_stand.messenger.formatters.token_quest_subformatters import LSStarterBundleFormatter, LSBattlePassPointsFormatter, LSKingRewardFormatter
        return (LSStarterBundleFormatter(), LSBattlePassPointsFormatter(), LSKingRewardFormatter())

    @property
    def _client_battleControllersRepository(self):
        from last_stand.gui.battle_control.controllers.repositories import LastStandControllerRepository
        return LastStandControllerRepository

    @property
    def _client_sharedControllersRepository(self):
        from last_stand.gui.battle_control.controllers.repositories import LastStandSharedControllersRepository
        return LastStandSharedControllersRepository

    @property
    def _client_battleChannelController(self):
        from last_stand.messenger.gui.channel.bw_chat2.battle_channel_controller import LSTeamChannelController
        return (BATTLE_CHANNEL.TEAM, LSTeamChannelController)

    @property
    def _client_battleResultStatsCtrlClass(self):
        from last_stand.gui.battle_results.composer import LastStandBattleStatsComposer
        return LastStandBattleStatsComposer

    @property
    def _client_battleResultsReusables(self):
        from last_stand.gui.battle_results.reusable import REUSABLE_FACTORY_ITEMS
        return REUSABLE_FACTORY_ITEMS

    @property
    def _client_messengerServerFormatters(self):
        from last_stand.messenger.formatters.service_channel import LSArtefactKeysFormatter, LSBattleResultsFormatter, LSDifficultyLevelFormatter, LSAutoMaintenanceFormatter
        from messenger.formatters.service_channel import InvoiceReceivedFormatter
        return {_SM_TYPE.lsArtefactKeysMessage.index(): LSArtefactKeysFormatter(),
         _SM_TYPE.lsBattleResults.index(): LSBattleResultsFormatter(),
         _SM_TYPE.lsDifficultyRewardCongrats.index(): LSDifficultyLevelFormatter(),
         _SM_TYPE.lsAutoMaintenance.index(): LSAutoMaintenanceFormatter(),
         _SM_TYPE.lsInvoiceReceived.index(): InvoiceReceivedFormatter()}

    @property
    def _client_customizationHangarDisabled(self):
        from last_stand.gui.impl.lobby.ls_helpers import isCustomizationHangarDisabled
        return isCustomizationHangarDisabled

    @property
    def _client_advancedChatComponent(self):
        from last_stand.arena_components.ls_advanced_chat_component import LSAdvancedChatComponent
        return LSAdvancedChatComponent

    @property
    def _client_controlModes(self):
        return {CTRL_MODE_NAME.ARCADE: (LSArcadeControlMode, 'arcadeMode', CTRL_TYPE.USUAL),
         CTRL_MODE_NAME.SNIPER: (LSSniperControlMode, 'sniperMode', CTRL_TYPE.USUAL)}

    @property
    def _client_equipmentTriggers(self):
        from last_stand.gui.battle_control.controllers.equipment_triggers import _EventArtilleryItem, _ReplayEventArtilleryItem
        return [('LSartillery_deathzone', _EventArtilleryItem, _ReplayEventArtilleryItem), ('LSdetonator_deathzone', _EventArtilleryItem, _ReplayEventArtilleryItem)]

    @property
    def _client_equipmentItems(self):
        from last_stand.gui.battle_control.controllers.equipment_items import _HpRepairAndCrewHeal, LSEquipmentReplayItem, LSEquipmentItem, LSSituationalEquipmentItem, _FastReload, _LSInstantShot, _NitroEquipmentReplayItem, _NitroEquipmentItem, _AbilityWithDuration
        return [('LS_selfRepair', _HpRepairAndCrewHeal, LSEquipmentReplayItem),
         ('LS_teamRepair', LSEquipmentItem, LSEquipmentReplayItem),
         ('LS_damageShield', _AbilityWithDuration, LSEquipmentReplayItem),
         ('LS_fastReload', _FastReload, LSEquipmentReplayItem),
         ('LS_aoeDamageInstantShot', _LSInstantShot, LSEquipmentReplayItem),
         ('LS_aoeStunInstantShot', _LSInstantShot, LSEquipmentReplayItem),
         ('LS_aoeDrainEnemyHpInstantShot', _LSInstantShot, LSEquipmentReplayItem),
         ('LS_invisibility', LSEquipmentItem, LSEquipmentReplayItem),
         ('LS_doubleDamage', _AbilityWithDuration, LSEquipmentReplayItem),
         ('LS_nitro', _NitroEquipmentItem, _NitroEquipmentReplayItem),
         ('LS_healSituational', LSSituationalEquipmentItem, LSEquipmentReplayItem),
         ('LS_nitroSituational', LSSituationalEquipmentItem, LSEquipmentReplayItem),
         ('LS_extraDamageSituational', LSSituationalEquipmentItem, LSEquipmentReplayItem)]

    @property
    def _client_equipmentItemsTooltipMovies(self):
        from last_stand.gui.impl.lobby.tank_setup.backports.tooltips import LS_CONSUMABLE_EMPTY_TOOLTIP
        moduleMovies = {'ls_selfRepairKit': 'last_stand|ls_selfRepairKit',
         'ls_teamRepairKit': 'last_stand|ls_teamRepairKit',
         'ls_damageShield': 'last_stand|ls_damageShield',
         'ls_fastReload': 'last_stand|ls_fastReload',
         'ls_invisibility': 'last_stand|ls_invisibility',
         'ls_aoeDamageInstantShot': 'last_stand|ls_aoeDamageInstantShot',
         'ls_aoeStunInstantShot': 'last_stand|ls_aoeStunInstantShot',
         'ls_aoeDrainEnemyHpInstantShot': 'last_stand|ls_aoeDrainEnemyHpInstantShot',
         'ls_doubleDamage': 'last_stand|ls_doubleDamage',
         'ls_nitro': 'last_stand|ls_nitro',
         'ls_healSituational': 'last_stand|ls_healSituational',
         'ls_nitroSituational': 'last_stand|ls_nitroSituational',
         'ls_extraDamageSituational': 'last_stand|ls_extraDamageSituational'}
        advancedTooltipMovies = {LS_CONSUMABLE_EMPTY_TOOLTIP: 'last_stand|ls_equipment'}
        return (moduleMovies, advancedTooltipMovies)

    @property
    def _client_hangarPresetsReader(self):
        from last_stand.gui.hangar_presets.ls_presets_reader import LSPresetsReader
        return LSPresetsReader

    @property
    def _client_hangarPresetsGetter(self):
        from last_stand.gui.hangar_presets.ls_presets_getter import LSPresetsGetter
        return LSPresetsGetter

    @property
    def _client_guiItemsCacheInvalidators(self):
        from LSAccountEquipmentController import LSInventorySessionCache
        return [LSInventorySessionCache.vehInventoryInvalidator]

    @property
    def _client_lowPriorityWulfWindows(self):
        from gui.impl.gen import R
        return [R.views.last_stand.lobby.MembersWindow(), R.views.last_stand.mono.lobby.hangar()]

    @property
    def _client_viewsForMonitoring(self):
        return [LAST_STAND_HANGAR_ALIASES.LS_HANGAR]


class ClientLastStandMediumBattleMode(ClientLastStandBattleMode):
    _ARENA_BONUS_TYPE = last_stand_constants.ARENA_BONUS_TYPE.LAST_STAND_MEDIUM
    _QUEUE_TYPE = last_stand_constants.QUEUE_TYPE.LAST_STAND_MEDIUM

    @property
    def _client_hangarPresetsReader(self):
        return None

    @property
    def _client_hangarPresetsGetter(self):
        from last_stand.gui.hangar_presets.ls_presets_getter import LSMediumPresetsGetter
        return LSMediumPresetsGetter


class ClientLastStandHardBattleMode(ClientLastStandBattleMode):
    _ARENA_BONUS_TYPE = last_stand_constants.ARENA_BONUS_TYPE.LAST_STAND_HARD
    _QUEUE_TYPE = last_stand_constants.QUEUE_TYPE.LAST_STAND_HARD

    @property
    def _client_hangarPresetsReader(self):
        return None

    @property
    def _client_hangarPresetsGetter(self):
        from last_stand.gui.hangar_presets.ls_presets_getter import LSHardPresetsGetter
        return LSHardPresetsGetter


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    initCommonTypes(last_stand_constants, __name__)
    initSquadCommonTypes(last_stand_constants, __name__)
    initGuiTypes(ls_gui_constants, __name__)
    initAdditionalGuiTypes(ls_gui_constants, __name__)
    initScaleformGuiTypes(ls_gui_constants, __name__)
    initBattleCtrlIDs(ls_gui_constants, __name__)
    addBattleEventTypesFromExtension(last_stand_constants.BATTLE_EVENT_TYPE, __name__)
    ls_gui_constants.FEEDBACK_EVENT_ID.inject(__name__)
    ls_battle_constants.VEHICLE_VIEW_STATE.inject(__name__)
    addAttackReasonTypesFromExtension(last_stand_constants.ATTACK_REASON, __name__)
    addDamageResistanceReasonsFromExtension(last_stand_constants.DamageResistanceReason, __name__)
    addDamageInfoCodes(last_stand_constants.DAMAGE_INFO_CODES_PER_ATTACK_REASON, __name__)
    battleMode = ClientLastStandBattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerHangarEventBanner()
    battleMode.registerGameControllers()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerLobbyContextMenuOptions()
    battleMode.registerDynamicObjectCache()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerBattleControllersRepository()
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleChannelController()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerClientBattleResultsCtrl()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientSystemMessagesTypes()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerAutoMaintenanceSysMsgType()
    battleMode.registerCustomizationHangarDecorator()
    battleMode.registerClientEquipmentTriggers()
    battleMode.registerClientEquipmentItems()
    battleMode.registerAttackReasonToCode()
    battleMode.registerClientViewsForMonitoring()
    battleMode.registerClientAdvancedChatComponent()
    battleMode.registerControlModes()
    battleMode.registerGuiItemsCacheInvalidators()
    battleMode.registerLowPriorityWulfWindows()
    battleMediumMode = ClientLastStandMediumBattleMode(__name__)
    battleMediumMode.registerCommon()
    battleMediumMode.registerClientHangarPresets()
    battleMediumMode.registerBattleResultsConfig()
    battleMediumMode.registerClientBattleResultsCtrl()
    battleMediumMode.registerClientBattleResultReusabled()
    battleMediumMode.registerClientAdvancedChatComponent()
    battleMediumMode.registerControlModes()
    battleHardMode = ClientLastStandHardBattleMode(__name__)
    battleHardMode.registerCommon()
    battleHardMode.registerClientHangarPresets()
    battleHardMode.registerBattleResultsConfig()
    battleHardMode.registerClientBattleResultsCtrl()
    battleHardMode.registerClientBattleResultReusabled()
    battleHardMode.registerClientAdvancedChatComponent()
    battleHardMode.registerControlModes()
    registerAdditionalParams(__name__)


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['last_stand.gui.scaleform.daapi.view.lobby',
     'last_stand.gui.scaleform.daapi.view.lobby.store',
     'last_stand.gui.scaleform.daapi.view.lobby.tank_setup',
     'last_stand.gui.impl.lobby'])
    BATTLE_PACKAGES = ('last_stand.gui.scaleform.daapi.view.battle.shared', 'gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics', 'messenger.gui.Scaleform.view.battle')
    registerScaleformBattlePackages(last_stand_constants.ARENA_GUI_TYPE.LAST_STAND, BATTLE_PACKAGES)
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['last_stand.gui.scaleform.daapi.view.battle'], last_stand_constants.ARENA_GUI_TYPE.LAST_STAND)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    if HAS_DEV_RESOURCES:
        from last_stand.gui.development import prb_dev
        prb_dev.prbDevInit()


def start():
    pass


def fini():
    if HAS_DEV_RESOURCES:
        from last_stand.gui.development import prb_dev
        prb_dev.prbDevFini()
