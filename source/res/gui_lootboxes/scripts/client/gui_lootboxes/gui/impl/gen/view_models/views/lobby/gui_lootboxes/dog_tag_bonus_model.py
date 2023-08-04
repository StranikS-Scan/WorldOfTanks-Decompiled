# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/dog_tag_bonus_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class DogTagType(IntEnum):
    ENGRAVING = 0
    BACKGROUND = 1


class DogTagBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(DogTagBonusModel, self).__init__(properties=properties, commands=commands)

    def getDogTagType(self):
        return DogTagType(self._getNumber(8))

    def setDogTagType(self, value):
        self._setNumber(8, value.value)

    def _initialize(self):
        super(DogTagBonusModel, self)._initialize()
        self._addNumberProperty('dogTagType')
