# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/dialog_view_data.py
import nations
from gui.impl.auxiliary.detachment_helper import getTankmanResIcon
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache

class DialogViewData(object):
    __slots__ = ('ctx', 'credits', 'gold', 'crystals', 'freeExp', 'userGoldCount', 'goldToCreditRate', 'goldToCreditDiscount', 'needCredits', 'title', 'okBtnTitle', 'cancelBtnTitle', 'icon', '_ctx', '_stats', '_shop')
    _itemsCache = dependency.descriptor(IItemsCache)
    _detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self, ctx):
        self._ctx = ctx
        self._stats = self._itemsCache.items.stats
        self._shop = self._itemsCache.items.shop
        self._setCommonData()
        self._setCommonViewData()
        self._setExtraData()

    def _setCommonData(self):
        self.credits = self._stats.money.credits
        self.gold = self._stats.money.gold
        self.crystals = self._stats.money.crystal
        self.freeExp = self._stats.freeXP
        self.goldToCreditRate = self._shop.exchangeRate
        self.goldToCreditDiscount = 0
        self.needCredits = self._ctx['needCredits']

    def _setCommonViewData(self):
        self._setTitle()
        self._setOkBtnText()
        self._setCancelBtnText()
        self._setIcon()

    def _setTitle(self):
        self.title = R.strings.detachment.vehicleCurrency.title()

    def _setOkBtnText(self):
        self.okBtnTitle = R.strings.detachment.convertCurrency.trade()

    def _setCancelBtnText(self):
        self.cancelBtnTitle = R.strings.detachment.convertCurrency.reset()

    def _setIcon(self):
        self.icon = R.images.gui.maps.shop.vehicles.c_180x135.dyn('empty_tank')()

    def _setExtraData(self):
        pass


class DialogVehicleViewData(DialogViewData):
    __slots__ = ('vehicleCD', 'vehicleItem', 'vehName', 'vehLvl', 'vehType', 'vehNation', 'isVehElite')

    def __init__(self, ctx):
        self.vehicleCD = ctx['vehicleCD']
        self.vehicleItem = self._itemsCache.items.getItemByCD(self.vehicleCD)
        super(DialogVehicleViewData, self).__init__(ctx)

    def _setTitle(self):
        self.title = self._ctx.get('title', R.strings.detachment.vehicleCurrency.title())

    def _setIcon(self):
        resName = getIconResourceName(getNationLessName(self.vehicleItem.name))
        self.icon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(resName)()

    def _setExtraData(self):
        vehicleName = self.vehicleItem.shortUserName
        self.vehName = vehicleName
        self.vehLvl = self.vehicleItem.level
        self.vehType = self.vehicleItem.type
        self.vehNation = nations.NAMES[self.vehicleItem.nationID]
        self.isVehElite = self.vehicleItem.isElite


class DialogRestoreDetachmentViewData(DialogViewData):
    __slots__ = ('_detachment',)

    def __init__(self, ctx):
        self._detachment = self._detachmentCache.getDetachment(ctx['detInvID'])
        super(DialogRestoreDetachmentViewData, self).__init__(ctx)

    def _setTitle(self):
        self.title = R.strings.detachment.detachment_restore.title()

    def _setIcon(self):
        self.icon = self._detachment.cmdrPortrait


class DialogCrewbookViewData(DialogViewData):
    __slots__ = ('crewbookItem',)

    def __init__(self, ctx):
        self.crewbookItem = self._itemsCache.items.getItemByCD(ctx['crewbookCD'])
        super(DialogCrewbookViewData, self).__init__(ctx)

    def _setTitle(self):
        self.title = R.strings.detachment.crewbookCurrency.title()

    def _setIcon(self):
        self.icon = R.images.gui.maps.icons.crewBooks.books.large.dyn(self.crewbookItem.getBonusIconName())()


class DialogRestoreRecruitViewData(DialogViewData):
    __slots__ = ('_tankman',)

    def __init__(self, ctx):
        self._tankman = self._itemsCache.items.getTankman(ctx['tankmanInvID'])
        super(DialogRestoreRecruitViewData, self).__init__(ctx)

    def _setTitle(self):
        self.title = R.strings.detachment.recruitRestore.title()

    def _setIcon(self):
        self.icon = getTankmanResIcon(self._tankman)


class DialogMatrixEditViewData(DialogViewData):

    def _setTitle(self):
        self.title = self._ctx['title']
