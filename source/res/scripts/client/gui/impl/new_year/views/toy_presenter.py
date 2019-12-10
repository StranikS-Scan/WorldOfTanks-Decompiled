# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/toy_presenter.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_break_decoration_slot_model import NewYearBreakDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_craft_decoration_slot_model import NewYearCraftDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_popover_decoration_slot_model import NewYearPopoverDecorationSlotModel
from items.components.ny_constants import ToyTypes

class _ToyPresenterBase(object):

    def __init__(self, toy):
        self._toy = toy
        self.id = toy.getID()
        self.title = toy.getName()
        self.description = toy.getDesc()
        self.setting = toy.getSetting()
        self.image = self.__getSlotImg()
        self.rankIcon = toy.getRankIcon()
        self.isMega = toy.isMega()

    def asSlotModel(self):
        slot = self._createModel()
        self.fillSlotModel(slot)
        return slot

    def fillSlotModel(self, slotModel):
        slotModel.setToyID(self.id)
        slotModel.setTitle(self.title)
        slotModel.setDescription(self.description)
        slotModel.setDecorationImage(self.image)
        slotModel.setRankImage(self.rankIcon)
        slotModel.setIsMega(self.isMega)

    def _createModel(self):
        raise NotImplementedError

    def __getSlotImg(self):
        return self._toy.getIcon()


class PopoverToyPresenter(_ToyPresenterBase):

    def __init__(self, toy, currentToyRank=0):
        super(PopoverToyPresenter, self).__init__(toy)
        self.__currentToyRank = currentToyRank

    def fillSlotModel(self, slotModel):
        super(PopoverToyPresenter, self).fillSlotModel(slotModel)
        slotModel.setSetting(self.setting)
        slotModel.setIsNew(self._toy.getUnseenCount() > 0 and self._toy.getRank() >= self.__currentToyRank)
        slotModel.setCount(self._toy.getCount())

    def _createModel(self):
        return NewYearPopoverDecorationSlotModel()


class BreakToyPresenter(_ToyPresenterBase):

    def _createModel(self):
        return NewYearBreakDecorationSlotModel()


class CraftToyPresenter(_ToyPresenterBase):

    def fillSlotModel(self, slotModel):
        super(CraftToyPresenter, self).fillSlotModel(slotModel)
        slotModel.setType(ToyTypes.MEGA_COMMON if self.isMega else self._toy.getToyType())

    def _createModel(self):
        return NewYearCraftDecorationSlotModel()
