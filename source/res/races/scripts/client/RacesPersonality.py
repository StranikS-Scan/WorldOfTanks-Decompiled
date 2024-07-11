# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/RacesPersonality.py
from races_common import races_constants
from constants_utils import initCommonTypes, deselectLobbyHeaderButtons
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.prb_control.prb_utils import initGuiTypes
from gui.shared.system_factory import registerAwardControllerHandler
from gui.shared.system_factory import registerScaleformBattlePackages, registerScaleformLobbyPackages
from races.gui import gui_constants
from races.gui.game_control.awards_controller import RacesProgressionTokenQuestsHandler, RacesWelcomeQuestHandler, RacesFirstWinQuestHandler
from races.gui.prb_control import prb_config

class ClientRacesBattleMode(races_constants.RacesBattleMode):
    _CLIENT_GAME_SEASON_TYPE = races_constants.GameSeasonType.RACES
    _CLIENT_PRB_ACTION_NAME = prb_config.PREBATTLE_ACTION_NAME.RACES
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.RACES_BATTLE_PAGE
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = HANGAR_ALIASES.RACES_BANNER_ENTRY_POINT

    @property
    def _client_gameControllers(self):
        from races.skeletons.progression_controller import IRacesProgressionController
        from races.gui.game_control.progression_controller import RacesProgressionController
        from skeletons.gui.game_control import IRacesBattleController
        from races.gui.game_control.races_battle_controller import RacesBattleController
        from skeletons.gui.game_control import IRacesVisibilityLayerController
        from races.gui.game_control.visibility_layer_controller import RacesVisibilityLayerController
        return ([IRacesProgressionController, RacesProgressionController, False], [IRacesBattleController, RacesBattleController, False], [IRacesVisibilityLayerController, RacesVisibilityLayerController, False])

    @property
    def _client_sharedControllersRepository(self):
        from races.gui.battle_control.controllers.repository import RacesSharedControllersRepository
        return RacesSharedControllersRepository

    @property
    def _client_seasonControllerHandler(self):
        from races.gui.game_control.races_battle_controller import RacesBattleController
        return RacesBattleController

    @property
    def _client_battleResultsComposerClass(self):
        from races.gui.battle_results.composer import RacesEventBattleStatsComposer
        return RacesEventBattleStatsComposer

    @property
    def _client_prbEntityClass(self):
        from races.gui.prb_control.entities.pre_queue.entity import RacesEntity
        return RacesEntity

    @property
    def _client_canSelectPrbEntity(self):
        from races.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_messengerServerFormatters(self):
        from races.messenger.formatters.service_channel import RacesBattleResultsFormatter
        from chat_shared import SYS_MESSAGE_TYPE
        return {SYS_MESSAGE_TYPE.RacesBattleResults.index(): RacesBattleResultsFormatter()}

    @property
    def _client_selectorItemsCreator(self):
        from races.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addRacesBattlesType
        return addRacesBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        from races.gui.impl.lobby.mode_selector.races_mode_selector_item import RacesModeSelectorItem
        return RacesModeSelectorItem

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 10)

    @property
    def _client_prbEntryPointClass(self):
        from races.gui.prb_control.entities.pre_queue.entity import RacesBattleEntryPoint
        return RacesBattleEntryPoint

    @property
    def _client_providerBattleQueue(self):
        from races.gui.prb_control.races_queue import RacesQueueProvider
        return RacesQueueProvider

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from races.gui.impl.lobby.races_banner import races_banner_view
        return races_banner_view.isRacesBannerAvailable

    @property
    def _client_messengerClientFormatters(self):
        import races.messenger.formatters.service_channel as formatters
        return {gui_constants.SCH_CLIENT_MSG_TYPE.RACES_STATE: formatters.RacesStateMessageFormatter(),
         gui_constants.SCH_CLIENT_MSG_TYPE.RACES_LOOT_BOXES_ACCRUAL: formatters.RacesLootBoxesAccrual()}

    @property
    def _client_notificationActionHandlers(self):
        import races.notifications.action_handlers as handlers
        return (handlers.RacesOpenHandler, handlers.RacesLootBoxesAccrualHandler)

    @property
    def _client_tokenQuestsSubFormatters(self):
        import races.messenger.formatters.service_channel as formatters
        return (formatters.RacesProgressionMessageFormatter(),)


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    initCommonTypes(races_constants, __name__)
    initGuiTypes(prb_config, __name__)
    gui_constants.injectClientConstants()
    battleMode = ClientRacesBattleMode(__name__)
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerGameControllers()
    battleMode.registerProviderBattleQueue()
    battleMode.registerClientBattleResultsComposer()
    battleMode.registerClientSeasonType(races_constants)
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleResultsConfig()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerClientNotificationHandlers()
    battleMode.registerClientTokenQuestsSubFormatters()
    registerAwardControllerHandler(RacesProgressionTokenQuestsHandler)
    registerAwardControllerHandler(RacesWelcomeQuestHandler)
    registerAwardControllerHandler(RacesFirstWinQuestHandler)
    from races.gui.battle_control.controllers.consumables import equipment_ctrl
    equipment_ctrl.registerRacesEquipmentsItems()
    from AvatarInputHandler import OVERWRITE_CTRLS_DESC_MAP
    from aih_constants import CTRL_MODE_NAME
    from races.races_control_mode import RacesControlMode
    OVERWRITE_CTRLS_DESC_MAP[races_constants.ARENA_BONUS_TYPE.RACES] = {CTRL_MODE_NAME.ARCADE: (RacesControlMode, 'racesMode', 0)}
    from gui.impl.gen import R
    alias = R.views.races.lobby.races_lobby_view.RacesLobbyView()
    deselectLobbyHeaderButtons(alias, __name__)


def init():
    LOG_DEBUG('init', __name__)
    registerScaleformBattlePackages(races_constants.ARENA_GUI_TYPE.RACES, ('races.gui.Scaleform.daapi.view.battle.races', 'races.gui.Scaleform.daapi.view.battle.shared', 'messenger.gui.Scaleform.view.battle'))
    registerScaleformLobbyPackages(('races.gui.Scaleform.daapi.view.lobby',))


def start():
    pass


def fini():
    pass
