# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/dog_tags_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tag_model import DogTagModel

class DogTagsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DogTagsModel, self).__init__(properties=properties, commands=commands)

    @property
    def customizableDogTag(self):
        return self._getViewModel(0)

    @staticmethod
    def getCustomizableDogTagType():
        return DogTagModel

    @property
    def animatedDogTag(self):
        return self._getViewModel(1)

    @staticmethod
    def getAnimatedDogTagType():
        return DogTagModel

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(DogTagsModel, self)._initialize()
        self._addViewModelProperty('customizableDogTag', DogTagModel())
        self._addViewModelProperty('animatedDogTag', DogTagModel())
        self._addBoolProperty('isEnabled', True)
