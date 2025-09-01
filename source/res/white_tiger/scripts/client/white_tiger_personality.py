# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger_personality.py
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS, KEY_FAVORITES
from constants_utils import initCommonTypes, addAttackReasonTypesFromExtension, addDamageInfoCodes, initSquadCommonTypes
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_HANGAR_ALIASES import WHITE_TIGER_HANGAR_ALIASES
from white_tiger.gui.white_tiger_account_settings import ACCOUNT_DEFAULT_SETTINGS, ACCOUNT_DEFAULT_FAVORITES
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, WHITE_TIGER_BATTLES_SET
from white_tiger_common import wt_constants
from white_tiger.gui import white_tiger_gui_constants
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from white_tiger.gui.battle_control.controllers.equipment_items import registerWTEquipmentsItems
from gui.prb_control.prb_utils import initBattleCtrlIDs
from AvatarInputHandler import OVERWRITE_CTRLS_DESC_MAP
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE
from aih_constants import CTRL_TYPE, CTRL_MODE_NAME
from WTMapCaseMode import HyperionMapCaseControlMode
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from white_tiger.gui.shared.tooltips.white_tiger_advanced import registerWTEquipmentTooltipMovies
from white_tiger.gui.impl.lobby import registerModeToPOMapping, registerWhiteTigerTokenBonus
from white_tiger.gui.server_events import registerWhiteTigerBattleResultsKeys
from gui.shared.system_factory import registerLobbyTooltipsBuilders, registerIgnoredModeForAutoSelectVehicle
from white_tiger.gui.game_control import registerWhiteTigerAwardControllers, registerWhiteTigerSMTypes
from white_tiger.gui.prb_control import registerWhiteTigerPrbParams

class ClientWhiteTigerBattleMode(wt_constants.WhiteTigerBattleMode):
    _CLIENT_PRB_ACTION_NAME = white_tiger_gui_constants.PREBATTLE_ACTION_NAME.WHITE_TIGER
    _CLIENT_PRB_ACTION_NAME_SQUAD = PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD
    _CLIENT_BATTLE_PAGE = white_tiger_gui_constants.VIEW_ALIAS.WHITE_TIGER_BATTLE_PAGE
    _CLIENT_SETTINGS_VIEW_ALIAS = WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_SETTINGS_WINDOW

    @property
    def _client_battleRequiredLibraries(self):
        return ['white_tiger|white_tiger_battle.swf']

    @property
    def _client_LobbyContextMenuOptions(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.white_tiger_user_cm_handlers import CREATE_WHITE_TIGER_SQUAD, whiteTigerSquadOptionBuilder, createWhiteTigerSquadHandler
        return ((CREATE_WHITE_TIGER_SQUAD, whiteTigerSquadOptionBuilder, createWhiteTigerSquadHandler),)

    @property
    def _client_battleResultStatsCtrlClass(self):
        from white_tiger.gui.battle_results.presenter import WhiteTigerBattleResultsPresenter
        return WhiteTigerBattleResultsPresenter

    @property
    def _client_DynamicObjectCacheClass(self):
        from white_tiger_dyn_object_cache import _WhiteTigerDynObjects
        return _WhiteTigerDynObjects

    @property
    def _client_prbEntityClass(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import WhiteTigerEntity
        return WhiteTigerEntity

    @property
    def _client_providerBattleQueue(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.battle_queue_provider import WhiteTigerQueueProvider
        return WhiteTigerQueueProvider

    @property
    def _client_canSelectPrbEntity(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import WhiteTigerEntryPoint
        return WhiteTigerEntryPoint

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, -1)

    @property
    def _client_selectorItemsCreator(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addWhiteTigerType
        return addWhiteTigerType

    @property
    def _client_selectorSquadItemsCreator(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addWhiteTigerSquadType
        return addWhiteTigerSquadType

    @property
    def _client_modeSelectorItemsClass(self):
        from white_tiger.gui.impl.lobby.mode_selector.white_tiger_selector_item import WhiteTigerSelectorItem
        return WhiteTigerSelectorItem

    @property
    def _client_gameControllers(self):
        from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
        from white_tiger.gui.game_control.white_tiger_controller import WhiteTigerController
        from white_tiger.skeletons.economics_controller import IEconomicsController
        from white_tiger.gui.game_control.economics_controller import EconomicsController
        from white_tiger.skeletons.white_tiger_notifications import IWhiteTigerNotifications
        from white_tiger.gui.game_control.white_tiger_notifications import WhiteTigerNotifications
        return ((IWhiteTigerController, WhiteTigerController, False), (IEconomicsController, EconomicsController, False), (IWhiteTigerNotifications, WhiteTigerNotifications, False))

    @property
    def _client_seasonControllerHandler(self):
        from helpers import dependency
        from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
        return lambda *args, **kwargs: dependency.instance(IWhiteTigerController)

    @property
    def _client_battleControllersRepository(self):
        from white_tiger.gui.battle_control.controllers.repositories import WhiteTigerControllerRepository
        return WhiteTigerControllerRepository

    @property
    def _client_sharedControllersRepository(self):
        from white_tiger.gui.battle_control.controllers.repositories import WhiteTigerSharedControllerRepository
        return WhiteTigerSharedControllerRepository

    @property
    def _client_hangarPresetsReader(self):
        from white_tiger.gui.hangar_presets.white_tiger_presets_reader import WhiteTigerPresetsReader
        return WhiteTigerPresetsReader

    @property
    def _client_hangarPresetsGetter(self):
        from white_tiger.gui.hangar_presets.white_tiger_presets_getter import WhiteTigerPresetsGetter
        return WhiteTigerPresetsGetter

    @property
    def _client_messengerServerFormatters(self):
        from white_tiger.messenger.formatters.service_channel import WTTicketTokenWithdrawnFormatter
        from white_tiger.messenger.formatters.service_channel import WTBattleResultsFormatter
        return {_SM_TYPE.wtBattleResults.index(): WTBattleResultsFormatter(),
         _SM_TYPE.wtTicketTokenWithdrawn.index(): WTTicketTokenWithdrawnFormatter()}

    @property
    def _client_prbSquadEntityClass(self):
        from white_tiger.gui.prb_control.entities.squad.entity import WhiteTigerSquadEntity
        return WhiteTigerSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from white_tiger.gui.prb_control.entities.squad.entity import WhiteTigerSquadEntryPoint
        return WhiteTigerSquadEntryPoint

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_platoonViewClass(self):
        from white_tiger.gui.impl.lobby.platoon.wt_platoon_members_view import WhiteTigerMembersView
        return WhiteTigerMembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
        return WelcomeView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.white_tiger.lobby.platoon.MembersWindow(), MembersWindow))]

    @property
    def _client_arenaDescrClass(self):
        from white_tiger.gui.battle_control.arena_info.white_tiger_arena_descrs import WhiteTigerArenaDescription
        return WhiteTigerArenaDescription

    @property
    def _client_notificationActionHandlers(self):
        from white_tiger.notification.action_handlers import _OpenWTEventProgressionHandler
        from white_tiger.notification.action_handlers import _OpenWTEventHandler
        from white_tiger.notification.action_handlers import _OpenWTEventQuestsHandler
        from white_tiger.notification.action_handlers import _OpenWTEventTicketPurchasingHandler
        return (_OpenWTEventProgressionHandler,
         _OpenWTEventHandler,
         _OpenWTEventQuestsHandler,
         _OpenWTEventTicketPurchasingHandler)

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['white_tiger|white_tiger_lobby.swf']

    @property
    def _client_hangarEventBannerType(self):
        from white_tiger.gui.impl.lobby.event_banner import WhiteTigerEventBanner
        return WhiteTigerEventBanner


def _registerArenaComponents():
    from arena_component_system.assembler_helper import ARENA_BONUS_TYPE_CAP_COMPONENTS
    from arena_component_system.overtime_component import OvertimeComponent
    ARENA_BONUS_TYPE_CAP_COMPONENTS[white_tiger_gui_constants.OVERTIME_COMPONENT_NAME] = (wt_constants.ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, OvertimeComponent)


def _registerAdditionalMissionsRewardsPackers():
    from white_tiger.gui.wt_bonus_packers import WTTokenFormatter
    from gui.Scaleform.daapi.view.lobby.missions.missions_helper import _cardAwardsFormatter, _detailedCardAwardsFormatter
    formatter = {'ticket': WTTokenFormatter()}
    _cardAwardsFormatter.addFormatter(formatter)
    _detailedCardAwardsFormatter.addFormatter(formatter)


def preInit():
    initCommonTypes(wt_constants, __name__)
    initGuiTypes(white_tiger_gui_constants, __name__)
    initScaleformGuiTypes(white_tiger_gui_constants, __name__)
    initBattleCtrlIDs(white_tiger_gui_constants, __name__)
    initSquadCommonTypes(wt_constants, __name__)
    registerWTEquipmentTooltipMovies()
    registerWTEquipmentsItems()
    registerModeToPOMapping()
    registerWhiteTigerTokenBonus()
    registerWhiteTigerBattleResultsKeys()
    registerWhiteTigerSMTypes()
    registerWhiteTigerAwardControllers()
    registerWhiteTigerPrbParams()
    OVERWRITE_CTRLS_DESC_MAP[ARENA_BONUS_TYPE.WHITE_TIGER] = {CTRL_MODE_NAME.MAP_CASE: (HyperionMapCaseControlMode, 'strategicMode', CTRL_TYPE.USUAL)}
    addAttackReasonTypesFromExtension(wt_constants.ATTACK_REASON, __name__)
    addDamageInfoCodes(wt_constants.DAMAGE_INFO_CODES_PER_ATTACK_REASON, __name__)
    _registerArenaComponents()
    battleMode = ClientWhiteTigerBattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerGameControllers()
    battleMode.registerProviderBattleQueue()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsCtrl()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerClientSystemMessagesTypes()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerBattleControllersRepository()
    battleMode.registerSharedControllersRepository()
    battleMode.registerDynamicObjectCache()
    battleMode.registerLobbyContextMenuOptions()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerSettingsWindow()
    battleMode.registerHangarEventBanner()
    if not constants.IS_DEVELOPMENT:
        battleMode.registerNonReplayMode()
    registerLobbyTooltipsBuilders([('white_tiger.gui.Scaleform.daapi.view.tooltips.tooltip_builders', WHITE_TIGER_BATTLES_SET)])
    registerIgnoredModeForAutoSelectVehicle([FUNCTIONAL_FLAG.WHITE_TIGER])
    _registerAdditionalMissionsRewardsPackers()


def init():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    AccountSettings.overrideDefaultSettings(KEY_FAVORITES, ACCOUNT_DEFAULT_FAVORITES)
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['white_tiger.gui.Scaleform.daapi.view.battle'], wt_constants.ARENA_GUI_TYPE.WHITE_TIGER)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['white_tiger.gui.Scaleform.daapi.view.lobby', 'white_tiger.gui.impl.lobby'])


def start():
    pass


def fini():
    pass
