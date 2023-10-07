# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween_personality.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.impl.lobby.mode_selector.items.items_constants import COLUMN_SETTINGS
from halloween_common.halloween_constants import QUEUE_TYPE, PREBATTLE_TYPE
from constants_utils import initCommonTypes, initSquadCommonTypes
from system_events import g_systemEvents
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.backports.context_menu import TANK_SETUP_CARD_CM, TANK_SETUP_SLOT_CM, HANGAR_TANK_SETUP_SLOT_CM
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.shared.system_factory import registerBattleResultsComposer, registerCanSelectPrbEntity, registerAwardControllerHandlers, registerLobbyTooltipsBuilders
from gui.prb_control.prb_utils import initGuiTypes, addPrbTypeToQueueType, addArenaGUITypeByQueueType, addQueueTypeToPrbType
from gui.shared.system_factory import registerBattleQueueProvider
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout, QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME, PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY, PREBATTLE_TYPE_TO_VEH_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, default_maps_ctrl, team_bases_recapturable_ctrl
from halloween.gui.battle_control.controllers import battle_hints_ctrl
from gui.battle_control.controllers.repositories import registerBattleControllerRepo, _ControllersRepositoryByBonuses
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
import dyn_objects_cache
from halloween.hw_constants import HWTooltips
from halloween_common import halloween_constants
from halloween.gui import halloween_gui_constants
from halloween.messenger.formatters.collections_by_type import addHW22ClientFormatters
from halloween.notification.actions_handler import addHW22ActionHandlers
from halloween.gui.battle_control.controllers.hw_equipment_ctrl import registerHWEquipmentCtrls
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_entry_point import addHW22EntryPoint, canSelectPrbEntityFun
from halloween.hw_constants import ACCOUNT_DEFAULT_SETTINGS
from halloween.gui.game_control.award_handlers import HWBattleQuestsRewardHandler, HWInvoiceCrewBonusHandler
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HelpHintContext
from gui.shared.system_factory import registerIngameHelpPagesBuilder
from gui.ingame_help import detailed_help_pages
from gui.ingame_help.detailed_help_pages import addPage, DetailedHelpPagesBuilder
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.system_factory import registerDynObjCache
import CGF
LOBBY_EXT_PACKAGES = ('halloween.gui.Scaleform.daapi.view.lobby', 'halloween.gui.Scaleform.daapi.view.lobby.hangar', 'halloween.gui.Scaleform.daapi.view.lobby.tank_setup')
BATTLE_EXT_PACKAGES = ('halloween.gui.Scaleform.daapi.view.battle',)
TOOLTIP_PACKAGES = [('halloween.gui.Scaleform.daapi.view.tooltips.halloween_lobby_builders', HWTooltips.HW_LOBBY_SET)]
HW_AWARD_HANDLERS = [HWBattleQuestsRewardHandler, HWInvoiceCrewBonusHandler]

class _HalloweenDynObjects(dyn_objects_cache._BattleRoyaleDynObjects):
    _LOOT_TYPES = 'halloweenLootTypes'

    def __init__(self):
        super(_HalloweenDynObjects, self).__init__()
        self.__inspiringEffect = None
        self.__friendPrefab = ''
        self.__enemyPrefab = ''
        self.__cachedPrefabs = []
        return

    def init(self, dataSection):
        if self._initialized:
            return
        self.__friendPrefab = dataSection['hwFrozenMantle'].readString('friend')
        self.__enemyPrefab = dataSection['hwFrozenMantle'].readString('enemy')
        self.__cachedPrefabs.append(self.__friendPrefab)
        self.__cachedPrefabs.append(self.__enemyPrefab)
        CGF.cacheGameObjects(self.__cachedPrefabs, False)
        super(_HalloweenDynObjects, self).init(dataSection)

    def getFriendPrefab(self):
        return self.__friendPrefab

    def getEnemyPrefab(self):
        return self.__enemyPrefab

    def destroy(self):
        self.clear()

    def clear(self):
        if self.__cachedPrefabs:
            CGF.clearGameObjectsCache(self.__cachedPrefabs)
            self.__cachedPrefabs = []
        self._initialized = False


class ClientHalloweenBattleMode(halloween_constants.HalloweenBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.CLASSIC_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE
    _CLIENT_PRB_ACTION_NAME_SQUAD = halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE_SQUAD
    _CLIENT_GAME_SEASON_TYPE = halloween_constants.GameSeasonType.HALLOWEEN_BATTLES

    def registerClient(self):
        super(ClientHalloweenBattleMode, self).registerClient()
        addArenaGUITypeByQueueType(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, self._ARENA_GUI_TYPE, self._personality)
        addQueueTypeToPrbType(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, self._PREBATTLE_TYPE, self._personality)
        addPrbTypeToQueueType(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, self._PREBATTLE_TYPE, self._personality)

    @property
    def _client_gameControllers(self):
        from halloween.gui.game_control.halloween_controller import HalloweenController
        from skeletons.gui.game_control import IHalloweenController
        from halloween.gui.game_control.visibility_layer_controller import VisibilityLayerController
        from halloween.skeletons.gui.visibility_layer_controller import IHalloweenVisibilityLayerController
        from halloween.gui.sounds.sound_controller import HWSoundController
        from halloween.skeletons.gui.sound_controller import IHWSoundController
        return ((IHalloweenController, HalloweenController, False), (IHalloweenVisibilityLayerController, VisibilityLayerController, False), (IHWSoundController, HWSoundController, False))

    @property
    def _client_arenaDescrClass(self):
        from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
        import BattleReplay

        class EventBattleArenaDescription(ArenaWithLabelDescription):

            def getWinString(self, isInBattle=True):
                return backport.text(R.strings.hw_ingame_gui.loading.battleTypes.description())

            def isInvitationEnabled(self):
                replayCtrl = BattleReplay.g_replayCtrl
                return not replayCtrl.isPlaying

        return EventBattleArenaDescription

    @property
    def _client_battleControllersRepository(self):
        from gui.battle_control.controllers.repositories import EventControllerRepository
        return EventControllerRepository

    @property
    def _client_selectorItemsCreator(self):
        from halloween.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addHalloweenBattleType
        return addHalloweenBattleType

    @property
    def _client_selectorSquadItemsCreator(self):
        from halloween.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addHalloweenSquadType
        return addHalloweenSquadType

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_modeSelectorItemsClass(self):
        from halloween.gui.impl.lobby.mode_selector.halloween_mode_selector_item import HalloweenModeSelectorItem
        return HalloweenModeSelectorItem

    @property
    def _client_prbEntityClass(self):
        from halloween.gui.prb_control.entities.pre_queue.entity import HalloweenBattleEntity
        return HalloweenBattleEntity

    @property
    def _client_prbEntryPointClass(self):
        from halloween.gui.prb_control.entities.pre_queue.entity import HalloweenBattleEntryPoint
        return HalloweenBattleEntryPoint

    @property
    def _client_prbSquadEntityClass(self):
        from halloween.gui.prb_control.entities.squad.entity import HalloweenBattleSquadEntity
        return HalloweenBattleSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from halloween.gui.prb_control.entities.squad.entity import HalloweenBattleSquadEntryPoint
        return HalloweenBattleSquadEntryPoint

    @property
    def _client_providerBattleQueue(self):
        from halloween.gui.Scaleform.daapi.view.lobby.battle_queue_provider import HalloweenQueueProvider
        return HalloweenQueueProvider

    @property
    def _client_canSelectPrbEntity(self):
        return canSelectPrbEntityFun

    @property
    def _client_platoonViewClass(self):
        from halloween.gui.impl.lobby.platoon.HalloweenMemberView import HalloweenMemberView
        return HalloweenMemberView

    @property
    def _client_platoonWelcomeViewClass(self):
        return WelcomeView

    @property
    def _client_platoonLayouts(self):
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow))]


def preInit():
    initCommonTypes(halloween_constants, __name__)
    initSquadCommonTypes(halloween_constants, __name__)
    initGuiTypes(halloween_gui_constants, __name__)
    battleMode = ClientHalloweenBattleMode(__name__)
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerGameControllers()
    battleMode.registerProviderBattleQueue()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientSeasonType(halloween_constants)
    __registerPrebatles()
    registerHWEquipmentCtrls()
    registerLobbyTooltipsBuilders(TOOLTIP_PACKAGES)
    from halloween.gui.battle_results.composer import HalloweenBattleStatsComposer
    registerBattleResultsComposer(halloween_constants.ARENA_BONUS_TYPE.HALLOWEEN_BATTLES, HalloweenBattleStatsComposer)
    registerBattleResultsComposer(halloween_constants.ARENA_BONUS_TYPE.HALLOWEEN_BATTLES_WHEEL, HalloweenBattleStatsComposer)
    registerCanSelectPrbEntity(halloween_constants.QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, canSelectPrbEntityFun)
    TANK_SETUP_CARD_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HW_CONSUMABLE_ITEM})
    TANK_SETUP_SLOT_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HW_CONSUMABLE_SLOT})
    HANGAR_TANK_SETUP_SLOT_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_HW_CONSUMABLE_SLOT})
    from gui.shared.gui_items.marker_items import MarkerParamsFactory
    from halloween.gui.Scaleform.daapi.view.battle.entity_markers import HW_MARKERS
    for markerStyle, markerParams in HW_MARKERS.items():
        MarkerParamsFactory.registerMarker(markerStyle, markerParams)

    registerAwardControllerHandlers(HW_AWARD_HANDLERS)
    data = {halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE: (ModeSelectorColumns.COLUMN_1, 40)}
    COLUMN_SETTINGS.update(data)
    from constants import ARENA_GUI_TYPE_LABEL
    data = {halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES: 'event'}
    ARENA_GUI_TYPE_LABEL.LABELS.update(data)
    registerHalloweenOthersParams()
    registerHalloweenRepositories()
    from gui.Scaleform.daapi.view.battle.shared.frag_correlation_bar import GuiTypeViewStateBehaviour, _GUI_TYPE_VIEW_STATE_BEHAVIOUR
    data = {halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES: GuiTypeViewStateBehaviour(False, False, False, True, True, True)}
    _GUI_TYPE_VIEW_STATE_BEHAVIOUR.update(data)
    g_systemEvents.onDependencyConfigReady += updateServicesConfig
    registerIngameHelpPagesBuilder(HalloweenPagesBuilder)


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, LOBBY_EXT_PACKAGES)
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, BATTLE_EXT_PACKAGES, halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    addHW22EntryPoint()
    addHW22ActionHandlers()
    addHW22ClientFormatters()


def start():
    pass


def fini():
    g_systemEvents.onDependencyConfigReady -= updateServicesConfig


def updateServicesConfig(manager):
    from skeletons.gui.battle_results import IBattleResultsService
    from halloween.gui.game_control.halloween_battle_result_service import HalloweenBattleResultService
    resultsService = HalloweenBattleResultService()
    resultsService.init()
    manager.replaceInstance(IBattleResultsService, resultsService)


def __registerPrebatles():
    from halloween.gui.Scaleform.daapi.view.lobby.battle_queue_provider import HalloweenWheeledVehiclesQueueProvider
    registerBattleQueueProvider(halloween_constants.QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, HalloweenWheeledVehiclesQueueProvider)
    data = {QUEUE_TYPE.HALLOWEEN_BATTLES: halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE_SQUAD,
     QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL: halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE_SQUAD}
    QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME.update(data)
    data = {PREBATTLE_TYPE.HALLOWEEN_BATTLES: WelcomeView}
    PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY.update(data)
    data = {PREBATTLE_TYPE.HALLOWEEN_BATTLES: WelcomeView}
    PREBATTLE_TYPE_TO_VEH_CRITERIA.update(data)
    registerDynObjCache(halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES, _HalloweenDynObjects)


def registerHalloweenOthersParams():
    from gui.shared.system_factory import registerPrbStorage, registerQueueEntity
    from gui.prb_control.storages import makeQueueName
    from halloween.gui.prb_control.storage.halloween_storage import HalloweenStorage
    from halloween.gui.prb_control.entities.pre_queue.entity import HalloweenBattleEntity
    registerPrbStorage(makeQueueName(QUEUE_TYPE.HALLOWEEN_BATTLES), HalloweenStorage())
    registerQueueEntity(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL, HalloweenBattleEntity)


class HalloweenControllerRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(HalloweenControllerRepository, cls).create(setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(battle_hints_ctrl.createBattleHintsController(), setup)
        repository.addArenaController(EventAppearanceCacheController(setup), setup)
        repository.addArenaViewController(team_bases_recapturable_ctrl.TeamsBasesRecapturableController(), setup)
        return repository


def registerHalloweenRepositories():
    registerBattleControllerRepo(halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES, HalloweenControllerRepository)


class HalloweenPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isHalloween',)

    @classmethod
    def priority(cls):
        return detailed_help_pages.HelpPagePriority.DEFAULT

    @classmethod
    def buildPages(cls, ctx):
        R_HELP_STRINGS = R.strings.hw_ingame_help.detailsHelp
        R_HELP_IMAGES = R.images.halloween.gui.maps.icons.battleHelp
        pages = []
        headerTitle = backport.text(R.strings.hw_ingame_help.detailsHelp.title())
        for page in ('pageTask', 'pageRespawn', 'pageAbility', 'pageLanterns'):
            addPage(datailedList=pages, headerTitle=headerTitle, title=backport.text(R_HELP_STRINGS.dyn(page).title()), descr=text_styles.mainBig(backport.text(R_HELP_STRINGS.dyn(page).desc())), vKeys=[], buttons=[], image=backport.image(R_HELP_IMAGES.dyn(page)()), hintCtx=HelpHintContext.EVENT_BATTLE)

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isHalloween'] = arenaVisitor.getArenaGuiType() == halloween_constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES
