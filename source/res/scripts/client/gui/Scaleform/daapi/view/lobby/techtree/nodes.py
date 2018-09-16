# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/nodes.py
from gui.Scaleform.daapi.view.lobby.techtree.settings import DEFAULT_UNLOCK_PROPS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import MONEY_UNDEFINED, Currency
from helpers import i18n

class BaseNode(object):
    __slots__ = ('nodeName', 'nodeCD', 'nationID', 'itemTypeID', 'isFound', 'isAnnouncement', 'order')

    def __init__(self, nodeName, nationID, itemTypeID, nodeCD, isFound=True, isAnnouncement=False, order=0):
        super(BaseNode, self).__init__()
        self.nodeName = nodeName
        self.nationID = nationID
        self.itemTypeID = itemTypeID
        self.nodeCD = nodeCD
        self.isFound = isFound
        self.isAnnouncement = isAnnouncement
        self.order = order


class ExposedNode(object):
    __slots__ = ('__nodeCD', '__earnedXP', '__state', '__unlockProps', '__guiPrice', '__displayInfo')

    def __init__(self, nodeCD, earnedXP, state, displayInfo, unlockProps=None, price=None):
        super(ExposedNode, self).__init__()
        self.__nodeCD = nodeCD
        self.__earnedXP = earnedXP
        self.__state = state
        self.__displayInfo = displayInfo
        self.__unlockProps = unlockProps or DEFAULT_UNLOCK_PROPS
        self.__guiPrice = price or MONEY_UNDEFINED

    def clear(self):
        self.__displayInfo = None
        self.__unlockProps = DEFAULT_UNLOCK_PROPS
        self.__guiPrice = MONEY_UNDEFINED
        return

    def getNodeCD(self):
        return self.__nodeCD

    def getEarnedXP(self):
        return self.__earnedXP

    def getState(self):
        return self.__state

    def setState(self, state):
        self.__state = state

    def addStateFlag(self, flag):
        self.__state |= flag

    def getDisplayInfo(self):
        return self.__displayInfo

    def getUnlockTuple(self):
        return self.__unlockProps.makeTuple()

    def getUnlockProps(self):
        return self.__unlockProps

    def setUnlockProps(self, unlockProps):
        self.__unlockProps = unlockProps

    def getShopPrice(self):
        return (self.__guiPrice.getSignValue(Currency.CREDITS), self.__guiPrice.getSignValue(Currency.GOLD), self.getActionPrice())

    def setGuiPrice(self, price):
        self.__guiPrice = price

    def getTags(self):
        raise NotImplementedError

    def getLevel(self):
        raise NotImplementedError

    def getTypeName(self):
        raise NotImplementedError

    def getShortUserName(self):
        raise NotImplementedError

    def getLongUserName(self):
        raise NotImplementedError

    def getIcon(self):
        raise NotImplementedError

    def getSmallIcon(self):
        raise NotImplementedError

    def getActionPrice(self):
        raise NotImplementedError

    def isVehicle(self):
        raise NotImplementedError

    def isRented(self):
        raise NotImplementedError

    def isPremiumIGR(self):
        raise NotImplementedError

    def isPreviewAllowed(self):
        raise NotImplementedError

    def getPreviewLabel(self):
        raise NotImplementedError

    def getStatus(self):
        raise NotImplementedError

    def getCompareData(self):
        raise NotImplementedError

    def getExtraInfo(self, rootItem):
        raise NotImplementedError


class RealNode(ExposedNode):
    __slots__ = ('__item',)

    def __init__(self, nodeCD, item, earnedXP, state, displayInfo, unlockProps=None, price=None):
        super(RealNode, self).__init__(nodeCD, earnedXP, state, displayInfo, unlockProps=unlockProps, price=price)
        self.__item = item

    def clear(self):
        super(RealNode, self).clear()
        self.__item = None
        return

    def getTags(self):
        return self.__item.tags

    def getLevel(self):
        return self.__item.level

    def getTypeName(self):
        return self.__item.itemTypeName

    def getShortUserName(self):
        return self.__item.shortUserName

    def getLongUserName(self):
        return self.__item.longUserName

    def getIcon(self):
        return self.__item.icon

    def getSmallIcon(self):
        return self.__item.iconSmall

    def getActionPrice(self):
        from gui.shared.tooltips.formatters import getActionPriceData
        return getActionPriceData(self.__item)

    def isVehicle(self):
        return self.__item.itemTypeID == GUI_ITEM_TYPE.VEHICLE

    def isRented(self):
        return self.__item.isRented

    def isPremiumIGR(self):
        return self.__item.isPremiumIGR

    def isPreviewAllowed(self):
        return self.__item.isInInventory or self.__item.isPreviewAllowed()

    def getPreviewLabel(self):
        label = ''
        if self.isVehicle():
            if self.__item.isInInventory:
                label = i18n.makeString(MENU.RESEARCH_LABELS_BUTTON_SHOWINHANGAR)
            else:
                label = i18n.makeString(MENU.RESEARCH_SHOWINPREVIEWBTN_LABEL)
        return label

    def getStatus(self):
        status, statusLevel = ('', '')
        item = self.__item
        if item is not None and item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            if item.isRented and not item.isTelecom:
                if item.rentalIsOver:
                    if item.isPremiumIGR:
                        status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_IGRRENTALISOVER)
                    else:
                        status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_RENTALISOVER)
                    statusLevel = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                elif not item.isPremiumIGR:
                    status = RentLeftFormatter(item.rentInfo).getRentLeftStr()
                    statusLevel = Vehicle.VEHICLE_STATE_LEVEL.RENTED
            elif item.isRentable and item.isRentAvailable:
                status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_ISRENTABLE)
                statusLevel = Vehicle.VEHICLE_STATE_LEVEL.RENTED
            elif item.canTradeIn:
                status = i18n.makeString(MENU.TRADE_IN)
                statusLevel = Vehicle.VEHICLE_STATE_LEVEL.INFO
        return (status, statusLevel)

    def getCompareData(self):
        if self.__item is not None and self.__item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            from gui.Scaleform.daapi.view.lobby.vehicle_compare import formatters
            return formatters.getTreeNodeCompareData(self.__item)
        else:
            return {}

    def getExtraInfo(self, rootItem):
        descriptor = rootItem.descriptor if rootItem else None
        return self.__item.getExtraIconInfo(descriptor)


class AnnouncementNode(ExposedNode):
    __slots__ = ('__announcementInfo',)

    def __init__(self, nodeCD, info, state, displayInfo):
        super(AnnouncementNode, self).__init__(nodeCD, 0, state, displayInfo, unlockProps=None, price=None)
        self.__announcementInfo = info
        return

    def clear(self):
        super(AnnouncementNode, self).clear()
        self.__announcementInfo = None
        return

    def getTags(self):
        return self.__announcementInfo.tags

    def getLevel(self):
        return self.__announcementInfo.level

    def getTypeName(self):
        return GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE]

    def getShortUserName(self):
        return i18n.makeString(self.__announcementInfo.userString)

    def getLongUserName(self):
        return i18n.makeString(self.__announcementInfo.userString)

    def getIcon(self):
        return self.__announcementInfo.icon

    def getSmallIcon(self):
        return self.__announcementInfo.icon

    def getActionPrice(self):
        return None

    def isRented(self):
        return False

    def isPremiumIGR(self):
        return False

    def isVehicle(self):
        return True

    def isPreviewAllowed(self):
        return False

    def getPreviewLabel(self):
        pass

    def getStatus(self):
        pass

    def getCompareData(self):
        return {}

    def getExtraInfo(self, rootItem):
        return None
