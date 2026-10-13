# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/page/keys_presenter.py
from __future__ import absolute_import
from frameworks.wulf import WindowStatus, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.gen.view_models.views.lobby.page.header.keys_model import KeysModel
from halloween.gui.impl.lobby.bundle_view import BundleView
from halloween.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from halloween.gui.shared.event_dispatcher import showBundleWindow
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_shop_controller import IHalloweenShopController
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class KeysPresenter(ViewComponent[KeysModel]):
    _guiLoader = dependency.descriptor(IGuiLoader)
    hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    hwCtrl = dependency.descriptor(IHalloweenController)
    hwShopCtrl = dependency.descriptor(IHalloweenShopController)

    def __init__(self):
        super(KeysPresenter, self).__init__(model=KeysModel)

    def createToolTipContent(self, event, contentID):
        return KeyTooltipView(isPostBattle=False) if contentID == R.views.halloween.mono.lobby.tooltips.key_tooltip() else super(KeysPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(KeysPresenter, self)._onLoading()
        self.__fillViewModel()

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (self.hwArtifactsCtrl.onArtefactKeyUpdated, self.__onArtefactKeyUpdated),
         (self.hwArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated),
         (self.hwCtrl.onSettingsUpdate, self.__onSettingsUpdate),
         (self._guiLoader.windowsManager.onWindowStatusChanged, self.__windowStatusChanged)]

    def __needToDisable(self):
        return self.__isEnoughKeys() and not self.hwShopCtrl.checkIsEnoughBundles()

    def __onSettingsUpdate(self):
        self.__fillViewModel()

    def __onArtefactKeyUpdated(self):
        self.__updateViewModel()

    def __onArtefactStatusUpdated(self, *_):
        self.__updateViewModel()

    def __hasOverlayWindow(self):
        windows = self.gui.windowsManager.findWindows(lambda w: WindowLayer.FULLSCREEN_WINDOW <= w.layer <= WindowLayer.OVERLAY)
        return len(windows) > 0

    def __fillViewModel(self):
        with self.getViewModel().transaction() as tx:
            tx.setAmount(self.hwArtifactsCtrl.getArtefactKeyQuantity())
            tx.setIsDisabled(self.__needToDisable())

    def __updateViewModel(self):
        if not self.__hasOverlayWindow():
            self.__fillViewModel()

    def __isEnoughKeys(self):
        return self.hwArtifactsCtrl.getLackOfKeysForArtefacts() == 0

    def __onClick(self):
        showBundleWindow(source=HWLogKeys.HEADER)

    def __windowStatusChanged(self, uniqueID, newStatus):
        vm = self.getViewModel()
        window = self._guiLoader.windowsManager.getWindow(uniqueID)
        if window and isinstance(window.content, BundleView):
            if newStatus == WindowStatus.CREATED:
                vm.setIsDisabled(True)
            elif newStatus == WindowStatus.DESTROYING:
                vm.setIsDisabled(self.__needToDisable())
        elif newStatus == WindowStatus.DESTROYED and not self.__hasOverlayWindow():
            vm.setAmount(self.hwArtifactsCtrl.getArtefactKeyQuantity())
