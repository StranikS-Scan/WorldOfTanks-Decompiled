# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline_personality.py
from frontline_common.constants import ACCOUNT_DEFAULT_SETTINGS
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from constants import ARENA_GUI_TYPE, PREBATTLE_TYPE, QUEUE_TYPE, ARENA_BONUS_TYPE, HAS_DEV_RESOURCES
from constants_utils import AbstractBattleMode
from frontline.gui import gui_constants
from frontline.gui.Scaleform import registerFLBattlePackages, registerFLTooltipsBuilders
from frontline.gui.battle_control.controllers.consumables import registerFLEquipmentController
from frontline.gui.battle_control.controllers.equipment_items import registerFLEquipmentsItems
from frontline.gui.battle_control.controllers.repositories import registerFLBattleRepositories
from frontline.gui.prb_control import registerFLPrebattles, extendIntroByType
from frontline.gui.frontline_gui_constants import initFLLimitedUIIDs
from frontline.gui.Scaleform.daapi.view.lobby.hangar.hangar_quest_flags import registerQuestFlags
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.prb_utils import initHangarGuiConsts
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
LOBBY_EXT_PACKAGES = ['frontline.gui.Scaleform.daapi.view.lobby', 'frontline.gui.Scaleform.daapi.view.lobby.hangar', 'frontline.gui.Scaleform.daapi.view.lobby.epicBattleTraining']

class ClientFrontlineBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.EPIC
    _QUEUE_TYPE = QUEUE_TYPE.EPIC
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.EPIC_BATTLE
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.EPIC_BATTLE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.EPIC
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = EPICBATTLES_ALIASES.EPIC_BATTLES_ENTRY_POINT

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from frontline.gui.Scaleform.daapi.view.lobby.hangar.entry_point import isEpicBattlesEntryPointAvailable
        return isEpicBattlesEntryPointAvailable

    @property
    def _client_bannerEntryPointLUIRule(self):
        from gui.limited_ui.lui_rules_storage import LUI_RULES
        return LUI_RULES.EpicBattlesEntryPoint

    @property
    def _client_providerBattleQueue(self):
        from frontline.gui.Scaleform.daapi.view.lobby.battle_queue_provider import EpicQueueProvider
        return EpicQueueProvider

    @property
    def _client_ammunitionPanelViews(self):
        from gui.impl.lobby.tank_setup.frontline.ammunition_panel import FrontlineAmmunitionPanelView
        return [FrontlineAmmunitionPanelView]

    @property
    def _client_hangarPresetsReader(self):
        from frontline.gui.hangar_presets.frontline_presets_reader import FrontlinePresetsReader
        return FrontlinePresetsReader

    @property
    def _client_hangarPresetsGetter(self):
        from frontline.gui.hangar_presets.frontline_presets_getter import FrontlinePresetsGetter
        return FrontlinePresetsGetter


def preInit():
    initFLLimitedUIIDs()
    initHangarGuiConsts(gui_constants, __name__)
    battleMode = ClientFrontlineBattleMode(__name__)
    battleMode.registerClientHangarPresets()
    battleMode.registerBannerEntryPointValidatorMethod()
    battleMode.registerBannerEntryPointLUIRule()
    battleMode.registerAmmunitionPanelViews()
    battleMode.registerProviderBattleQueue()
    registerFLBattlePackages()
    registerFLBattleRepositories()
    registerFLTooltipsBuilders()
    registerQuestFlags()
    extendIntroByType()
    registerFLEquipmentController()
    registerFLEquipmentsItems()
    registerFLPrebattles()


def init():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, LOBBY_EXT_PACKAGES)
    if HAS_DEV_RESOURCES:
        from frontline.gui.development import prb_dev
        prb_dev.prbDevInit()


def start():
    pass


def fini():
    if HAS_DEV_RESOURCES:
        from frontline.gui.development import prb_dev
        prb_dev.prbDevFini()
