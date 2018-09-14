# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleRoomOrdersPanelComponent.py
import fortified_regions
from helpers import dependency
from helpers import i18n
from collections import namedtuple
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.meta.SlotsPanelMeta import SlotsPanelMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.ORDER_TYPES import ORDER_TYPES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.fortifications.FortOrder import FortOrder
from gui.shared.fortifications.FortBuilding import FortBuilding
from skeletons.gui.lobby_context import ILobbyContext
_SlotDataVO = namedtuple('_SlotDataVO', ['id',
 'slotID',
 'buildingStr',
 'level',
 'type',
 'icon',
 'group',
 'fortOrderTypeID',
 'isInactive'])

def _makeSlotVO(orderID, slotIdx, buildingLabel='', level=None, orderIcon='', orderTypeID=None, isInactive=False, orderType=ORDER_TYPES.FORT_ORDER_CONSUMABLES_ACTIVE_TYPE, orderGroup=ORDER_TYPES.FORT_ORDER_CONSUMABLES_GROUP):
    return _SlotDataVO(orderID, slotIdx, buildingLabel, level, orderType, orderIcon, orderGroup, orderTypeID, isInactive)._asdict()


def _makeEmptySlotVO(slotIdx, isInactive):
    return _makeSlotVO(ORDER_TYPES.EMPTY_ORDER, slotIdx, isInactive=isInactive, orderIcon=RES_ICONS.MAPS_ICONS_ARTEFACT_EMPTYORDER)


class FortBattleRoomOrdersPanelComponent(SlotsPanelMeta, FortViewHelper, IUnitListener):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(FortBattleRoomOrdersPanelComponent, self).__init__()

    def getSlotTooltipBody(self, orderID):
        return makeTooltip(i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(orderID)), i18n.makeString(TOOLTIPS.FORTORDERSPANELCOMPONENT_EMPTYSLOT_BODY), None) if orderID == ORDER_TYPES.EMPTY_ORDER else ''

    def onOrderChanged(self, orderTypeID, reason):
        if self.fortCtrl.getFort().getOrder(orderTypeID).isConsumable:
            self.__updateSlots()

    def onConsumablesChanged(self, unitMgrID):
        self.__updateSlots()

    def onUnitExtraChanged(self, extra):
        self.__updateSlots()

    def onClientStateChanged(self, state):
        self.__updateSlots()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__updateSlots()

    def _populate(self):
        super(FortBattleRoomOrdersPanelComponent, self)._populate()
        self.startPrbListening()
        self.__updateSlots()

    def _dispose(self):
        self.stopPrbListening()
        super(FortBattleRoomOrdersPanelComponent, self)._dispose()

    def _isConsumablesAvailable(self):
        return self.prbEntity.getExtra().canUseEquipments

    def _getSlotsProps(self):
        return {'slotsCount': 3,
         'groupCount': 1,
         'slotWidth': 50,
         'paddings': 64,
         'groupPadding': 18,
         'ySlotPosition': 5,
         'offsetSlot': -2,
         'useOnlyLeftBtn': True,
         'popoverAlias': FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS}

    def __updateSlots(self):
        if not self._isConsumablesAvailable():
            return
        else:
            extra = self.prbEntity.getExtra()
            consumablesVisible = self.fortCtrl.getPermissions().canActivateConsumable() and self.prbEntity.getPermissions().canChangeConsumables()
            consumablesDisabled = not self.lobbyContext.getServerSettings().isFortsEnabled()
            result = []
            if extra is not None:
                activeConsumes = extra.getConsumables()
                for slotIdx in xrange(fortified_regions.g_cache.consumablesSlotCount):
                    if slotIdx in activeConsumes:
                        orderTypeID, level = activeConsumes[slotIdx]
                        orderItem = FortOrder(orderTypeID)
                        building = FortBuilding(typeID=orderItem.buildingID)
                        result.append(_makeSlotVO(self.getOrderUIDbyID(orderTypeID), slotIdx, building.userName, level, orderItem.icon, orderTypeID, not consumablesVisible or consumablesDisabled))
                    if consumablesVisible:
                        result.append(_makeEmptySlotVO(slotIdx, consumablesDisabled))

            self.as_setPanelPropsS(dict(self._getSlotsProps()))
            self.as_setSlotsS(result)
            return
