# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode_personality.py
from AvatarInputHandler import OVERWRITE_CTRLS_DESC_MAP
from aih_constants import CTRL_TYPE, CTRL_MODE_NAME
from chat_shared import SYS_MESSAGE_TYPE
from constants import HAS_DEV_RESOURCES, ARENA_GUI_TYPE, ARENA_BONUS_TYPE
from debug_utils import LOG_DEBUG
from gui.battle_hints import battle_hints_overlap_controller
from gui.battle_hints.battle_hints_overlap_controller import HintScope
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initGuiTypes, initScaleformGuiTypes
from gui.shared.system_factory import registerScaleformBattlePackages
from schema_manager import getSchemaManager
from story_mode import account_settings
from story_mode.control_modes import OnboardingArcadeControlMode, OnboardingSniperControlMode, StoryModeArcadeControlMode, StoryModeSniperControlMode
from story_mode.gui import story_mode_gui_constants
from story_mode.gui.app_loader import observers
from story_mode.gui.battle_control.controllers import equipments_items
from story_mode.gui.battle_control.controllers.repository import OnboardingRepository, StoryModeRepository, StoryModeSharedRepository
from story_mode.gui.game_control.story_mode_controller import entryPointValidator
from story_mode.gui.game_control.story_mode_fading_controller import StoryModeFadingController
from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_fading_controller import IStoryModeFadingController
from story_mode_common import story_mode_constants, battle_mode, injectConsts
from story_mode_common.configs.story_mode_battle_mgr_quotums import quotumsSchema
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.configs.story_mode_settings import settingsSchema

class ClientStoryModeBattleMode(battle_mode.StoryModeBattleMode):
    _CLIENT_BATTLE_PAGE = story_mode_gui_constants.VIEW_ALIAS.STORY_MODE_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = story_mode_gui_constants.PREBATTLE_ACTION_NAME.STORY_MODE
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = VIEW_ALIAS.STORY_MODE_ENTRY_POINT

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        return entryPointValidator

    @property
    def _client_prbEntityClass(self):
        from story_mode.gui.prb_control.entities.pre_queue.entity import StoryModeEntity
        return StoryModeEntity

    @property
    def _client_prbEntryPointClass(self):
        from story_mode.gui.prb_control.entities.pre_queue.entity import StoryModeEntryPoint
        return StoryModeEntryPoint

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_3, 40)

    @property
    def _client_selectorItemsCreator(self):
        from story_mode.gui.scaleform.daapi.view.lobby.header.battle_selector_items import addStoryModeType
        return addStoryModeType

    @property
    def _client_modeSelectorItemsClass(self):
        from story_mode.gui.impl.lobby.mode_selector.story_mode_selector_item import StoryModeSelectorItem
        return StoryModeSelectorItem

    @property
    def _client_battleRequiredLibraries(self):
        return ['story_mode|story_mode_battle.swf', 'story_mode|storyModeComponents.swf']

    @property
    def _client_lobbyRequiredLibraries(self):
        return ['story_mode|story_mode_lobby.swf']

    @property
    def _client_gameControllers(self):
        from story_mode.skeletons.story_mode_controller import IStoryModeController
        from story_mode.gui.game_control.story_mode_controller import StoryModeController
        from story_mode.gui.game_control.voiceover_manager import VoiceoverManager
        from story_mode.skeletons.voiceover_controller import IVoiceoverManager
        return ((IStoryModeController, StoryModeController, False), (IVoiceoverManager, VoiceoverManager, False), (IStoryModeFadingController, StoryModeFadingController, False))

    @property
    def _client_arenaDescrClass(self):
        from story_mode.gui.battle_control.arena_descr import ArenaDescription
        return ArenaDescription

    @property
    def _client_battleResultsComposerClass(self):
        from story_mode.gui.battle_results.composer import StoryModeStatsComposer
        return StoryModeStatsComposer

    @property
    def _client_messengerServerFormatters(self):
        from story_mode.gui.messenger.formatters.service_channel import StoryModeResultsFormatter
        from story_mode.gui.messenger.formatters.service_channel import StoryModeAwardFormatter
        return {SYS_MESSAGE_TYPE.storyModeBattleResults.index(): StoryModeResultsFormatter(),
         SYS_MESSAGE_TYPE.lookup(story_mode_constants.SM_CONGRATULATIONS_MESSAGE).index(): StoryModeAwardFormatter()}

    @property
    def _client_battleControllersRepository(self):
        return StoryModeRepository

    @property
    def _client_sharedControllersRepository(self):
        return StoryModeSharedRepository

    @property
    def _client_DynamicObjectCacheClass(self):
        from story_mode.dyn_objects import StoryModeDynObjects
        return StoryModeDynObjects


class ClientOnboardingBattleMode(ClientStoryModeBattleMode):
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.STORY_MODE_ONBOARDING
    _CLIENT_BATTLE_PAGE = story_mode_gui_constants.VIEW_ALIAS.ONBOARDING_BATTLE_PAGE

    @property
    def _client_battleControllersRepository(self):
        return OnboardingRepository

    @property
    def _client_lobbyRequiredLibraries(self):
        return []


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    schemaManager = getSchemaManager()
    schemaManager.registerClientServerSchema(settingsSchema)
    schemaManager.registerClientServerSchema(quotumsSchema)
    schemaManager.registerClientServerSchema(missionsSchema)
    injectConsts(__name__)
    initGuiTypes(story_mode_gui_constants, __name__)
    initScaleformGuiTypes(story_mode_gui_constants, __name__)
    OVERWRITE_CTRLS_DESC_MAP[ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING] = {CTRL_MODE_NAME.ARCADE: (OnboardingArcadeControlMode, 'arcadeMode', CTRL_TYPE.USUAL),
     CTRL_MODE_NAME.SNIPER: (OnboardingSniperControlMode, 'sniperMode', CTRL_TYPE.USUAL)}
    OVERWRITE_CTRLS_DESC_MAP[ARENA_BONUS_TYPE.STORY_MODE_REGULAR] = {CTRL_MODE_NAME.ARCADE: (StoryModeArcadeControlMode, 'arcadeMode', CTRL_TYPE.USUAL),
     CTRL_MODE_NAME.SNIPER: (StoryModeSniperControlMode, 'sniperMode', CTRL_TYPE.USUAL)}
    battle_hints_overlap_controller.addSettings(ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING, HintScope.STORY_MODE.value, {STORY_MODE_BATTLE_VIEW_ALIASES.STORY_MODE_TIMER})
    equipments_items.register()
    battleMode = ClientStoryModeBattleMode(__name__)
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerGameControllers()
    battleMode.registerDynamicObjectCache()
    battleMode.registerBattleResultsConfig()
    battleMode.registerClientBattleResultsComposer()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerBattleResultSysMsgType()
    battleMode.registerMessengerServerFormatters()
    battleMode.registerBattleControllersRepository()
    battleMode.registerSharedControllersRepository()
    battleMode.registerBannerEntryPointValidatorMethod()
    onboardingBattleMode = ClientOnboardingBattleMode(__name__)
    onboardingBattleMode.registerGuiType()
    onboardingBattleMode.registerScaleformRequiredLibraries()
    onboardingBattleMode.registerBattleResultsConfig()
    onboardingBattleMode.registerClientBattleResultsComposer()
    onboardingBattleMode.registerBattleResultSysMsgType()
    onboardingBattleMode.registerBattleControllersRepository()
    observers.preInit()


def init():
    LOG_DEBUG('init', __name__)
    account_settings.init()
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['story_mode.gui.scaleform.daapi.view.lobby'])
    registerScaleformBattlePackages(story_mode_constants.ARENA_GUI_TYPE.STORY_MODE_ONBOARDING, ('story_mode.gui.scaleform.daapi.view.battle',))
    registerScaleformBattlePackages(story_mode_constants.ARENA_GUI_TYPE.STORY_MODE_REGULAR, ('story_mode.gui.scaleform.daapi.view.battle',))
    if HAS_DEV_RESOURCES:
        from story_mode.gui.development import prb_dev
        prb_dev.prbDevInit()


def start():
    pass


def fini():
    if HAS_DEV_RESOURCES:
        from story_mode.gui.development import prb_dev
        prb_dev.prbDevFini()
