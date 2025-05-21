# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/keys_view.py
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer, WindowStatus
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.keys_view_model import KeysViewModel
from last_stand.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from last_stand.gui.shared.event_dispatcher import showBundleWindow
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
from last_stand.skeletons.ls_shop_controller import ILSShopController
from skeletons.gui.impl import IGuiLoader

class KeysView(ViewImpl):
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsCtrl = dependency.descriptor(ILSController)
    lsShopCtrl = dependency.descriptor(ILSShopController)

    def __init__(self, layoutID=R.views.last_stand.lobby.virtual_res.KeysView()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = KeysViewModel()
        super(KeysView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(KeysView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return KeyTooltipView(isPostBattle=False) if contentID == R.views.last_stand.mono.lobby.tooltips.key_tooltip() else super(KeysView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(KeysView, self)._onLoading()
        self.__fillViewModel()

    def _getEvents(self):
        return [(self.viewModel.onClick, self.__onClick),
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
        with self.viewModel.transaction() as tx:
            tx.setKeys(self.lsArtifactsCtrl.getArtefactKeyQuantity())
            tx.setIsCompleted(self.__isEnoughKeys())

    def __updateViewModel(self):
        if not self.__hasOverlayWindow():
            self.viewModel.setKeys(self.lsArtifactsCtrl.getArtefactKeyQuantity())
            self.viewModel.setIsCompleted(self.__isEnoughKeys())
            self.viewModel.setIsDisabled(self.__isEnoughKeys() and not self.lsShopCtrl.checkIsEnoughBundles())

    def __isEnoughKeys(self):
        return self.lsArtifactsCtrl.getLackOfKeysForArtefacts() == 0

    def __onClick(self):
        showBundleWindow()

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYED:
            self.__updateViewModel()
