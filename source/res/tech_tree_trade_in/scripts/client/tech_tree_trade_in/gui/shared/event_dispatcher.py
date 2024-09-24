# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/shared/event_dispatcher.py
from typing import Optional
from debug_utils import LOG_WARNING
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from tech_tree_trade_in.gui.scaleform.genConsts.TECH_TREE_TRADE_IN_HANGAR_ALIASES import TECH_TREE_TRADE_IN_HANGAR_ALIASES
from gui.shared.notifications import NotificationPriorityLevel
from tech_tree_trade_in.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from tech_tree_trade_in_common.tech_tree_trade_in_constants import TTT_OP_TYPES
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

def showTechTreeTradeInView(viewId):
    from tech_tree_trade_in.gui.impl.lobby.meta_view.tech_tree_trade_in_view import TechTreeTradeInViewWindow
    window = TechTreeTradeInViewWindow(viewId)
    window.load()


def showBranchTechTradeInOverlay(url):
    if not url:
        LOG_WARNING('The {} url is missing'.format(url))
        return
    showBrowserOverlayView(url=url, alias=TECH_TREE_TRADE_IN_HANGAR_ALIASES.TECH_TREE_TRADE_IN_BROWSER_OVERLAY, forcedSkipEscape=True)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushTradeInCompleteNotification(branchToTrade, branchToReceive, data, systemMessages=None):
    resources = {}
    for ops in data.values():
        for assetType, assetDict in ops.get(TTT_OP_TYPES.FEE_WITHDRAW, {}).items():
            if assetType == 266:
                resources.setdefault('currency', {})['gold'] = sum(assetDict.values())
            if assetType == 268:
                resources.setdefault('currency', {})['freeXP'] = sum(assetDict.values())
            if assetType == 290:
                resources.setdefault('currency', {})['crystal'] = sum(assetDict.values())
            if assetType == 299:
                resources.setdefault('blueprints', {}).update(assetDict)

    lockedVehicles, unlockedVehicles = _getTradedVehsLists(data, branchToTrade, branchToReceive)
    msg = {'resources': resources,
     'lockedVehicles': lockedVehicles,
     'unlockedVehicles': unlockedVehicles}
    systemMessages.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.TECH_TREE_TRADE_IN_COMPLETED_NOTIFICATION, auxData=msg)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushTradeInDetailsNotification(data, systemMessages=None):
    numRecruits = 0
    numSentToBarracks = 0
    postProgressionCompensation = 0
    xpTransferredVehCD = -1
    for ops in data.values():
        numRecruits += len(ops.get(TTT_OP_TYPES.TURN_CREW, []))
        numSentToBarracks += len(ops.get(TTT_OP_TYPES.MOVE_TANKMAN, []))
        postProgressionCompensation += ops.get(TTT_OP_TYPES.CREDITS_COMPENSATION, 0)
        if TTT_OP_TYPES.MOVE_XP in ops:
            xpTransferredVehCD = ops[TTT_OP_TYPES.MOVE_XP]['intCD']

    msg = {'postProgressionCompensation': {'currency': {'credits': postProgressionCompensation}},
     'crew': {'recruits': numRecruits,
              'sentToBarracks': numSentToBarracks},
     'xpTransferredVehCD': xpTransferredVehCD}
    systemMessages.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.TECH_TREE_TRADE_IN_DETAILS_NOTIFICATION, auxData=msg)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushTechTreeTradeInErrorNotification(systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientSysMessage(backport.text(R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.error.body()), SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.error.title())})


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushTechTreeTradeInUnavailableNotification(systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientSysMessage(backport.text(R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.vehicleUnavailable.body()), SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.tech_tree_trade_in_messenger.serviceChannelMessages.vehicleUnavailable.title())})


def showTechTreeView(nation):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)


def _getTradedVehsLists(operationsData, branchToTrade, branchToReceive):
    lockedVehicles, unlockedVehicles = set(), set()
    for intCD, ops in operationsData.iteritems():
        if intCD <= 0:
            continue
        if ops.get(TTT_OP_TYPES.REMOVAL) or ops.get(TTT_OP_TYPES.DERESEARCH):
            lockedVehicles.add(intCD)
        if ops.get(TTT_OP_TYPES.ACCRUAL) or ops.get(TTT_OP_TYPES.RESEARCH):
            unlockedVehicles.add(intCD)

    return ([ intCD for intCD in branchToTrade if intCD in lockedVehicles ], [ intCD for intCD in branchToReceive if intCD in unlockedVehicles ])
