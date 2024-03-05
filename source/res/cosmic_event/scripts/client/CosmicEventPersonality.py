# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicEventPersonality.py
from typing import TYPE_CHECKING
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from constants_utils import initCommonTypes
from cosmic_constants import COSMIC_BANNER_ENTRY_POINT
from cosmic_event.gui import gui_constants
from cosmic_event.gui.game_control.awards_controller import CosmicDailyQuestsHandler, CosmicProgressionTokenQuestsHandler
from cosmic_event.gui.prb_control import prb_config
from cosmic_event_common import cosmic_constants
from cosmic_event_common.cosmic_constants import ARENA_GUI_TYPE, ACCOUNT_DEFAULT_SETTINGS
from cosmic_event_dyn_objects_cache import CosmicEventDynObjects
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes
from gui.shared.system_factory import registerAwardControllerHandler
from gui.limited_ui.lui_rules_storage import LuiRules
if TYPE_CHECKING:
    from typing import Tuple, List, Type
    from skeletons.gui.game_control import IGameController

class ClientCosmicEventBattleMode(cosmic_constants.CosmicEventBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.COSMIC_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = prb_config.PREBATTLE_ACTION_NAME.COSMIC_EVENT
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = COSMIC_BANNER_ENTRY_POINT
    _CLIENT_GAME_SEASON_TYPE = cosmic_constants.GameSeasonType.COSMIC_EVENT

    @property
    def _client_prbEntityClass(self):
        from cosmic_event.gui.prb_control.entities.pre_queue.entity import CosmicEventBattleEntity
        return CosmicEventBattleEntity

    @property
    def _client_canSelectPrbEntity(self):
        from cosmic_event.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from cosmic_event.gui.prb_control.entities.pre_queue.entity import CosmicEventBattleEntryPoint
        return CosmicEventBattleEntryPoint

    @property
    def _client_bannerEntryPointLUIRule(self):
        return LuiRules.GUI_COSMIC_ENTRY_POINT

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 5)

    @property
    def _client_selectorItemsCreator(self):
        from cosmic_event.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addCosmicEventBattlesType
        return addCosmicEventBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        from cosmic_event.gui.impl.lobby.mode_selector.cosmic_mode_selector_item import CosmicEventModeSelectorItem
        return CosmicEventModeSelectorItem

    @property
    def _client_providerBattleQueue(self):
        from cosmic_event.gui.Scaleform.daapi.view.lobby.cosmic_battle_queue import CosmicEventQueueProvider
        return CosmicEventQueueProvider

    @property
    def _client_seasonControllerHandler(self):
        from cosmic_event.gui.game_control.battle_controller import CosmicEventBattleController
        return CosmicEventBattleController

    @property
    def _client_gameControllers(self):
        from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
        from cosmic_event.gui.game_control.battle_controller import CosmicEventBattleController
        from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
        from cosmic_event.gui.game_control.progression_controller import CosmicProgressionController
        return [(ICosmicEventProgressionController, CosmicProgressionController, False), (ICosmicEventBattleController, CosmicEventBattleController, False)]

    @property
    def _client_sharedControllersRepository(self):
        from cosmic_event.gui.battle_control.controllers.repository import CosmicSharedControllersRepository
        return CosmicSharedControllersRepository

    @property
    def _client_battleControllersRepository(self):
        from cosmic_event.gui.battle_control.controllers.repository import CosmicDynamicControllersRepository
        return CosmicDynamicControllersRepository

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from cosmic_event.gui.impl.lobby.banner_entry_point import cosmic_banner_entry_point
        return cosmic_banner_entry_point.isCosmicBannerEntryPointAvailable

    @property
    def _client_battleResultsComposerClass(self):
        from cosmic_event.gui.battle_results.composer import CosmicEventBattleStatsComposer
        return CosmicEventBattleStatsComposer

    @property
    def _client_messengerServerFormatters(self):
        from cosmic_event.messenger.formatters.service_channel import CosmicBattleResultsFormatter
        from chat_shared import SYS_MESSAGE_TYPE
        return {SYS_MESSAGE_TYPE.cosmicEventBattleResults.index(): CosmicBattleResultsFormatter()}

    @property
    def _client_messengerClientFormatters(self):
        import cosmic_event.messenger.formatters.service_channel as formatters
        return {gui_constants.SCH_CLIENT_MSG_TYPE.COSMIC_DAILY: formatters.CosmicDailyMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.COSMIC_EVENT_STATE: formatters.CosmicEventStateMessageFormatter()}

    @property
    def _client_notificationActionHandlers(self):
        import cosmic_event.notifications.action_handlers as handlers
        return (handlers.ProgressionDetailsActionHandler, handlers.CosmicEventOpenHandler)

    @property
    def _client_tokenQuestsSubFormatters(self):
        import cosmic_event.messenger.formatters.service_channel as formatters
        return (formatters.CosmicProgressionMessageFormatter(), formatters.CosmicVehicleRentMessageFormatter(), formatters.CosmicAchievementsMessageFormatter())


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    initCommonTypes(cosmic_constants, __name__)
    initGuiTypes(prb_config, __name__)
    gui_constants.injectClientConstants()
    battleMode = ClientCosmicEventBattleMode(__name__)
    battleMode.registerGameControllers()
    battleMode.registerClient()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerClientSelector()
    battleMode.registerProviderBattleQueue()
    battleMode.registerClientBattleResultsComposer()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientSeasonType(cosmic_constants)
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleControllersRepository()
    battleMode.registerBattleResultsConfig()
    registerAwardControllerHandler(CosmicProgressionTokenQuestsHandler)
    registerAwardControllerHandler(CosmicDailyQuestsHandler)
    from cosmic_event_common.cosmic_constants import registerLootTypes, registerDailyQuestsDecorations
    registerLootTypes(__name__)
    registerDailyQuestsDecorations(__name__)
    from gui.shared.system_factory import registerDynObjCache
    registerDynObjCache(ARENA_GUI_TYPE.COSMIC_EVENT, CosmicEventDynObjects)
    from cosmic_event.gui.battle_control.controllers.consumables import equipment_ctrl
    equipment_ctrl.registerCosmicEventEquipmentsItems()
    from AvatarInputHandler import OVERWRITE_CTRLS_DESC_MAP
    from aih_constants import CTRL_MODE_NAME
    from cosmic_event.cosmic_control_mode import CosmicControlMode, BlackHoleArcadeMapCaseControlMode
    OVERWRITE_CTRLS_DESC_MAP[cosmic_constants.ARENA_BONUS_TYPE.COSMIC_EVENT] = {CTRL_MODE_NAME.ARCADE: (CosmicControlMode, 'cosmicMode', 0),
     CTRL_MODE_NAME.MAP_CASE_ARCADE: (BlackHoleArcadeMapCaseControlMode, 'cosmicMode', 0)}


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['cosmic_event.gui.Scaleform.daapi.view.lobby'])
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['cosmic_event.gui.Scaleform.daapi.view.battle.cosmic'], cosmic_constants.ARENA_GUI_TYPE.COSMIC_EVENT)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def start():
    pass


def fini():
    pass
