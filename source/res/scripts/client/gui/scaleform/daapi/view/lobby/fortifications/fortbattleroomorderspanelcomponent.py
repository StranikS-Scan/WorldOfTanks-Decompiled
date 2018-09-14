# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleRoomOrdersPanelComponent.py
from collections import namedtuple
import fortified_regions
from helpers import i18n
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.meta.OrdersPanelMeta import OrdersPanelMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.ORDER_TYPES import ORDER_TYPES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
_SlotDataVO = namedtuple('_SlotDataVO', ['orderID',
 'slotID',
 'buildingStr',
 'level',
 'orderType',
 'orderIcon',
 'orderGroup',
 'fortOrderTypeID',
 'isInactive'])

def _makeSlotVO(orderID, slotIdx, buildingLabel = '', level = None, orderIcon = '', orderTypeID = None, isInactive = False, orderType = ORDER_TYPES.FORT_ORDER_CONSUMABLES_ACTIVE_TYPE, orderGroup = ORDER_TYPES.FORT_ORDER_CONSUMABLES_GROUP):
    return _SlotDataVO(orderID, slotIdx, buildingLabel, level, orderType, orderIcon, orderGroup, orderTypeID, isInactive)._asdict()


def _makeEmptySlotVO(slotIdx):
    return _makeSlotVO(ORDER_TYPES.EMPTY_ORDER, slotIdx, orderIcon=RES_ICONS.MAPS_ICONS_ARTEFACT_EMPTYORDER)


class FortBattleRoomOrdersPanelComponent(OrdersPanelMeta, FortViewHelper, UnitListener, AppRef):
    _SLOTS_PROPS = {'slotsCount': 3,
     'groupCount': 1,
     'slotWidth': 50,
     'paddings': 64,
     'groupPadding': 18,
     'ySlotPosition': 5,
     'offsetSlot': -2,
     'popoverAlias': FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS}

    def __init__(self, ctx = None):
        super(FortBattleRoomOrdersPanelComponent, self).__init__()
        self.__battle = self.__battleID = None
        return

    def getOrderTooltipBody(self, orderID):
        if orderID == ORDER_TYPES.EMPTY_ORDER:
            return makeTooltip(i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(orderID)), i18n.makeString(TOOLTIPS.FORTORDERSPANELCOMPONENT_EMPTYSLOT_BODY), None)
        else:
            return ''

    def onConsumablesChanged(self, battleID, consumableOrderTypeID):
        if battleID == self.__battleID:
            self.__updateSlots()

    def onClientStateChanged(self, state):
        if state.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.__updateSlots()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__updateSlots()

    def _populate(self):
        super(FortBattleRoomOrdersPanelComponent, self)._populate()
        self.startFortListening()
        self.startUnitListening()
        if self.fortState.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.__updateSlots()

    def _dispose(self):
        self.stopUnitListening()
        self.stopFortListening()
        super(FortBattleRoomOrdersPanelComponent, self)._dispose()

    def __updateSlots(self):
        fort = self.fortCtrl.getFort()
        canActivateConsumables = self.fortCtrl.getPermissions().canActivateConsumable() and self.unitFunctional.getPermissions().canChangeConsumables()
        self.__battleID = getBattleID()
        self.__battle = fort.getBattle(self.__battleID)
        result = []
        if self.__battle is not None:
            activeConsumes = self.__battle.getActiveConsumables()
            for slotIdx in xrange(fortified_regions.g_cache.consumablesSlotCount):
                if slotIdx in activeConsumes:
                    orderTypeID, level = activeConsumes[slotIdx]
                    orderItem = fort.getOrder(orderTypeID)
                    result.append(_makeSlotVO(self.getOrderUIDbyID(orderTypeID), slotIdx, fort.getBuilding(orderItem.buildingID).userName, level, orderItem.icon, orderTypeID, not canActivateConsumables))
                elif canActivateConsumables:
                    result.append(_makeEmptySlotVO(slotIdx))

        self.as_setPanelPropsS(dict(self._SLOTS_PROPS))
        self.as_setOrdersS(result)
        return
