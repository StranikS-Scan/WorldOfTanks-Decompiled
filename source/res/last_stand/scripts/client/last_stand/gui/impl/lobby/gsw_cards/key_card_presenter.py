# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/key_card_presenter.py
from frameworks.wulf import WindowStatus, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.keys_view_model import KeysViewModel
from last_stand.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from last_stand.gui.shared.event_dispatcher import showBundleWindow
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_shop_controller import ILSShopController
from skeletons.gui.impl import IGuiLoader

class KeyCardPresenter(ViewComponent[KeysViewModel]):
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsCtrl = dependency.descriptor(ILSController)
    lsShopCtrl = dependency.descriptor(ILSShopController)

    def __init__(self):
        super(KeyCardPresenter, self).__init__(model=KeysViewModel)

    def createToolTipContent(self, event, contentID):
        return KeyTooltipView(isPostBattle=False) if contentID == R.views.last_stand.mono.lobby.tooltips.key_tooltip() else super(KeyCardPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(KeyCardPresenter, self)._onLoading()
        self.__fillViewModel()

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (self.lsArtifactsCtrl.onArtefactKeyUpdated, self.__onArtefactKeyUpdated),
         (self.lsArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated),
         (self.lsCtrl.onSettingsUpdate, self.__onSettingsUpdate),
         (self._guiLoader.windowsManager.onWindowStatusChanged, self.__windowStatusChanged)]

    def __onSettingsUpdate(self):
        self.__fillViewModel()

    def __onArtefactKeyUpdated(self):
        self.__updateViewModel()

    def __onArtefactStatusUpdated(self, *args):
        self.__updateViewModel()

    def __hasOverlayWindow(self):
        windows = self.gui.windowsManager.findWindows(lambda w: WindowLayer.FULLSCREEN_WINDOW <= w.layer <= WindowLayer.OVERLAY)
        return len(windows) > 0

    def __fillViewModel(self):
        with self.getViewModel().transaction() as tx:
            tx.setKeys(self.lsArtifactsCtrl.getArtefactKeyQuantity())
            tx.setIsCompleted(self.__isEnoughKeys())

    def __updateViewModel(self):
        if not self.__hasOverlayWindow():
            self.getViewModel().setKeys(self.lsArtifactsCtrl.getArtefactKeyQuantity())
            self.getViewModel().setIsCompleted(self.__isEnoughKeys())
            self.getViewModel().setIsDisabled(self.__isEnoughKeys() and not self.lsShopCtrl.checkIsEnoughBundles())

    def __isEnoughKeys(self):
        return self.lsArtifactsCtrl.getLackOfKeysForArtefacts() == 0

    def __onClick(self):
        showBundleWindow()

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYED:
            self.__updateViewModel()
