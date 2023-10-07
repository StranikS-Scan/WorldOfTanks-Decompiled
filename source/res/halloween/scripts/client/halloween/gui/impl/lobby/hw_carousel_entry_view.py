# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_carousel_entry_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from halloween.gui.impl.gen.view_models.views.lobby.hw_carousel_entry_view_model import HwCarouselEntryViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.hangar import ICarouselEventEntry
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
from halloween.gui.shared.event_dispatcher import showHalloweenShop

class HWCarouselEntryView(ViewImpl, ICarouselEventEntry):
    __slots__ = ()
    _hwController = dependency.descriptor(IHalloweenController)

    @staticmethod
    def getIsActive(state):
        return HWCarouselEntryView._hwController.isAvailable() and HWCarouselEntryView._hwController.isEventPrbActive()

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.halloween.lobby.HWCarouselEntryView(), flags=ViewFlags.VIEW, model=HwCarouselEntryViewModel())
        super(HWCarouselEntryView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HWCarouselEntryView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HWCarouselEntryView, self)._onLoading(*args, **kwargs)
        self.viewModel.onAction += self.__onAction

    def _finalize(self):
        self.viewModel.onAction -= self.__onAction
        super(HWCarouselEntryView, self)._finalize()

    def __onAction(self):
        showHalloweenShop()
