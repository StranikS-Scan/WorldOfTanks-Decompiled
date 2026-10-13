# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/shop_style_panel.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.gen.view_models.views.lobby.widgets.shop_style_panel_model import ShopStylePanelModel
from halloween.gui.shared.event_dispatcher import showHalloweenShopVehicle
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_shop_controller import IHalloweenShopController
from helpers import dependency
from items.vehicles import getVehicleType, makeVehicleTypeCompDescrByName
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from halloween_common.configs.halloween_bestiary import EnemyModel

class ShopStylePanelPresenter(ViewComponent[ShopStylePanelModel]):
    __hwCtrl = dependency.descriptor(IHalloweenController)
    __hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)
    __hwShopCtrl = dependency.descriptor(IHalloweenShopController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ShopStylePanelPresenter, self).__init__(model=ShopStylePanelModel)

    @property
    def viewModel(self):
        return super(ShopStylePanelPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ShopStylePanelPresenter, self)._onLoading()
        self.__update()

    def _getEvents(self):
        return [(self.viewModel.onClick, self.__onClick), (g_currentPreviewVehicle.onSelected, self.__update)]

    @staticmethod
    def __onClick():
        showHalloweenShopVehicle()

    def __canPurchaseStyles(self, enemy):
        bundlesForPurchase = []
        for bundleID in enemy.shop.bundles:
            bundle = self.__hwShopCtrl.getBundleByID(bundleID)
            bundlesForPurchase.append(bundle.limit is not None and bundle.limit > self.__hwShopCtrl.getPurchaseCount(bundle.bundleID))

        return any(bundlesForPurchase)

    @staticmethod
    def __getVehName(enemy):
        vehIntCD = makeVehicleTypeCompDescrByName(enemy.shop.vehicle)
        vehType = getVehicleType(vehIntCD)
        return vehType.shortUserString

    def __update(self):
        enemyIntCD = g_currentPreviewVehicle.intCD
        if not enemyIntCD:
            return
        enemy = self.__hwBestiaryCtrl.getEnemyByIntCD(enemyIntCD)
        if not enemy or not enemy.shop.vehicle:
            return
        with self.viewModel.transaction() as model:
            model.setName(self.__getVehName(enemy))
            model.setTimer(self.__hwCtrl.remainingEventSeconds)
            model.setIsOwned(not self.__canPurchaseStyles(enemy))
