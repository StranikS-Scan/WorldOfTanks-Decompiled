# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchPersonality.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from aih_constants import CTRL_TYPE, CTRL_MODE_NAME
from arena_component_system.assembler_helper import ARENA_BONUS_TYPE_CAP_COMPONENTS
from constants_utils import initCommonTypes, initSquadCommonTypes, addAttackReasonTypesFromExtension, addDamageInfoCodes
from GrinchAccountSettings import ACCOUNT_DEFAULT_SETTINGS
from grinch.account_helpers.account_settings import extendAccountSettings
from grinch.arena_components.GrinchVisualStateGOStorage import GrinchVisualStateGOStorage
from grinch.gui import grinch_gui_constants
from grinch.gui.battle_control.controllers.hit_direction_control import GrinchHitDirectionController, GrinchHitDirectionControllerPlayer
from grinch.gui.game_control.awards_controller import GrinchPunishWindowHandler, GrinchRewardsHandler
from grinch.gui.grinch_gui_constants import VIEW_ALIAS, PREBATTLE_ACTION_NAME
from grinch.gui.hangar_presets import registerGrinchHangarPresets
from grinch.gui.Scaleform.genConsts.GRINCH_HANGAR_ALIASES import GRINCH_HANGAR_ALIASES
from grinch.messenger.formatters.token_quest_subformatters import GrinchProgressionRewardsSyncFormatter
from grinch.overrides.hangar_override import HangarOverride
from grinch_common import grinch_constants
from grinch_common.grinch_battle_mode import GrinchBattleMode
from grinch_common.grinch_constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE_CAPS, GameSeasonType, GrinchClientArenaComponents
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes
from gui.Scaleform.framework.managers.loaders import g_viewOverrider
from gui.shared.system_factory import registerAwardControllerHandler

class ClientGrinchBattleMode(GrinchBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.GRINCH_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.GRINCH
    _CLIENT_PRB_ACTION_NAME_SQUAD = PREBATTLE_ACTION_NAME.GRINCH_SQUAD
    _CLIENT_GAME_SEASON_TYPE = GameSeasonType.GRINCH
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = GRINCH_HANGAR_ALIASES.GRINCH_ENTRY_POINT

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['grinch|grinch_lobby.swf']

    @property
    def _client_battleRequiredLibraries(self):
        return ['grinch|grinch_battle.swf']

    @property
    def _client_prbEntityClass(self):
        from grinch.gui.prb_control.entities.pre_queue.entity import GrinchEntity
        return GrinchEntity

    @property
    def _client_prbEntryPointClass(self):
        from grinch.gui.prb_control.entities.pre_queue.entity import GrinchEntryPoint
        return GrinchEntryPoint

    @property
    def _client_prbSquadEntityClass(self):
        from grinch.gui.prb_control.entities.squad.entity import GrinchSquadEntity
        return GrinchSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from grinch.gui.prb_control.entities.squad.entity import GrinchSquadEntryPoint
        return GrinchSquadEntryPoint

    @property
    def _client_gameControllers(self):
        from grinch.skeletons.battle_controller import IGrinchController
        from grinch.gui.game_control.grinch_controller import GrinchController
        return ((IGrinchController, GrinchController, False),)

    @property
    def _client_seasonControllerHandler(self):
        from helpers import dependency
        from grinch.skeletons.battle_controller import IGrinchController
        return lambda *args, **kwargs: dependency.instance(IGrinchController)

    @property
    def _client_battleControllersRepository(self):
        from grinch.gui.battle_control.controllers.repository import GrinchBattleControllerRepository
        return GrinchBattleControllerRepository

    @property
    def _client_sharedControllersRepository(self):
        from grinch.gui.battle_control.controllers.repository import GrinchSharedControllerRepository
        return GrinchSharedControllerRepository

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 20)

    @property
    def _client_modeSelectorItemsClass(self):
        from grinch.gui.impl.lobby.mode_selector.grinch_mode_selector_item import GrinchModeSelectorItem
        return GrinchModeSelectorItem

    @property
    def _client_selectorItemsCreator(self):
        from grinch.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addGrinchBattleType
        return addGrinchBattleType

    @property
    def _client_selectorSquadItemsCreator(self):
        from grinch.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addGrinchSquadType
        return addGrinchSquadType

    @property
    def _client_messengerClientFormatters(self):
        from grinch.messenger.formatters.service_channel import GrinchEventStateMessageFormatter
        return {grinch_gui_constants.SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_STATE: GrinchEventStateMessageFormatter(),
         grinch_gui_constants.SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_PROGRESSION: GrinchProgressionRewardsSyncFormatter()}

    @property
    def _client_platoonViewClass(self):
        from grinch.gui.impl.lobby.platoon.grinch_platoon_members_view import GrinchMembersView
        return GrinchMembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
        return WelcomeView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow))]

    @property
    def _client_providerBattleQueue(self):
        from grinch.gui.Scaleform.daapi.view.lobby.battle_queue_provider import GrinchQueueProvider
        return GrinchQueueProvider

    @property
    def _client_arenaDescrClass(self):
        from grinch.gui.battle_control.arena_info.arena_descrs import GrinchArenaDescription
        return GrinchArenaDescription

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_battleResultStatsCtrlClass(self):
        from grinch.gui.battle_results.composer import GrinchBattleStatsComposer
        return GrinchBattleStatsComposer

    @property
    def _client_messengerServerFormatters(self):
        from grinch.messenger.formatters.service_channel import GrinchBattleResultsFormatter
        from chat_shared import SYS_MESSAGE_TYPE
        return {SYS_MESSAGE_TYPE.grinchBattleResults.index(): GrinchBattleResultsFormatter()}

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from grinch.gui.impl.lobby.banner_entry_point import grinch_banner_entry_point
        return grinch_banner_entry_point.isGrinchBannerEntryPointAvailable

    @property
    def _client_controlModes(self):
        from grinch.avatar_input_handler.grinch_map_case_mode import GrinchArcadeMapCaseControlMode
        return {CTRL_MODE_NAME.MAP_CASE_ARCADE: (GrinchArcadeMapCaseControlMode, 'arcadeMode', CTRL_TYPE.USUAL)}

    @property
    def _client_notificationActionHandlers(self):
        import grinch.notifications.action_handlers as handlers
        return (handlers.GrinchSwitchPrbActionHandler,)


def preInit():
    initCommonTypes(grinch_constants, __name__)
    initSquadCommonTypes(grinch_constants, __name__)
    addAttackReasonTypesFromExtension(grinch_constants.ATTACK_REASON, __name__)
    addDamageInfoCodes(grinch_constants.DAMAGE_INFO_CODES_PER_ATTACK_REASON, __name__)
    initGuiTypes(grinch_gui_constants, __name__)
    initScaleformGuiTypes(grinch_gui_constants, __name__)
    battleMode = ClientGrinchBattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerSquadTypes()
    battleMode.registerVehicleTags()
    battleMode.registerClientSelector()
    battleMode.registerGameControllers()
    battleMode.registerClientSeasonType(grinch_constants)
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerProviderBattleQueue()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerBattleControllersRepository()
    battleMode.registerSharedControllersRepository()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsCtrl()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(grinch_gui_constants)
    battleMode.registerControlModes()
    battleMode.registerDamageHitIndicator(GrinchHitDirectionController, GrinchHitDirectionControllerPlayer)
    battleMode.registerNonReplayMode()
    registerAwardControllerHandler(GrinchPunishWindowHandler)
    registerAwardControllerHandler(GrinchRewardsHandler)
    from grinch.gui.battle_control.controllers import equipment_ctrl
    equipment_ctrl.registerEquipmentsItems()
    ARENA_BONUS_TYPE_CAP_COMPONENTS[GrinchClientArenaComponents.GRINCH_VISUAL_STATE_GO_STORAGE] = (ARENA_BONUS_TYPE_CAPS.GRINCH, GrinchVisualStateGOStorage)
    registerGrinchHangarPresets()


def init():
    extendAccountSettings()
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['grinch.gui.Scaleform.daapi.view.lobby'])
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['grinch.gui.Scaleform.daapi.view.battle'], ARENA_GUI_TYPE.GRINCH)
    g_viewOverrider.addOverride(VIEW_ALIAS.LOBBY_HANGAR, lambda *args, **kwargs: HangarOverride())
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def start():
    pass


def fini():
    pass
