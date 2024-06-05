# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/animated_dog_tags_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.animated_dog_tag_component import AnimatedDogTagComponent

class AnimatedDogTagsViewModel(ViewModel):
    __slots__ = ('onEquip', 'onGoToAchievement', 'onInfoButtonClick', 'onPlayVideo', 'onOnboardingCloseClick', 'onHideNewBubble', 'onClose')

    def __init__(self, properties=3, commands=7):
        super(AnimatedDogTagsViewModel, self).__init__(properties=properties, commands=commands)

    def getDogTags(self):
        return self._getArray(0)

    def setDogTags(self, value):
        self._setArray(0, value)

    @staticmethod
    def getDogTagsType():
        return AnimatedDogTagComponent

    def getOnboardingEnabled(self):
        return self._getBool(1)

    def setOnboardingEnabled(self, value):
        self._setBool(1, value)

    def getInitialIndex(self):
        return self._getNumber(2)

    def setInitialIndex(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(AnimatedDogTagsViewModel, self)._initialize()
        self._addArrayProperty('dogTags', Array())
        self._addBoolProperty('onboardingEnabled', False)
        self._addNumberProperty('initialIndex', 0)
        self.onEquip = self._addCommand('onEquip')
        self.onGoToAchievement = self._addCommand('onGoToAchievement')
        self.onInfoButtonClick = self._addCommand('onInfoButtonClick')
        self.onPlayVideo = self._addCommand('onPlayVideo')
        self.onOnboardingCloseClick = self._addCommand('onOnboardingCloseClick')
        self.onHideNewBubble = self._addCommand('onHideNewBubble')
        self.onClose = self._addCommand('onClose')
