# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/toy_presenter.py
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.new_year.components.new_year_break_decoration_slot_model import NewYearBreakDecorationSlotModel
from gui.impl.gen.view_models.new_year.components.new_year_craft_decoration_slot_model import NewYearCraftDecorationSlotModel
from gui.impl.gen.view_models.new_year.components.new_year_popover_decoration_slot_model import NewYearPopoverDecorationSlotModel
RANK_TO_COLOR_IMG = {1: R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.red,
 2: R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.yellow,
 3: R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.green,
 4: R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.blue,
 5: R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.violet}

class _ToyPresenterBase(object):

    def __init__(self, toy):
        self._toy = toy
        self.id = toy.getID()
        self.title = toy.getName()
        self.description = toy.getDesc()
        self.setting = toy.getSetting()
        self.image = self.__getSlotImg()

    def getRankImage(self):
        return RANK_TO_COLOR_IMG[self._toy.getRank()]

    def asSlotModel(self, idx=None):
        slot = self._createModel()
        if idx is not None:
            slot.setIdx(idx)
        slot.setToyID(self.id)
        slot.setTitle(self.title)
        slot.setDescription(self.description)
        slot.setDecorationImage(self.image)
        slot.setRankImage(self.getRankImage())
        return slot

    def _createModel(self):
        return None

    def __getSlotImg(self):
        return self._toy.getIcon()


class PopoverToyPresenter(_ToyPresenterBase):

    def asSlotModel(self, idx=None, currentToyRank=0):
        model = super(PopoverToyPresenter, self).asSlotModel(idx)
        model.setSetting(self.setting)
        model.setIsNew(self._toy.getUnseenCount() > 0 and self._toy.getRank() >= currentToyRank)
        return model

    def _createModel(self):
        return NewYearPopoverDecorationSlotModel()


class BreakToyPresenter(_ToyPresenterBase):

    def _createModel(self):
        return NewYearBreakDecorationSlotModel()


class CraftToyPresenter(_ToyPresenterBase):

    def _createModel(self):
        return NewYearCraftDecorationSlotModel()
