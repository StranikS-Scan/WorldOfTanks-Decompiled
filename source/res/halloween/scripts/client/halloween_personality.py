# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween_personality.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, QUEUE_TYPE
from debug_utils import LOG_DEBUG
from halloween.messenger.formatters.collections_by_type import addHW22ClientFormatters
from halloween.notification.actions_handler import addHW22ActionHandlers
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.backports.context_menu import TANK_SETUP_CARD_CM, TANK_SETUP_SLOT_CM, HANGAR_TANK_SETUP_SLOT_CM
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from halloween.gui.battle_control.controllers.hw_equipment_ctrl import registerHWEquipmentCtrls
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_entry_point import addHW22EntryPoint, canSelectPrbEntityFun
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.shared.system_factory import registerGameControllers, registerStatsComposerByArenaBonusType, registerCanSelectPrbEntity
from halloween.hw_constants import ACCOUNT_DEFAULT_SETTINGS
from halloween.gui.shared.tooltips.hw_advanced import registerHWEquipmentTooltipMovies
from gui.shared.system_factory import registerLobbyTooltipsBuilders
from halloween.hw_constants import HWTooltips
from gui.game_control.AwardController import AWARD_HANDLERS
from halloween.gui.game_control.award_handlers import HWBattleQuestsRewardHandler, HWInvoiceCrewBonusHandler
LOBBY_EXT_PACKAGES = ('halloween.gui.Scaleform.daapi.view.lobby', 'halloween.gui.Scaleform.daapi.view.lobby.hangar', 'halloween.gui.Scaleform.daapi.view.lobby.tank_setup')
BATTLE_EXT_PACKAGES = ('halloween.gui.Scaleform.daapi.view.battle',)
TOOLTIP_PACKAGES = [('halloween.gui.Scaleform.daapi.view.tooltips.halloween_lobby_builders', HWTooltips.HW_LOBBY_SET)]
ARENA_GUI_TYPES = (ARENA_GUI_TYPE.EVENT_BATTLES,)
HW_AWARD_HANDLERS = [HWBattleQuestsRewardHandler, HWInvoiceCrewBonusHandler]

def preInit():
    registerHWEquipmentCtrls()
    registerHWEquipmentTooltipMovies()
    registerLobbyTooltipsBuilders(TOOLTIP_PACKAGES)
    from halloween.gui.game_control.halloween_progress_controller import HalloweenProgressController
    from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
    from halloween.gui.game_control.visibility_layer_controller import VisibilityLayerController
    from halloween.skeletons.gui.visibility_layer_controller import IHalloweenVisibilityLayerController
    from halloween.gui.sounds.sound_controller import HWSoundController
    from halloween.skeletons.gui.sound_controller import IHWSoundController
    registerGameControllers([(IHalloweenProgressController, HalloweenProgressController, False), (IHalloweenVisibilityLayerController, VisibilityLayerController, False), (IHWSoundController, HWSoundController, False)])
    from halloween.gui.battle_results.composer import HalloweenBattleStatsComposer
    registerStatsComposerByArenaBonusType(ARENA_BONUS_TYPE.EVENT_BATTLES, HalloweenBattleStatsComposer)
    registerStatsComposerByArenaBonusType(ARENA_BONUS_TYPE.EVENT_BATTLES_2, HalloweenBattleStatsComposer)
    registerCanSelectPrbEntity(QUEUE_TYPE.EVENT_BATTLES, canSelectPrbEntityFun)
    registerCanSelectPrbEntity(QUEUE_TYPE.EVENT_BATTLES_2, canSelectPrbEntityFun)
    TANK_SETUP_CARD_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HW_CONSUMABLE_ITEM})
    TANK_SETUP_SLOT_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HW_CONSUMABLE_SLOT})
    HANGAR_TANK_SETUP_SLOT_CM.update({TankSetupConstants.HWCONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_HW_CONSUMABLE_SLOT})
    from gui.shared.gui_items.marker_items import MarkerParamsFactory
    from halloween.gui.Scaleform.daapi.view.battle.entity_markers import HW_MARKERS
    for markerStyle, markerParams in HW_MARKERS.items():
        MarkerParamsFactory.registerMarker(markerStyle, markerParams)

    AWARD_HANDLERS.extend(HW_AWARD_HANDLERS)


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionGUIPackages(__name__, LOBBY_EXT_PACKAGES, BATTLE_EXT_PACKAGES, ARENA_GUI_TYPES)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    addHW22EntryPoint()
    addHW22ActionHandlers()
    addHW22ClientFormatters()


def start():
    pass


def fini():
    pass
