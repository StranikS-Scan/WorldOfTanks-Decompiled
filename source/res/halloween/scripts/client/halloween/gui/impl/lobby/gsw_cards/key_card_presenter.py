# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/gsw_cards/key_card_presenter.py
from __future__ import absolute_import
from frameworks.wulf import WindowStatus, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.gen.view_models.views.lobby.widgets.keys_view_model import KeysViewModel
from halloween.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from halloween.gui.impl.lobby.tooltips.tooltip_positioner import TooltipPositionerMixin
from halloween.gui.shared.event_dispatcher import showBundleWindow
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_shop_controller import IHalloweenShopController
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class KeyCardPresenter(TooltipPositionerMixin, ViewComponent[KeysViewModel]):
    _guiLoader = dependency.descriptor(IGuiLoader)
    hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    hwCtrl = dependency.descriptor(IHalloweenController)
    hwShopCtrl = dependency.descriptor(IHalloweenShopController)
    __slots__ = ('_source',)

    def __init__(self, source):
        super(KeyCardPresenter, self).__init__(model=KeysViewModel)
        self._source = source

    def createToolTipContent(self, event, contentID):
        return KeyTooltipView(isPostBattle=False) if contentID == R.views.halloween.mono.lobby.tooltips.key_tooltip() else super(KeyCardPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(KeyCardPresenter, self)._onLoading()
        self.__fillViewModel()

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (self.hwArtifactsCtrl.onArtefactKeyUpdated, self.__onArtefactKeyUpdated),
         (self.hwArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated),
         (self.hwCtrl.onSettingsUpdate, self.__onSettingsUpdate),
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
            tx.setKeys(self.hwArtifactsCtrl.getArtefactKeyQuantity())
            tx.setIsCompleted(self.__isEnoughKeys())
            tx.setIsDisabled(self.__isEnoughKeys() and not self.hwShopCtrl.checkIsEnoughBundles())

    def __updateViewModel(self):
        if not self.__hasOverlayWindow():
            self.__fillViewModel()

    def __isEnoughKeys(self):
        return self.hwArtifactsCtrl.getLackOfKeysForArtefacts() == 0

    def __onClick(self):
        showBundleWindow(source=self._source)

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYED:
            self.__updateViewModel()
