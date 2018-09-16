# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/nodes.py
from gui.Scaleform.daapi.view.lobby.techtree.settings import DEFAULT_UNLOCK_PROPS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import MONEY_UNDEFINED, Currency
from gui.shared.utils import CLIP_ICON_PATH, HYDRAULIC_ICON_PATH
from helpers import i18n

class BaseNode(object):
    """This is class holds basic information about node in techtree."""
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
    """ This is class includes node information and some expanded information
    to generate presentation information."""
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
        """Clears node data."""
        self.__displayInfo = None
        self.__unlockProps = DEFAULT_UNLOCK_PROPS
        self.__guiPrice = MONEY_UNDEFINED
        return

    def getNodeCD(self):
        """ Gets int-type compact descriptor of node. """
        return self.__nodeCD

    def getEarnedXP(self):
        """ Gets earned XP for specified node. """
        return self.__earnedXP

    def getState(self):
        """ Gets bitmask that contains flags from NODE_STATE_FLAGS. """
        return self.__state

    def setState(self, state):
        """ Sets new state.
        :param state: integer containing bitmask.
        """
        self.__state = state

    def addStateFlag(self, flag):
        """ Adds flag to bitmask.
        :param flag: integer containing bit from NODE_STATE_FLAGS.
        """
        self.__state |= flag

    def getDisplayInfo(self):
        """Gets display information"""
        return self.__displayInfo

    def getUnlockTuple(self):
        """ Gets tuple containing unlock information."""
        return self.__unlockProps.makeTuple()

    def getUnlockProps(self):
        """ Gets instance of UnlockProps. """
        return self.__unlockProps

    def setUnlockProps(self, unlockProps):
        """ Sets new instance of UnlockProps.
        :param unlockProps: instance of UnlockProps.
        """
        self.__unlockProps = unlockProps

    def getShopPrice(self):
        """ Gets tuple containing shop prices: price in credits, price in gold
        and action price."""
        return (self.__guiPrice.getSignValue(Currency.CREDITS), self.__guiPrice.getSignValue(Currency.GOLD), self.getActionPrice())

    def setGuiPrice(self, price):
        """ Sets new GUI price.
        :param price: instance of Money.
        """
        self.__guiPrice = price

    def getTags(self):
        """ Gets tags of vehicle or item. """
        raise NotImplementedError

    def getLevel(self):
        """ Gets level of vehicle or item. """
        raise NotImplementedError

    def getTypeName(self):
        """ Gets name of item type. """
        raise NotImplementedError

    def getShortUserName(self):
        """ Gets short i18n name of item. """
        raise NotImplementedError

    def getLongUserName(self):
        """ Gets long i18n name of item. """
        raise NotImplementedError

    def getIcon(self):
        """ Gets relative path of item icon. """
        raise NotImplementedError

    def getSmallIcon(self):
        """ Gets relative path of item small icon. """
        raise NotImplementedError

    def getActionPrice(self):
        """ Gets action price if it has, otherwise - None. """
        raise NotImplementedError

    def isVehicle(self):
        """ Is node vehicle. """
        raise NotImplementedError

    def isRented(self):
        """ Is item rented. """
        raise NotImplementedError

    def isPremiumIGR(self):
        """ Is item premium IGR. """
        raise NotImplementedError

    def isPreviewAllowed(self):
        """ Is item preview allowed. """
        raise NotImplementedError

    def getPreviewLabel(self):
        """ Gets label for preview button. """
        raise NotImplementedError

    def getStatus(self):
        """ Gets current state of vehicle or empty string for other items. """
        raise NotImplementedError

    def getCompareData(self):
        """ Gets comparative information for vehicle or empty dict for other items. """
        raise NotImplementedError

    def getExtraInfo(self, rootItem):
        """ Gets exclusive information about item. """
        raise NotImplementedError


class RealNode(ExposedNode):
    """ This is class  is used to get some expanded information from GUI item."""
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
        extraInfo = None
        if self.__item.itemTypeID == GUI_ITEM_TYPE.GUN and self.__item.isClipGun(rootItem.descriptor):
            extraInfo = CLIP_ICON_PATH
        elif self.__item.itemTypeID == GUI_ITEM_TYPE.CHASSIS and self.__item.isHydraulicChassis():
            extraInfo = HYDRAULIC_ICON_PATH
        return extraInfo


class AnnouncementNode(ExposedNode):
    """ This is class  is used to get some expanded information from light object.
    This light object contains short information about announcement vehicle."""
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
