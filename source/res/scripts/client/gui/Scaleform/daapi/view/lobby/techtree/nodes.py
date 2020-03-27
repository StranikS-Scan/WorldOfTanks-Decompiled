# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/nodes.py
from gui.Scaleform.daapi.view.lobby.techtree.settings import DEFAULT_UNLOCK_PROPS
from gui.shared.formatters import text_styles
from gui.shared.formatters import getItemPricesVO, getItemRestorePricesVO, getItemUnlockPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.money import MONEY_UNDEFINED
from helpers.time_utils import getCurrentTimestamp
from helpers import i18n, dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.server_events import IEventsCache

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
    __slots__ = ('__nodeCD', '__earnedXP', '__state', '__unlockProps', '__bpfProps', '__guiPrice', '__displayInfo')

    def __init__(self, nodeCD, earnedXP, state, displayInfo, unlockProps=None, bpfProps=None, price=None):
        super(ExposedNode, self).__init__()
        self.__nodeCD = nodeCD
        self.__earnedXP = earnedXP
        self.__state = state
        self.__displayInfo = displayInfo
        self.__unlockProps = unlockProps or DEFAULT_UNLOCK_PROPS
        self.__bpfProps = bpfProps
        self.__guiPrice = price or MONEY_UNDEFINED

    def clear(self):
        self.__displayInfo = None
        self.__unlockProps = DEFAULT_UNLOCK_PROPS
        self.__bpfProps = None
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

    def getBpfProps(self):
        return self.__bpfProps

    def setBpfProps(self, bpfProps):
        self.__bpfProps = bpfProps

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

    def getIcon(self):
        raise NotImplementedError

    def getSmallIcon(self):
        raise NotImplementedError

    def isVehicle(self):
        raise NotImplementedError

    def isRented(self):
        raise NotImplementedError

    def getItemPrices(self):
        raise NotImplementedError

    def getBuyPrices(self):
        raise NotImplementedError

    def getCompareData(self):
        raise NotImplementedError

    def getExtraInfo(self, rootItem):
        raise NotImplementedError

    def isActionPrice(self):
        raise NotImplementedError

    def getActionDiscount(self):
        raise NotImplementedError

    def getBlueprintLabel(self):
        raise NotImplementedError

    def getBlueprintProgress(self):
        raise NotImplementedError

    def getActionFinishTime(self):
        raise NotImplementedError

    def getRestoreFinishTime(self):
        raise NotImplementedError

    def getRentInfo(self):
        raise NotImplementedError

    def hasItemNationGroup(self):
        raise NotImplementedError


class RealNode(ExposedNode):
    __slots__ = ('__item',)
    __eventsCache = dependency.descriptor(IEventsCache)
    __tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, nodeCD, item, earnedXP, state, displayInfo, unlockProps=None, bpfProps=None, price=None):
        super(RealNode, self).__init__(nodeCD, earnedXP, state, displayInfo, unlockProps=unlockProps, bpfProps=bpfProps, price=price)
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
        return self.__item.getGUIEmblemID()

    def getShortUserName(self):
        return self.__item.shortUserName

    def getIcon(self):
        return self.__item.icon

    def getSmallIcon(self):
        return self.__item.iconSmall

    def isVehicle(self):
        return self.__item.itemTypeID == GUI_ITEM_TYPE.VEHICLE

    def isRented(self):
        return self.__item.isRented

    def getItemPrices(self):
        item = self.__item
        unlockProps = self.getUnlockProps()
        if item.canTradeIn:
            return getItemPricesVO(self.__tradeIn.getTradeInPrice(item))
        elif not item.isUnlocked and unlockProps is not None and not item.isCollectible:
            return getItemUnlockPricesVO(unlockProps)
        else:
            return getItemRestorePricesVO(item.restorePrice) if item.isRestoreAvailable() else getItemPricesVO(item.getBuyPrice())

    def getBuyPrices(self):
        return getItemPricesVO(self.__item.getBuyPrice())

    def isActionPrice(self):
        itemPrice = self.__item.buyPrices.itemPrice
        return itemPrice.isActionPrice()

    def getActionDiscount(self):
        return self.__item.buyPrices.itemPrice.getActionPrc()

    def getCompareData(self):
        if self.__item is not None and self.__item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            from gui.Scaleform.daapi.view.lobby.vehicle_compare import formatters
            return formatters.getTreeNodeCompareData(self.__item)
        else:
            return {}

    def getExtraInfo(self, rootItem):
        descriptor = rootItem.descriptor if rootItem else None
        return self.__item.getExtraIconInfo(descriptor)

    def getBlueprintLabel(self):
        bpfProps = self.getBpfProps()
        label = ''
        if bpfProps is not None:
            label = text_styles.counterLabelText(' '.join((str(bpfProps.filledCount), '/', str(bpfProps.totalCount))))
        return label

    def getBlueprintProgress(self):
        bpfProps = self.getBpfProps()
        progress = 0.0
        if bpfProps is not None and bpfProps.totalCount != 0:
            progress = float(bpfProps.filledCount) / bpfProps.totalCount
        return progress

    def getActionFinishTime(self):
        actions = self.__eventsCache.getItemAction(self.__item)
        actions = sorted(actions, key=lambda elem: elem[0])
        if not actions:
            return 0
        bestAction = self.__eventsCache.getActions().get(actions[0][1], '')
        return bestAction.getFinishTime() if bestAction else 0

    def getRestoreFinishTime(self):
        return self.__item.restoreInfo.getRestoreTimeLeft() + getCurrentTimestamp() if self.__item.isRestorePossible() and self.__item.hasLimitedRestore() else 0

    def getRentInfo(self):
        rentMoney = self.__item.minRentPrice
        return (rentMoney, rentMoney.getCurrency()) if rentMoney else (0, None)

    def hasItemNationGroup(self):
        return self.__item.hasNationGroup


class AnnouncementNode(ExposedNode):
    __slots__ = ('__announcementInfo',)

    def __init__(self, nodeCD, info, state, displayInfo):
        super(AnnouncementNode, self).__init__(nodeCD, 0, state, displayInfo, unlockProps=None, bpfProps=None, price=None)
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

    def getIcon(self):
        return self.__announcementInfo.icon

    def getSmallIcon(self):
        return self.__announcementInfo.icon

    def isRented(self):
        return False

    def isVehicle(self):
        return True

    def getItemPrices(self):
        return None

    def getBuyPrices(self):
        return None

    def getCompareData(self):
        return {}

    def getExtraInfo(self, rootItem):
        return None

    def isActionPrice(self):
        return False

    def getActionDiscount(self):
        pass

    def getBlueprintLabel(self):
        pass

    def getBlueprintProgress(self):
        pass

    def getActionFinishTime(self):
        pass

    def getRestoreFinishTime(self):
        pass

    def getRentInfo(self):
        return (0, None)

    def hasItemNationGroup(self):
        return False
