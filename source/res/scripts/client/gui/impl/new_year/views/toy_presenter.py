# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/toy_presenter.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_decoration_slot_model import NyDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_popover_decoration_slot_model import NyPopoverDecorationSlotModel
from helpers import dependency
from skeletons.new_year import INewYearController
from skeletons.gui.shared import IItemsCache

class _ToyPresenterBase(object):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, toy):
        self._toy = toy
        self.id = toy.getID()
        self.title = toy.getName()
        self.description = toy.getDesc()
        self.setting = toy.getSetting()
        self.imageName = self._getSlotImgName()
        self.rankIcon = toy.getRankIcon()

    def asSlotViewModel(self):
        slotVM = self._createViewModel()
        with slotVM.transaction() as vm:
            self.fillViewModel(vm)
        return slotVM

    def fillViewModel(self, viewModel):
        viewModel.setToyID(self.id)
        viewModel.setTitle(self.title)
        viewModel.setDescription(self.description)
        viewModel.setImageName(self.imageName)

    def _createViewModel(self):
        raise NotImplementedError

    def _getSlotImgName(self):
        return self._toy.getIconName()


class PopoverToyPresenter(_ToyPresenterBase):
    __nyController = dependency.descriptor(INewYearController)

    def fillViewModel(self, viewModel):
        super(PopoverToyPresenter, self).fillViewModel(viewModel)
        viewModel.setSetting(self.setting)
        viewModel.setIsNew(self.__hasCounter())
        viewModel.setCount(self._toy.getCount())
        if self.__nyController.isMaxAtmosphereLevel():
            viewModel.setCount(self._toy.getCount())

    def _createViewModel(self):
        return NyPopoverDecorationSlotModel()

    def _getSlotImgName(self):
        return self._toy.getIconName()

    def __hasCounter(self):
        toyToCheck = self._toy
        if not toyToCheck.getUnseenCount() > 0:
            return False
        return toyToCheck.isNewInCollection() if self.__nyController.isMaxAtmosphereLevel() else False
