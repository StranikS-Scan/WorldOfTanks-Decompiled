# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_personality.py
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from constants import IS_DEVELOPMENT
from constants_utils import initCommonTypes, initSquadCommonTypes
from debug_utils import LOG_DEBUG
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from gui.shared.system_factory import registerAwardControllerHandlers, registerIngameHelpPagesBuilders
from portal_common import portal_constants, injectConsts
from system_events import g_systemEvents
from portal.gui import portal_gui_constants
from portal.gui.Scaleform import registerPortalBattlePackages
from portal.gui.battle_control.controllers.consumables.equipment_ctrl import registerPortalEquipmentCtrls
from portal.gui.battle_control.controllers.repository import registerPortalBattleRepo
from portal_constants import PORTAL_BANNER_ENTRY_POINT
from portal.gui.ingame_help.portal_pages_builder import PortalHelpPagesBuilder

class ClientPortalBattleMode(portal_constants.PortalBattleMode):
    _CLIENT_BATTLE_PAGE = portal_gui_constants.VIEW_ALIAS.PORTAL_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = portal_gui_constants.PREBATTLE_ACTION_NAME.PORTAL_BATTLE
    _CLIENT_PRB_ACTION_NAME_SQUAD = portal_gui_constants.PREBATTLE_ACTION_NAME.PORTAL_BATTLE_SQUAD
    _CLIENT_GAME_SEASON_TYPE = portal_constants.GameSeasonType.PORTAL
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = PORTAL_BANNER_ENTRY_POINT

    @property
    def _client_prbEntityClass(self):
        from portal.gui.prb_control.entities.pre_queue.entity import PortalBattleEntity
        return PortalBattleEntity

    @property
    def _client_canSelectPrbEntity(self):
        from portal.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from portal.gui.prb_control.entities.pre_queue.entity import PortalBattleEntryPoint
        return PortalBattleEntryPoint

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 1)

    @property
    def _client_selectorItemsCreator(self):
        from portal.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addPortalBattlesType
        return addPortalBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        from portal.gui.impl.lobby.mode_selector.portal_mode_selector_item import PortalModeSelectorItem
        return PortalModeSelectorItem

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['portal|portal_lobby.swf', 'portal|portal_common_i18n.swf']

    @property
    def _client_battleRequiredLibraries(self):
        return ['portal|portal_battle.swf', 'portal|portal_common_i18n.swf']

    @property
    def _client_prbSquadEntityClass(self):
        from portal.gui.prb_control.entities.squad.entity import PortalSquadEntity
        return PortalSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from portal.gui.prb_control.entities.squad.entity import PortalEntryPoint
        return PortalEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from portal.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addPortalSquadType
        return addPortalSquadType

    @property
    def _client_platoonViewClass(self):
        from portal.gui.impl.lobby.portal_platoon_members_view import PortalMembersView
        return PortalMembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
        return WelcomeView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.portal.lobby.MembersWindow(), MembersWindow))]

    @property
    def _client_providerBattleQueue(self):
        from portal.gui.Scaleform.daapi.view.lobby.battle_queue_provider import PortalQueueProvider
        return PortalQueueProvider

    @property
    def _client_arenaDescrClass(self):
        from portal.gui.battle_control.arena_info.portal_arena_descrs import PortalArenaDescription
        return PortalArenaDescription

    @property
    def _client_squadFinderClass(self):
        from portal.gui.battle_control.arena_info.portal_squad_finder import PortalTeamScopeNumberingFinder
        return PortalTeamScopeNumberingFinder

    @property
    def _client_battleResultsComposerClass(self):
        from portal.gui.battle_results.composer import PortalBattleStatsComposer
        return PortalBattleStatsComposer

    @property
    def _client_seasonControllerHandler(self):
        from portal.gui.portal_event_control.portal_event_controller import PortalEventController
        return PortalEventController

    @property
    def _client_notificationActionHandlers(self):
        from portal.notification.action_handlers import PortalActionHandler, OpenPortalProgressionHandler
        return (PortalActionHandler, OpenPortalProgressionHandler)

    @property
    def _client_messengerClientFormatters(self):
        from portal.messenger.formatters.service_channel import PortalSystemMessageFormatter
        return {portal_gui_constants.SCH_CLIENT_MSG_TYPE.PORTAL_MSG_TYPE: PortalSystemMessageFormatter()}

    @property
    def _client_messengerServerFormatters(self):
        from portal.messenger.formatters.service_channel import ExtendedBattleResultsFormatter
        return {_SM_TYPE.portalBattleResults.index(): ExtendedBattleResultsFormatter()}

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from portal.gui.impl.lobby.portal_banner_entry_point import isPortalBannerEntryPointAvailable
        return isPortalBannerEntryPointAvailable

    @property
    def _client_bannerEntryPointLUIRule(self):
        return LuiRules.PORTAL_ENTRY_POINT

    @property
    def _client_battleControllersRepository(self):
        from portal.gui.battle_control.controllers.repository import PortalControllerRepository
        return PortalControllerRepository

    def registerAdditionalSystemMessageTypes(self):
        from gui.SystemMessages import SM_TYPE
        SM_TYPE.inject(['PortalProgression',
         'PortalMaxLevelCompleted',
         'PortalAllVehiclesUpgrade',
         'PortalVehicleUpgrade',
         'PortalResetVehicleUpgrade',
         'PortalDifficultyLevelChanged',
         'PortalEventEnabled',
         'PortalEventDisabled'])

    def registerSubFormatters(self):
        from gui.shared.system_factory import registerTokenQuestsSubFormatters
        from portal.messenger.formatters.portal_formatters import PortalProgressionQuestFormatter, PortalLastLevelQuestFormatter, PortalVehicleUpgradeQuestFormatter
        registerTokenQuestsSubFormatters((PortalProgressionQuestFormatter(), PortalLastLevelQuestFormatter(), PortalVehicleUpgradeQuestFormatter()))


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, portal_constants.ACCOUNT_DEFAULT_SETTINGS)
    initCommonTypes(portal_constants, __name__)
    initSquadCommonTypes(portal_constants, __name__)
    initGuiTypes(portal_gui_constants, __name__)
    initScaleformGuiTypes(portal_gui_constants, __name__)
    injectConsts(__name__)
    battleMode = ClientPortalBattleMode(__name__)
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerProviderBattleQueue()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsComposer()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientSeasonType(portal_constants)
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(portal_gui_constants)
    battleMode.registerMessengerServerFormatters()
    battleMode.registerAdditionalSystemMessageTypes()
    battleMode.registerSubFormatters()
    from portal_services_config import updateServicesConfig
    g_systemEvents.onDependencyConfigReady += updateServicesConfig
    from portal.gui.game_control.awards_controller import PortalProgressionAwardHandler
    registerAwardControllerHandlers((PortalProgressionAwardHandler,))
    registerPortalBattlePackages()
    registerPortalEquipmentCtrls()
    from portal.gui.hangar_presets import registerPortalHangarPresets
    registerPortalHangarPresets()
    registerPortalBattleRepo()
    registerIngameHelpPagesBuilders((PortalHelpPagesBuilder,))
    from AvatarInputHandler import OVERWRITE_CTRLS_DESC_MAP
    from aih_constants import CTRL_MODE_NAME, CTRL_TYPE
    from portal.avatar_input_handler.portal_control_modes import PortalPostMortemControlMode
    OVERWRITE_CTRLS_DESC_MAP[portal_constants.ARENA_BONUS_TYPE.PORTAL] = {CTRL_MODE_NAME.POSTMORTEM: (PortalPostMortemControlMode, 'postMortemMode', CTRL_TYPE.USUAL)}


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['portal.gui.Scaleform.daapi.view.lobby'])
    if IS_DEVELOPMENT:
        from portal.gui.development import prb_dev
        prb_dev.prbDevInit()
    from dyn_objects_cache import registerDynObjCache
    from portal.portal_dyn_objects_cache import PortalDynObjects
    registerDynObjCache(portal_constants.ARENA_GUI_TYPE.PORTAL, PortalDynObjects)


def start():
    pass


def fini():
    from portal_services_config import updateServicesConfig
    g_systemEvents.onDependencyConfigReady -= updateServicesConfig
    if IS_DEVELOPMENT:
        from portal.gui.development import prb_dev
        prb_dev.prbDevFini()
