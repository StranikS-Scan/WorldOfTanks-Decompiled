# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WhiteTigerPersonality.py
import logging
from constants_utils import initCommonTypes, addRosterTypes, addInvitationTypes
from gui.prb_control.prb_utils import initGuiTypes
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.prb_control.storages import makeQueueName
from gui.shared.system_factory import registerDynObjCache, registerPrbStorage, registerIngameHelpPagesBuilders
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from white_tiger.gui.ingame_help.white_tiger_pages_builder import WhiteTigerHelpPagesBuilder
from white_tiger_common import wt_constants
from white_tiger.gui import gui_constants
from wt_dyn_objects_cache import WTBattleDynObjects
from white_tiger.gui.hangar_presets import registerWhiteTigerHangarPresets
from white_tiger.gui.battle_control.controllers.consumables.equipment_items import registerTagsToEventItemMapping
from white_tiger.gui.prb_control.storages.white_tiger_battles_storage import WhiteTigerBattlesStorage
from white_tiger.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addWhiteTigerBattleSquadsType
from white_tiger.gui.Scaleform import registerWhiteTigerTooltipsBuilders
from gui.shared.system_factory import registerAwardControllerHandler
from white_tiger.gui.game_control.wt_award_controller import WtEventQuestAwardHandler, WtPunishWindowHandler
from gui.shared.system_factory import registerBattleResultsComposer
from white_tiger.gui.battle_results.composer import WhiteTigerBattleStatsComposer
from gui.battle_control.arena_info.arena_vos import GAMEMODE_SPECIFIC_KEYS, EventKeys
from gui.shared.system_factory import registerHangarPresetGetter
from white_tiger_common.wt_constants import QUEUE_TYPE
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter
_logger = logging.getLogger(__name__)

class WtEventPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.WHITE_TIGER


class ClientWhiteTigerBattleMode(wt_constants.WhiteTigerBattleMode):
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.EVENT_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = gui_constants.PREBATTLE_ACTION_NAME.WHITE_TIGER
    _CLIENT_PRB_ACTION_NAME_SQUAD = gui_constants.PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = HANGAR_ALIASES.WT_EVENT_ENTRY_POINT
    _CLIENT_GAME_SEASON_TYPE = wt_constants.GameSeasonType.WHITE_TIGER

    @property
    def _client_prbEntityClass(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import WhiteTigerBattleEntity
        return WhiteTigerBattleEntity

    @property
    def _client_canSelectPrbEntity(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity
        return canSelectPrbEntity

    @property
    def _client_prbEntryPointClass(self):
        from white_tiger.gui.prb_control.entities.pre_queue.entity import WhiteTigerEntryPoint
        return WhiteTigerEntryPoint

    @property
    def _client_bannerEntryPointLUIRule(self):
        return LuiRules.GUI_WHITE_TIGER_ENTRY_POINT

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_1, 5)

    @property
    def _client_selectorItemsCreator(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addWhiteTigerBattlesType
        return addWhiteTigerBattlesType

    @property
    def _client_modeSelectorItemsClass(self):
        from white_tiger.gui.impl.lobby.mode_selector.white_tiger_mode_selector_item import WhiteTigerModeSelectorItem
        return WhiteTigerModeSelectorItem

    @property
    def _client_battleRequiredLibraries(self):
        return ['white_tiger|white_tiger_battle.swf']

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['white_tiger|white_tiger_lobby.swf']

    @property
    def _client_providerBattleQueue(self):
        from white_tiger.gui.Scaleform.daapi.view.lobby.white_tiger_queue import WhiteTigerQueueProvider
        return WhiteTigerQueueProvider

    @property
    def _client_seasonControllerHandler(self):
        from white_tiger.gui.game_control.wt_controller import WhiteTigerController
        return WhiteTigerController

    @property
    def _client_gameControllers(self):
        from skeletons.gui.game_control import IWhiteTigerController
        from white_tiger.gui.game_control.wt_controller import WhiteTigerController
        from skeletons.gui.game_control import ILootBoxesController
        from white_tiger.gui.game_control.loot_boxes_controller import LootBoxesController
        return [(IWhiteTigerController, WhiteTigerController, False), (ILootBoxesController, LootBoxesController, False)]

    def registerSharedControllersRepository(self):
        from gui.battle_control.controllers.consumables import _EQUIPMENT_CONTROLLERS
        from white_tiger.gui.battle_control.controllers.consumables import equipment_ctrl
        _EQUIPMENT_CONTROLLERS.update({wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER: equipment_ctrl.WhiteTigerEquipmentController,
         wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER_2: equipment_ctrl.WhiteTigerEquipmentController})
        from gui.battle_control.controllers.consumables import _REPLAY_EQUIPMENT_CONTROLLERS
        _REPLAY_EQUIPMENT_CONTROLLERS.update({wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER: equipment_ctrl.WhiteTigerReplayConsumablesPanelMeta,
         wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER_2: equipment_ctrl.WhiteTigerReplayConsumablesPanelMeta})

    @property
    def _client_battleControllersRepository(self):
        from white_tiger.gui.battle_control.controllers.repository import WhiteTigerControllerRepository
        return WhiteTigerControllerRepository

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from white_tiger.gui.impl.lobby.entry_point import wt_banner_entry_point
        return wt_banner_entry_point.isWTBannerEntryPointAvailable

    @property
    def _client_messengerServerFormatters(self):
        from white_tiger.messenger.formatters.service_channel import WTBattleResultsFormatter
        from white_tiger.messenger.formatters.service_channel import WTEventTicketTokenWithdrawnFormatter
        from chat_shared import SYS_MESSAGE_TYPE
        return {SYS_MESSAGE_TYPE.whiteTigerBattleResults.index(): WTBattleResultsFormatter(),
         SYS_MESSAGE_TYPE.wtEventTicketTokenWithdrawn.index(): WTEventTicketTokenWithdrawnFormatter()}

    @property
    def _client_messengerClientFormatters(self):
        import white_tiger.messenger.formatters.service_channel as formatters
        return {gui_constants.SCH_CLIENT_MSG_TYPE.WT_EVENT_STATE: formatters.WTEventStateMessageFormatter()}

    @property
    def _client_notificationActionHandlers(self):
        import white_tiger.gui.notifications.action_handlers as handlers
        return (handlers.WTOpenPortalsHandler,
         handlers.WTOpenCollectionHandler,
         handlers.WTOpenHandler,
         handlers.WTOpenQuestsHandler,
         handlers.WTOpenTicketPurchasingHandler)

    @property
    def _client_platoonViewClass(self):
        from white_tiger.gui.impl.lobby.platoon.view.white_tiger_members_view import WhiteTigerMembersView
        return WhiteTigerMembersView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow))]

    @property
    def _client_platoonWelcomeViewClass(self):
        from white_tiger.gui.impl.lobby.wt_event_welcome import WTEventWelcomeView
        return WTEventWelcomeView

    @property
    def _client_prbSquadEntryPointClass(self):
        from white_tiger.gui.prb_control.entities.squad.entity import WhiteTigerBattleSquadEntryPoint
        return WhiteTigerBattleSquadEntryPoint

    @property
    def _client_prbSquadEntityClass(self):
        from white_tiger.gui.prb_control.entities.squad.entity import WhiteTigerBattleSquadEntity
        return WhiteTigerBattleSquadEntity

    @property
    def _client_selectorSquadItemsCreator(self):
        return addWhiteTigerBattleSquadsType

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    def registerOtherPrbParams(self):
        registerPrbStorage(makeQueueName(self._QUEUE_TYPE), WhiteTigerBattlesStorage())

    @property
    def _client_battleResultsComposerClass(self):
        return WhiteTigerBattleStatsComposer

    @property
    def _client_arenaDescrClass(self):
        from white_tiger.gui.battle_control.arena_info.arena_descrs import WhiteTigerArenaDescription
        return WhiteTigerArenaDescription

    def registerAdditionalSystemMessageTypes(self):
        from gui.SystemMessages import SM_TYPE
        SM_TYPE.inject(['WTLootBoxRewards'])


def preInit():
    _logger.debug('preInit personality: %r', __name__)
    initCommonTypes(wt_constants, __name__)
    wt_constants.UNIT_MGR_FLAGS.inject(__name__)
    addRosterTypes(wt_constants.ROSTER_TYPE, __name__)
    addInvitationTypes(wt_constants.INVITATION_TYPE, __name__)
    initGuiTypes(gui_constants, __name__)
    gui_constants.injectClientConstants(__name__)
    battleMode = ClientWhiteTigerBattleMode(__name__)
    battleMode.registerGameControllers()
    battleMode.registerClient()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerClientSelector()
    battleMode.registerProviderBattleQueue()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerClientBattleResultsComposer()
    registerBattleResultsComposer(wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER_2, WhiteTigerBattleStatsComposer)
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientSeasonType(wt_constants)
    battleMode.registerScaleformRequiredLibraries()
    arenaRanges = (wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER, wt_constants.ARENA_BONUS_TYPE.WHITE_TIGER_2)
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType(arenaRanges=arenaRanges)
    battleMode.registerMessengerServerFormatters()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerClientTokenQuestsSubFormatters()
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleControllersRepository()
    battleMode.registerBattleResultsConfig(arenaRanges)
    battleMode.registerSquadTypes()
    battleMode.registerOtherPrbParams()
    battleMode.registerAdditionalSystemMessageTypes()
    registerAwardControllerHandler(WtEventQuestAwardHandler)
    registerAwardControllerHandler(WtPunishWindowHandler)
    registerDynObjCache(wt_constants.ARENA_GUI_TYPE.WHITE_TIGER, WTBattleDynObjects)
    registerWhiteTigerHangarPresets()
    registerWhiteTigerTooltipsBuilders()
    registerTagsToEventItemMapping()
    from white_tiger.notification import registerClientNotificationHandlers
    registerClientNotificationHandlers()
    registerIngameHelpPagesBuilders((WhiteTigerHelpPagesBuilder,))
    GAMEMODE_SPECIFIC_KEYS.update({wt_constants.ARENA_GUI_TYPE.WHITE_TIGER: EventKeys})
    registerHangarPresetGetter(QUEUE_TYPE.WHITE_TIGER, WtEventPresetsGetter)


def init():
    _logger.debug('init: %r', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['white_tiger.gui.Scaleform.daapi.view.lobby'])
    g_overrideScaleFormViewsConfig.initExtensionBattlePackages(__name__, ['white_tiger.gui.Scaleform.daapi.view.battle.white_tiger'], wt_constants.ARENA_GUI_TYPE.WHITE_TIGER)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, wt_constants.ACCOUNT_DEFAULT_SETTINGS)


def start():
    pass


def fini():
    pass
