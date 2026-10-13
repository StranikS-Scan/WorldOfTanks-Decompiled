# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/register_additional_params.py
from __future__ import absolute_import
from gui.battle_hints import battle_hints_overlap_controller
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG, HWDailyQuestDecorationMap
from halloween.gui.shared.utils import checkAbilities
from helpers import dependency
from gui.prb_control.prb_utils import addSupportedQueues, addArenaGUITypeByQueueType, addQueueTypeToPrbType
from gui.prb_control.settings import PREBATTLE_TYPE_TO_QUEUE_TYPE
from halloween.messenger.formatters.invites import HalloweenPrbInviteHtmlTextFormatter
from halloween.gui import halloween_gui_constants
from halloween.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity, HalloweenEntity
from halloween_common.halloween_constants import QUEUE_TYPE, ARENA_GUI_TYPE, PREBATTLE_TYPE, ARENA_BONUS_TYPE
from gui.impl.lobby.platoon.platoon_config import addQueueTypeToPrbSquadActionName
from gui.impl.lobby.tank_setup.backports.context_menu import TANK_SETUP_CARD_CM, TANK_SETUP_SLOT_CM, HANGAR_TANK_SETUP_SLOT_CM
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VEHICLE_PREVIEW_ALIASES
from halloween.gui.scaleform.genConsts.HALLOWEEN_CM_HANDLER_TYPE import HALLOWEEN_CM_HANDLER_TYPE
from halloween.gui.scaleform.genConsts.HALLOWEEN_HANGAR_ALIASES import HALLOWEEN_HANGAR_ALIASES
from gui.impl.lobby.tank_setup.backports.tooltips import PANEL_SLOT_TOOLTIPS
from halloween.gui.impl.lobby.tank_setup.backports.tooltips import HWConsumableTooltipBuilder
from gui.shared.gui_items.items_actions.factory import _ACTION_MAP
from halloween.gui.shared.gui_items.items_actions import actions
from halloween.gui.impl.lobby.tank_setup.interactor import BUY_AND_INSTALL_HW_CONSUMABLES_ACTION
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import _SECTION_TO_FITTING_TYPE
from halloween.gui.impl.lobby.tank_setup import HWTankSetupConstants, HWFittingTypes
from gui.shared.system_factory import registerHitDirectionController, registerPrbInviteHtmlFormatter, registerIgnoredModeForAutoSelectVehicle, registerReadyVehicleChekers
from halloween.gui.battle_control.controllers.hit_direction_ctrl.hw_ctrl import HWHitDirectionController, HWHitDirectionControllerPlayer
from messenger.m_constants import LAZY_CHANNEL
from messenger.ext.channel_num_gen import _CHANNEL_LAZY_ORDER, _LAZY_CLIENT_IDS
from soft_exception import SoftException
from web.web_client_api.ui import OpenTabWebApi
from halloween.skeletons.halloween_controller import IHalloweenController

def _registerHWOpenTabWebApi():

    @dependency.replace_none_kwargs(ctrl=IHalloweenController)
    def _selectHalloweenMode(obj, cmd, ctrl=None):
        if ctrl and ctrl.isAvailable():
            ctrl.openHangar()

    OpenTabWebApi.addTabIdCallback('halloween2023', _selectHalloweenMode)
    return


def registerAdditionalParams(personality):
    for queueType in (QUEUE_TYPE.HALLOWEEN_MEDIUM, QUEUE_TYPE.HALLOWEEN_HARD):
        addSupportedQueues(queueType, HalloweenEntity, canSelectPrbEntity, personality)
        addQueueTypeToPrbSquadActionName(queueType, halloween_gui_constants.PREBATTLE_ACTION_NAME.HALLOWEEN_SQUAD, personality)
        addArenaGUITypeByQueueType(queueType, ARENA_GUI_TYPE.HALLOWEEN, personality)
        addQueueTypeToPrbType(queueType, PREBATTLE_TYPE.HALLOWEEN, personality)
        PREBATTLE_TYPE_TO_QUEUE_TYPE[PREBATTLE_TYPE.HALLOWEEN].append(queueType)
        registerReadyVehicleChekers(queueType, [checkAbilities])

    TANK_SETUP_CARD_CM.update({HWTankSetupConstants.HW_CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_ITEM})
    TANK_SETUP_SLOT_CM.update({HWTankSetupConstants.HW_CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_SLOT})
    HANGAR_TANK_SETUP_SLOT_CM.update({HWTankSetupConstants.HW_CONSUMABLES: HALLOWEEN_CM_HANDLER_TYPE.TANK_SETUP_HW_HANGAR_CONSUMABLE_SLOT})
    PANEL_SLOT_TOOLTIPS.update({HWTankSetupConstants.HW_CONSUMABLES: HWConsumableTooltipBuilder})
    _ACTION_MAP.update({BUY_AND_INSTALL_HW_CONSUMABLES_ACTION: actions.HWBuyAndInstallConsumables})
    _SECTION_TO_FITTING_TYPE.update({HWTankSetupConstants.HW_CONSUMABLES: HWFittingTypes.HW_EQUIPMENT})
    registerHitDirectionController(ARENA_GUI_TYPE.HALLOWEEN, HWHitDirectionController, HWHitDirectionControllerPlayer)
    registerPrbInviteHtmlFormatter(PREBATTLE_TYPE.HALLOWEEN, HalloweenPrbInviteHtmlTextFormatter)
    _registerHWOpenTabWebApi()
    VEHICLE_PREVIEW_ALIASES.update((HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_VEHICLE_PREVIEW, HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_HERO_PREVIEW))
    registerIgnoredModeForAutoSelectVehicle([FUNCTIONAL_FLAG.HALLOWEEN])
    for bonusType in (ARENA_BONUS_TYPE.HALLOWEEN, ARENA_BONUS_TYPE.HALLOWEEN_MEDIUM, ARENA_BONUS_TYPE.HALLOWEEN_HARD):
        battle_hints_overlap_controller.addSettings(bonusType, halloween_gui_constants.HALLOWEEN_BATTLE_HINTS_SCOPE, halloween_gui_constants.HALLOWEEN_BATTLE_HINTS_OVERLAP_VIEWS)

    registerConditionFormatterIcons()
    registerDailyQuestDecorationMap(personality)


def registerLazyChannelParam(extChannelConst, personality):
    extraAttrs = extChannelConst.getExtraAttrs()
    extChannelConst.inject(personality)
    for value in extraAttrs.values():
        LAZY_CHANNEL.ALL += (value,)
        _CHANNEL_LAZY_ORDER.update({value: 1})

    _LAZY_CLIENT_IDS.update(dict(((name, -(idx + 1 + 32)) for idx, name in enumerate(LAZY_CHANNEL.ALL))))


def initAdditionalGuiTypes(guiConstants, personality):
    registerLazyChannelParam(guiConstants.LAZY_CHANNEL, personality)


def registerConditionFormatterIcons():
    from gui.server_events.cond_formatters import BATTLE_RESULTS_KEYS
    BATTLE_RESULTS_KEYS.update({'hwUnveiledAnomaliesCount': 'anomalies'})


def registerDailyQuestDecorationMap(personality):
    from constants import DailyQuestDecorationMap
    commonKeys = set(DailyQuestDecorationMap) & set(HWDailyQuestDecorationMap)
    if commonKeys:
        raise SoftException('DailyQuestDecorationMap already has keys:{keys}. Personality: {personality}'.format(keys=commonKeys, personality=personality))
    DailyQuestDecorationMap.update(HWDailyQuestDecorationMap)
