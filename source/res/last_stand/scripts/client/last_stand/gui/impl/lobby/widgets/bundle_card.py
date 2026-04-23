# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/bundle_card.py
from __future__ import absolute_import
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.bundle_card_model import BundleCardModel
from last_stand.gui.shared.event_dispatcher import showLSShopBundle
from last_stand.skeletons.ls_shop_controller import ILSShopController

class BundleCard(ViewComponent[BundleCardModel]):
    lsShopCtrl = dependency.descriptor(ILSShopController)

    def __init__(self):
        super(BundleCard, self).__init__(model=BundleCardModel)

    @property
    def viewModel(self):
        return super(BundleCard, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BundleCard, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return [(self.viewModel.onClick, self.__onClick), (self.lsShopCtrl.onBundlesUpdated, self.__onBundlesUpdated), (self.lsShopCtrl.onShopSettingsUpdated, self.__onBundlesUpdated)]

    def __fillModel(self):
        bundles = self.lsShopCtrl.keyBundles()
        with self.viewModel.transaction() as model:
            model.setId('')
            model.setDescriptionKey('')
            if not self.lsShopCtrl.isEnabled():
                return
            for bundle in sorted(bundles, key=lambda bundle: (bundle.groupID, bundle.orderInGroup)):
                if bundle.isWebShopBundle and (bundle.limit is None or self.lsShopCtrl.getPurchaseCount(bundle.bundleID) < bundle.limit):
                    model.setId(bundle.bundleID)
                    model.setDescriptionKey(str(bundle.descrGroupKey))
                    return

        return

    def __onClick(self, args):
        bundleId = args.get('id', None)
        if bundleId is None:
            return
        else:
            bundle = self.lsShopCtrl.getBundleByID(bundleId)
            if not bundle:
                return
            showLSShopBundle(bundle.url)
            return

    def __onBundlesUpdated(self):
        self.__fillModel()
