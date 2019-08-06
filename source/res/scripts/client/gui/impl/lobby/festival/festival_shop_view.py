# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_shop_view.py
import logging
from account_helpers.AccountSettings import FESTIVAL_SHOP_VISITED, AccountSettings
from adisp import process
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.processors import FestivalBuyPackageProcessor
from frameworks.wulf import ViewFlags
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_shop_slot_model import FestivalShopSlotModel
from gui.impl.gen.view_models.views.lobby.festival.festival_shop_view_model import FestivalShopViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.festival import IFestivalController
_logger = logging.getLogger(__name__)

class FestivalShopView(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalShopView, self).__init__(R.views.lobby.festival.festival_shop_view.FestivalShopView(), ViewFlags.VIEW, FestivalShopViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(FestivalShopView, self).getViewModel()

    def _initialize(self):
        super(FestivalShopView, self)._initialize()
        self.getViewModel().onPackageClicked += self.__onPackageClicked
        self.__festController.onDataUpdated += self.__onDataUpdated
        self.__updateUnlock()
        self.__rebuildPackages()
        if self.__festController.isCommonItemCollected():
            AccountSettings.setNotifications(FESTIVAL_SHOP_VISITED, True)

    def _finalize(self):
        self.getViewModel().onPackageClicked -= self.__onPackageClicked
        self.__festController.onDataUpdated -= self.__onDataUpdated
        super(FestivalShopView, self)._finalize()

    def __onPackageClicked(self, eventData):
        packageID = eventData.get('packageId')
        if packageID:
            self.__buyPackage(packageID)

    @process
    def __buyPackage(self, packageID):
        result = yield FestivalBuyPackageProcessor(packageID, self.getParentWindow()).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onDataUpdated(self, keys):
        if FestSyncDataKeys.ITEMS in keys:
            self.__updateUnlock()
            self.__rebuildPackages()
            return
        if FestSyncDataKeys.PACKAGES in keys:
            self.__rebuildPackages()
        if any((key in keys for key in (FestSyncDataKeys.TICKETS, FestSyncDataKeys.PURCHASES))):
            self.__updatePurchases()

    def __updateUnlock(self):
        self.viewModel.setIsLocked(not self.__festController.isCommonItemCollected())

    def __rebuildPackages(self):
        packagesModel = self.viewModel.packages.getItems()
        packagesModel.clear()
        tickets = self.__festController.getTickets()
        availablePackages = self.__festController.getPackages()
        isShopLocked = not self.__festController.isCommonItemCollected()
        for packageID, package in availablePackages.iteritems():
            if not package.extractedItems:
                continue
            firstItem = package.extractedItems[0]
            slotModel = FestivalShopSlotModel()
            slotModel.setPackageID(packageID)
            slotModel.setPrice(package.price)
            slotModel.setIsMoneyEnough(tickets >= package.price if not isShopLocked else True)
            slotModel.setTitle(firstItem.title)
            slotModel.setDescription(firstItem.description)
            slotModel.setCounter(firstItem.count)
            slotModel.setIcon(firstItem.icon)
            slotModel.setModifierIcon(firstItem.modifierIcon)
            packagesModel.addViewModel(slotModel)

        packagesModel.invalidate()
        self.viewModel.setPackageCount(len(availablePackages))

    def __updatePurchases(self):
        tickets = self.__festController.getTickets()
        availablePackages = self.__festController.getPackages()
        packagesModel = self.viewModel.packages.getItems()
        isShopLocked = not self.__festController.isCommonItemCollected()
        for slotModel in packagesModel:
            pkgID = slotModel.getPackageID()
            if pkgID not in availablePackages:
                _logger.error('No packageID %d in packages!', pkgID)
                continue
            package = availablePackages[pkgID]
            slotModel.setPrice(package.price)
            slotModel.setIsMoneyEnough(tickets >= package.price if not isShopLocked else True)
