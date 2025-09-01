# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/register_additional_params.py
from helpers import dependency
from gui.prb_control.prb_utils import addSupportedQueues, addArenaGUITypeByQueueType, addQueueTypeToPrbType
from gui.prb_control.settings import PREBATTLE_TYPE_TO_QUEUE_TYPE
from last_stand.messenger.formatters.invites import LSPrbInviteHtmlTextFormatter
from last_stand.gui.prb_control.entities.pre_queue.entity import canSelectPrbEntity, LastStandEntity
from last_stand_common.last_stand_constants import QUEUE_TYPE, ARENA_GUI_TYPE, PREBATTLE_TYPE
from gui.impl.lobby.platoon.platoon_config import addQueueTypeToPrbSquadActionName
from gui.impl.lobby.tank_setup.backports.context_menu import TANK_SETUP_CARD_CM, TANK_SETUP_SLOT_CM, HANGAR_TANK_SETUP_SLOT_CM
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from last_stand.gui.scaleform.genConsts.LS_CM_HANDLER_TYPE import LS_CM_HANDLER_TYPE
from gui.impl.lobby.tank_setup.backports.tooltips import PANEL_SLOT_TOOLTIPS
from last_stand.gui.impl.lobby.tank_setup.backports.tooltips import LSConsumableTooltipBuilder
from gui.shared.gui_items.items_actions.factory import _ACTION_MAP
from last_stand.gui.shared.gui_items.items_actions import actions
from last_stand.gui.impl.lobby.tank_setup.interactor import ActionTypes
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import _SECTION_TO_FITTING_TYPE
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants, LSFittingTypes
from gui.shared.system_factory import registerHitDirectionController, registerPrbInviteHtmlFormatter, registerLobbyTooltipsBuilders, registerIgnoredModeForAutoSelectVehicle
from last_stand.gui.battle_control.controllers.hit_direction_ctrl.ls_ctrl import LSHitDirectionController, LSHitDirectionControllerPlayer
from gui.shared.system_factory import registerAwardControllerHandlers
from messenger.m_constants import LAZY_CHANNEL
from messenger.ext.channel_num_gen import _CHANNEL_LAZY_ORDER, _LAZY_CLIENT_IDS
from web.web_client_api.ui import OpenTabWebApi
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.ls_gui_constants import LS_TOOLTIP_SET, PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG

def _registerLSOpenTabWebApi():

    @dependency.replace_none_kwargs(ctrl=ILSController)
    def _selectLSMode(obj, cmd, ctrl=None):
        if ctrl and ctrl.isAvailable():
            ctrl.openHangar()

    OpenTabWebApi.addTabIdCallback('last_stand', _selectLSMode)
    return


def registerAdditionalParams(personality):
    for queueType in (QUEUE_TYPE.LAST_STAND_MEDIUM, QUEUE_TYPE.LAST_STAND_HARD):
        addSupportedQueues(queueType, LastStandEntity, canSelectPrbEntity, personality)
        addQueueTypeToPrbSquadActionName(queueType, PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD, personality)
        addArenaGUITypeByQueueType(queueType, ARENA_GUI_TYPE.LAST_STAND, personality)
        addQueueTypeToPrbType(queueType, PREBATTLE_TYPE.LAST_STAND, personality)
        PREBATTLE_TYPE_TO_QUEUE_TYPE[PREBATTLE_TYPE.LAST_STAND].append(queueType)

    TANK_SETUP_CARD_CM.update({LSTankSetupConstants.LS_CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_ITEM})
    TANK_SETUP_SLOT_CM.update({LSTankSetupConstants.LS_CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_SLOT})
    HANGAR_TANK_SETUP_SLOT_CM.update({LSTankSetupConstants.LS_CONSUMABLES: LS_CM_HANDLER_TYPE.TANK_SETUP_LS_HANGAR_CONSUMABLE_SLOT})
    PANEL_SLOT_TOOLTIPS.update({LSTankSetupConstants.LS_CONSUMABLES: LSConsumableTooltipBuilder})
    _ACTION_MAP.update({ActionTypes.BUY_AND_INSTALL_LS_CONSUMABLES_ACTION: actions.LSBuyAndInstallConsumables})
    _SECTION_TO_FITTING_TYPE.update({LSTankSetupConstants.LS_CONSUMABLES: LSFittingTypes.LS_EQUIPMENT})
    registerHitDirectionController(ARENA_GUI_TYPE.LAST_STAND, LSHitDirectionController, LSHitDirectionControllerPlayer)
    from last_stand.gui.game_control.award_handlers import LSArtefactAwardWindowHandler, LSCustomizationRewardHandler, LSDifficultyAwardWindowHandler
    registerAwardControllerHandlers((LSArtefactAwardWindowHandler, LSDifficultyAwardWindowHandler, LSCustomizationRewardHandler))
    registerPrbInviteHtmlFormatter(PREBATTLE_TYPE.LAST_STAND, LSPrbInviteHtmlTextFormatter)
    _registerLSOpenTabWebApi()
    registerLobbyTooltipsBuilders([('last_stand.gui.scaleform.daapi.view.tooltips.tooltip_builders', LS_TOOLTIP_SET)])
    registerIgnoredModeForAutoSelectVehicle([FUNCTIONAL_FLAG.LAST_STAND])


def registerLazyChannelParam(extChannelConst, personality):
    extraAttrs = extChannelConst.getExtraAttrs()
    extChannelConst.inject(personality)
    for value in extraAttrs.itervalues():
        LAZY_CHANNEL.ALL += (value,)
        _CHANNEL_LAZY_ORDER.update({value: 1})

    _LAZY_CLIENT_IDS.update(dict(((name, -(idx + 1 + 32)) for idx, name in enumerate(LAZY_CHANNEL.ALL))))


def initAdditionalGuiTypes(guiConstants, personality):
    registerLazyChannelParam(guiConstants.LAZY_CHANNEL, personality)
