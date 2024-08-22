# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/FunRandomPersonality.py
from fun_random.gui.battle_control import registerFunRandomBattle
from fun_random.gui.game_control import registerFunRandomAwardControllers
from fun_random.gui.prb_control import registerFunRandomOthersPrbParams
from fun_random.gui.Scaleform import registerFunRandomScaleform
from fun_random.gui.server_events import registerFunRandomQuests
from fun_random.gui.fun_gui_constants import initFunRandomLimitedUIIds, PREBATTLE_ACTION_NAME
from fun_random.gui import fun_gui_constants
from fun_random_common import injectConsts, injectSquadConsts
from fun_random_common.fun_battle_mode import FunRandomBattleMode
from gui.prb_control.prb_utils import initGuiTypes, initRequestType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES

class ClientFunRandomBattleMode(FunRandomBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.CLASSIC_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.FUN_RANDOM
    _CLIENT_PRB_ACTION_NAME_SQUAD = PREBATTLE_ACTION_NAME.FUN_RANDOM_SQUAD
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = FUNRANDOM_ALIASES.FUN_RANDOM_ENTRY_POINT
    _CLIENT_REPLAY_MODE_TAG = 'Arcade'

    @property
    def _client_prbEntityClass(self):
        from fun_random.gui.prb_control.entities.pre_queue.entity import FunRandomEntity
        return FunRandomEntity

    @property
    def _client_canSelectPrbEntity(self):
        from fun_random.gui.feature.util.fun_helpers import canSelectFunRandomPrbEntity
        return canSelectFunRandomPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from fun_random.gui.prb_control.entities.pre_queue.entity import FunRandomEntryPoint
        return FunRandomEntryPoint

    @property
    def _client_gameControllers(self):
        from skeletons.gui.game_control import IFunRandomController
        from fun_random.gui.game_control.fun_random_controller import FunRandomController
        return ((IFunRandomController, FunRandomController, True),)

    @property
    def _client_battleControllersRepository(self):
        from fun_random.gui.battle_control.controllers.repository import FunRandomControllerRepository
        return FunRandomControllerRepository

    @property
    def _client_providerBattleQueue(self):
        from fun_random.gui.Scaleform.daapi.view.lobby.battle_queue import FunRandomQueueProvider
        return FunRandomQueueProvider

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 20)

    @property
    def _client_selectorItemsCreator(self):
        from fun_random.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addFunRandomBattleType
        return addFunRandomBattleType

    @property
    def _client_modeSelectorItemsClass(self):
        from fun_random.gui.impl.lobby.mode_selector.items.fun_random_mode_selector_item import FunRandomSelectorItem
        return FunRandomSelectorItem

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from fun_random.gui.impl.lobby.feature.fun_random_entry_point_view import isFunRandomEntryPointAvailable
        return isFunRandomEntryPointAvailable

    @property
    def _client_bannerEntryPointLUIRule(self):
        from gui.limited_ui.lui_rules_storage import LUI_RULES
        return LUI_RULES.FunRandomEntryPoint

    @property
    def _client_prbSquadEntityClass(self):
        from fun_random.gui.prb_control.entities.squad.entity import FunRandomSquadEntity
        return FunRandomSquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from fun_random.gui.prb_control.entities.squad.entity import FunRandomSquadEntryPoint
        return FunRandomSquadEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from fun_random.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addFunRandomSquadType
        return addFunRandomSquadType

    @property
    def _client_platoonViewClass(self):
        from fun_random.gui.impl.lobby.platoon.view.fun_platoon_members_view import FunRandomMembersView
        return FunRandomMembersView

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
    def _client_arenaDescrClass(self):
        from fun_random.gui.battle_control.arena_info.arena_descrs import FunRandomArenaDescription
        return FunRandomArenaDescription

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_notificationActionHandlers(self):
        from fun_random.notification.actions_handlers import SelectFunRandomMode, ShowFunRandomProgression
        return (SelectFunRandomMode, ShowFunRandomProgression)

    @property
    def _client_messengerClientFormatters(self):
        from fun_random.messenger.formatters.service_channel import FunRandomNotificationsFormatter
        from fun_random.messenger.formatters.token_quest_subformatters import FunProgressionRewardsSyncFormatter
        return {fun_gui_constants.SCH_CLIENT_MSG_TYPE.FUN_RANDOM_NOTIFICATIONS: FunRandomNotificationsFormatter(),
         fun_gui_constants.SCH_CLIENT_MSG_TYPE.FUN_RANDOM_PROGRESSION: FunProgressionRewardsSyncFormatter()}

    @property
    def _client_tokenQuestsSubFormatters(self):
        from fun_random.messenger.formatters.token_quest_subformatters import FunProgressionRewardsAsyncFormatter, FunModeItemsQuestAsyncFormatter
        return (FunProgressionRewardsAsyncFormatter(), FunModeItemsQuestAsyncFormatter())

    @property
    def _client_lootBoxAutoOpenSubFormatters(self):
        from fun_random.messenger.formatters.loot_box_auto_open_subformatters import FunRandomLootboxAutoOpenFormatter
        return [FunRandomLootboxAutoOpenFormatter()]

    @property
    def _client_vehicleViewStates(self):
        from fun_random.gui.vehicle_view_states import FunRandomVehicleViewState
        return (FunRandomVehicleViewState,)

    @property
    def _client_hangarPresetsReader(self):
        from fun_random.gui.hangar_presets.fun_hangar_presets_reader import FunRandomPresetsReader
        return FunRandomPresetsReader

    @property
    def _client_hangarPresetsGetter(self):
        from fun_random.gui.hangar_presets.fun_hangar_presets_getter import FunRandomPresetsGetter
        return FunRandomPresetsGetter


def preInit():
    injectConsts(__name__)
    injectSquadConsts(__name__)
    initGuiTypes(fun_gui_constants, __name__)
    initRequestType(fun_gui_constants, __name__)
    initFunRandomLimitedUIIds()
    battleMode = ClientFunRandomBattleMode(__name__)
    battleMode.registerCommon()
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerClientHangarPresets()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerProviderBattleQueue()
    battleMode.registerBattleResultsConfig()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerClientReplay()
    battleMode.registerGameControllers()
    battleMode.registerBattleControllersRepository()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(fun_gui_constants)
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerClientLootBoxAutoOpenSubFormatters()
    battleMode.registerVehicleViewStates()
    registerFunRandomOthersPrbParams()
    registerFunRandomAwardControllers()
    registerFunRandomScaleform()
    registerFunRandomBattle()
    registerFunRandomQuests()


def init():
    pass


def start():
    pass


def fini():
    pass
