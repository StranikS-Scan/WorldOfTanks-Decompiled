# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/Comp7ExtensionPersonality.py
from comp7.gui import comp7_constants
from comp7.gui.Scaleform import registerComp7Scaleform
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME
from comp7.gui.impl.battle import registerComp7Battle
from comp7.gui.impl.lobby import registerComp7Lobby
from comp7.gui.prb_control import registerComp7OthersPrbParams
from comp7_common import comp7_constants as comp7_common_constants
from comp7_common import injectConsts, injectSquadConsts
from comp7_common.comp7_battle_mode import Comp7BattleMode
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes, initRequestType, initBattleCtrlIDs
_LOBBY_EXT_PACKAGES = ['comp7.gui.Scaleform.daapi.view.lobby.profile', 'comp7.gui.Scaleform.daapi.view.lobby.header', 'comp7.gui.Scaleform.daapi.view.lobby.missions.regular']
_BATTLE_EXT_PACKAGES = ['comp7.gui.Scaleform.daapi.view.battle.shared']

class ClientComp7BattleMode(Comp7BattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.COMP7_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.COMP7
    _CLIENT_PRB_ACTION_NAME_SQUAD = PREBATTLE_ACTION_NAME.COMP7_SQUAD
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = HANGAR_ALIASES.COMP7_ENTRY_POINT
    _CLIENT_REPLAY_MODE_TAG = 'Onslaught'
    _CLIENT_GAME_SEASON_TYPE = comp7_common_constants.GameSeasonType.COMP7

    @property
    def _client_prbEntityClass(self):
        from comp7.gui.prb_control.entities.pre_queue.entity import Comp7Entity
        return Comp7Entity

    @property
    def _client_canSelectPrbEntity(self):

        def canSelectComp7PrbEntity():
            return True

        return canSelectComp7PrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from comp7.gui.prb_control.entities.pre_queue.entity import Comp7EntryPoint
        return Comp7EntryPoint

    @property
    def _client_providerBattleQueue(self):
        from comp7.gui.Scaleform.daapi.view.lobby.battle_queue import Comp7QueueProvider
        return Comp7QueueProvider

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_2, 10)

    @property
    def _client_selectorItemsCreator(self):
        from comp7.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addComp7BattleType
        return addComp7BattleType

    @property
    def _client_modeSelectorItemsClass(self):
        from comp7.gui.impl.lobby.mode_selector.items.comp7_mode_selector_item import Comp7ModeSelectorItem
        return Comp7ModeSelectorItem

    @property
    def _client_prbSquadEntityClass(self):
        from comp7.gui.prb_control.entities.squad.entity import Comp7SquadEntity
        return Comp7SquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from comp7.gui.prb_control.entities.squad.entity import Comp7SquadEntryPoint
        return Comp7SquadEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from comp7.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addComp7SquadType
        return addComp7SquadType

    @property
    def _client_squadFinderClass(self):
        from comp7.gui.battle_control.arena_info.squad_finder import Comp7TeamScopeNumberingFinder
        return Comp7TeamScopeNumberingFinder

    @property
    def _client_arenaDescrClass(self):
        from comp7.gui.battle_control.arena_info.arena_descrs import Comp7BattlesDescription
        return Comp7BattlesDescription

    @property
    def _client_bannerEntryPointLUIRule(self):
        from gui.limited_ui.lui_rules_storage import LUI_RULES
        return LUI_RULES.Comp7EntryPoint

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from comp7.gui.Scaleform.daapi.view.lobby.comp7_entry_point import isComp7EntryPointAvailable
        return isComp7EntryPointAvailable

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.comp7.lobby.MembersWindow(), MembersWindow))]

    @property
    def _client_platoonViewClass(self):
        from comp7.gui.impl.lobby.platoon.view.platoon_members_view import Comp7MembersView
        return Comp7MembersView

    @property
    def _client_platoonWelcomeViewClass(self):
        from comp7.gui.impl.lobby.platoon.view.comp7_platoon_welcome_view import Comp7WelcomeView
        return Comp7WelcomeView

    @property
    def _client_notificationActionHandlers(self):
        from comp7.notification.actions_handlers import OpenComp7ShopHandler, OpenBondEquipmentSelection
        return (OpenComp7ShopHandler, OpenBondEquipmentSelection)

    @property
    def _client_tokenQuestsSubFormatters(self):
        from comp7.messenger.formatters.token_quest_subformatters import Comp7RewardsFormatter
        return (Comp7RewardsFormatter(),)

    @property
    def _client_gameControllers(self):
        from skeletons.gui.game_control import IComp7Controller
        from comp7.skeletons.gui.game_control import IComp7ShopController
        from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
        from comp7.gui.game_control.comp7_controller import Comp7Controller
        from comp7.gui.game_control.comp7_shop_controller import Comp7ShopController
        from comp7.gui.game_control.comp7_weekly_quests_controller import Comp7WeeklyQuestsController
        return ((IComp7Controller, Comp7Controller, True), (IComp7ShopController, Comp7ShopController, False), (IComp7WeeklyQuestsController, Comp7WeeklyQuestsController, False))

    @property
    def _client_battleResultStatsCtrlClass(self):
        from comp7.gui.battle_results.composer import Comp7StatsComposer
        return Comp7StatsComposer

    @property
    def _client_battleResultsReusables(self):
        from gui.battle_results.reusable.extension_utils import ReusableInfoFactory
        from comp7.gui.battle_results.reusable.shared import Comp7VehicleDetailedInfo, Comp7VehicleSummarizeInfo
        return {ReusableInfoFactory.Keys.VEHICLE_DETAILED: Comp7VehicleDetailedInfo,
         ReusableInfoFactory.Keys.VEHICLE_SUMMARIZED: Comp7VehicleSummarizeInfo}

    @property
    def _client_battleControllersRepository(self):
        from comp7.gui.battle_control.controllers.repositories import Comp7ControllerRepository
        return Comp7ControllerRepository

    @property
    def _client_ammunitionPanelViews(self):
        from comp7.gui.impl.lobby.tank_setup.ammunition_panel import Comp7AmmunitionPanelView
        return (Comp7AmmunitionPanelView,)

    @property
    def _client_messengerServerFormatters(self):
        from chat_shared import SYS_MESSAGE_TYPE
        from comp7.messenger.formatters.service_channel import Comp7BattleResultsFormatter
        return {SYS_MESSAGE_TYPE.comp7BattleResults.index(): Comp7BattleResultsFormatter()}

    @property
    def _client_LobbyContextMenuOptions(self):
        from comp7.gui.Scaleform.daapi.view.lobby.user_cm_handlers import createComp7Squad, addComp7SquadInfo
        from comp7.gui.Scaleform.daapi.view.lobby.lobby_constants import USER
        return ((USER.CREATE_COMP7_SQUAD, addComp7SquadInfo, createComp7Squad),)

    @property
    def _client_hangarPresetsGetter(self):
        from comp7.gui.hangar_presets.hangar_presets_getters import Comp7PresetsGetter
        return Comp7PresetsGetter

    @property
    def _client_DynamicObjectCacheClass(self):
        from comp7.comp7_dyn_objects_cache import Comp7DynObjects
        return Comp7DynObjects

    @property
    def _client_seasonControllerHandler(self):
        from comp7.gui.game_control.comp7_controller import Comp7Controller
        return Comp7Controller

    @property
    def _client_battleRequiredLibraries(self):
        return ['comp7|comp7_battle.swf', 'comp7|minimapEntriesLibrary.swf']

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['comp7|comp7_lobby.swf']

    def registerAdditionalScaleformRequiredLibraries(self):
        from comp7_common.comp7_constants import ARENA_GUI_TYPE
        from gui.Scaleform.required_libraries_config import addBattleRequiredLibraries
        for guiType in (ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            addBattleRequiredLibraries(self._client_battleRequiredLibraries, guiType, self._personality)

    def registerAdditionalBattleResultsCtrl(self):
        from constants import ARENA_BONUS_TYPE
        from gui.shared.system_factory import registerBattleResultStatsCtrl
        from comp7.gui.battle_results.composer import TournamentComp7StatsComposer, TrainingComp7StatsComposer
        registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.TOURNAMENT_COMP7, TournamentComp7StatsComposer)
        registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.TRAINING_COMP7, TrainingComp7StatsComposer)

    def registerAdditionalBattleRepository(self):
        from comp7_common.comp7_constants import ARENA_GUI_TYPE
        from gui.shared.system_factory import registerBattleControllerRepo
        for guiType in (ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            registerBattleControllerRepo(guiType, self._client_battleControllersRepository)

    def registerAdditionalBattleResultReusabled(self):
        from constants import ARENA_BONUS_TYPE
        from gui.battle_results.reusable import ReusableInfoFactory
        for bonusType in (ARENA_BONUS_TYPE.TOURNAMENT_COMP7, ARENA_BONUS_TYPE.TRAINING_COMP7):
            for key, infoCls in self._client_battleResultsReusables.iteritems():
                ReusableInfoFactory.addForBonusType(bonusType, key, infoCls)

    def registerAdditionalDynamicCache(self):
        from comp7_common.comp7_constants import ARENA_GUI_TYPE
        from gui.shared.system_factory import registerDynObjCache
        for guiType in (ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            registerDynObjCache(guiType, self._client_DynamicObjectCacheClass)

    def registerAdditionalGuiType(self):
        from gui.prb_control import prb_utils
        from comp7_common.comp7_constants import ARENA_GUI_TYPE
        from gui.Scaleform.daapi.settings.views import addViewBattlePageAliasByArenaGUIType
        for guiType in (ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            prb_utils.addArenaDescrs(guiType, self._client_arenaDescrClass, self._personality)
            addViewBattlePageAliasByArenaGUIType(guiType, self._CLIENT_BATTLE_PAGE, self._personality)

    def registerTrainingRoomHandler(self):
        from comp7_common.comp7_constants import ARENA_GUI_TYPE
        from comp7.gui.training_room_external_handlers import Comp7TrainingRoomHandler
        from gui.shared.system_factory import registerTrainingRoomExternalHandler
        for guiType in (ARENA_GUI_TYPE.COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            registerTrainingRoomExternalHandler(guiType, Comp7TrainingRoomHandler)


def preInit():
    injectConsts(__name__)
    injectSquadConsts(__name__)
    initGuiTypes(comp7_constants, __name__)
    initRequestType(comp7_constants, __name__)
    initBattleCtrlIDs(comp7_constants, __name__)
    comp7_constants.initComp7LimitedUIIds()
    battleMode = ClientComp7BattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerAdditionalGuiType()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerProviderBattleQueue()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerClientReplay()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerAdditionalBattleResultSysMsgType()
    battleMode.registerBattleResultsConfig()
    battleMode.registerAdditionalBattleResultsConfig()
    battleMode.registerClientBattleResultsCtrl()
    battleMode.registerAdditionalBattleResultsCtrl()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerAdditionalBattleResultReusabled()
    battleMode.registerGameControllers()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerAdditionalScaleformRequiredLibraries()
    battleMode.registerBattleControllersRepository()
    battleMode.registerAdditionalBattleRepository()
    battleMode.registerDynamicObjectCache()
    battleMode.registerAdditionalDynamicCache()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerAmmunitionPanelViews()
    battleMode.registerLobbyContextMenuOptions()
    battleMode.registerClientSeasonType(comp7_common_constants)
    battleMode.registerTrainingRoomHandler()
    battleMode.registerPrbTypeForWotPlusAssistant(SupportedWotldaLoadoutType.ONSLAUGHT)
    registerComp7Scaleform()
    registerComp7OthersPrbParams()
    registerComp7Lobby()
    registerComp7Battle()


def init():
    from comp7_common.comp7_constants import ARENA_GUI_TYPE
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, _LOBBY_EXT_PACKAGES)
    for guiType in (ARENA_GUI_TYPE.COMP7, ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
        g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, _BATTLE_EXT_PACKAGES, guiType)


def start():
    pass


def fini():
    pass
