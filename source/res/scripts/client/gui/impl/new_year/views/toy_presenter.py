# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/toy_presenter.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_break_decoration_slot_model import NewYearBreakDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_craft_decoration_slot_model import NewYearCraftDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_popover_decoration_slot_model import NewYearPopoverDecorationSlotModel
from gui.server_events.awards_formatters import EXTRA_BIG_AWARD_SIZE, AWARDS_SIZES
from items.components.ny_constants import ToyTypes

class _ToyPresenterBase(object):

    def __init__(self, toy):
        self._toy = toy
        self.id = toy.getID()
        self.title = toy.getName()
        self.description = toy.getDesc()
        self.setting = toy.getSetting()
        self.image = self._getSlotImg()
        self.rankIcon = toy.getRankIcon()
        self.isMega = toy.isMega()

    def asSlotViewModel(self):
        slotVM = self._createViewModel()
        with slotVM.transaction() as vm:
            self.fillViewModel(vm)
        return slotVM

    def fillViewModel(self, viewModel):
        viewModel.setToyID(self.id)
        viewModel.setTitle(self.title)
        viewModel.setDescription(self.description)
        viewModel.setDecorationImage(self.image)
        viewModel.setRankImage(self.rankIcon)
        viewModel.setIsMega(self.isMega)

    def _createViewModel(self):
        raise NotImplementedError

    def _getSlotImg(self):
        return self._toy.getIcon()


class PopoverToyPresenter(_ToyPresenterBase):

    def __init__(self, toy, currentToyRank=0):
        super(PopoverToyPresenter, self).__init__(toy)
        self.__currentToyRank = currentToyRank

    def fillViewModel(self, viewModel):
        super(PopoverToyPresenter, self).fillViewModel(viewModel)
        viewModel.setSetting(self.setting)
        viewModel.setIsNew(self._toy.getUnseenCount() > 0 and self._toy.getRank() >= self.__currentToyRank)
        viewModel.setCount(self._toy.getCount())

    def _createViewModel(self):
        return NewYearPopoverDecorationSlotModel()

    def _getSlotImg(self):
        return self._toy.getIcon(size=EXTRA_BIG_AWARD_SIZE if self._toy.isMega() else AWARDS_SIZES.BIG)


class BreakToyPresenter(_ToyPresenterBase):

    def _createViewModel(self):
        return NewYearBreakDecorationSlotModel()


class CraftToyPresenter(_ToyPresenterBase):

    def fillViewModel(self, viewModel):
        super(CraftToyPresenter, self).fillViewModel(viewModel)
        viewModel.setType(ToyTypes.MEGA_COMMON if self.isMega else self._toy.getToyType())

    def _createViewModel(self):
        return NewYearCraftDecorationSlotModel()
