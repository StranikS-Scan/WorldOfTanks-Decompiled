# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/catalog_animated_dog_tag_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_dog_tag import DtDogTag

class CatalogAnimatedDogTagTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CatalogAnimatedDogTagTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def equippedDogTag(self):
        return self._getViewModel(0)

    @staticmethod
    def getEquippedDogTagType():
        return DtDogTag

    def getStage(self):
        return self._getNumber(1)

    def setStage(self, value):
        self._setNumber(1, value)

    def getRequiredItemsCount(self):
        return self._getNumber(2)

    def setRequiredItemsCount(self, value):
        self._setNumber(2, value)

    def getItemsLeft(self):
        return self._getNumber(3)

    def setItemsLeft(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CatalogAnimatedDogTagTooltipModel, self)._initialize()
        self._addViewModelProperty('equippedDogTag', DtDogTag())
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('requiredItemsCount', 0)
        self._addNumberProperty('itemsLeft', 0)
