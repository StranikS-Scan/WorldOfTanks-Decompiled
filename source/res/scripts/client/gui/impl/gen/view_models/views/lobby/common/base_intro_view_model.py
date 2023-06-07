# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/base_intro_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel

class BaseIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideo', 'onViewLoaded')

    def __init__(self, properties=5, commands=3):
        super(BaseIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getIsVideoExist(self):
        return self._getBool(0)

    def setIsVideoExist(self, value):
        self._setBool(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getAbout(self):
        return self._getResource(2)

    def setAbout(self, value):
        self._setResource(2, value)

    def getButtonLabel(self):
        return self._getResource(3)

    def setButtonLabel(self, value):
        self._setResource(3, value)

    def getSlides(self):
        return self._getArray(4)

    def setSlides(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSlidesType():
        return IntroSlideModel

    def _initialize(self):
        super(BaseIntroViewModel, self)._initialize()
        self._addBoolProperty('isVideoExist', True)
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('about', R.invalid())
        self._addResourceProperty('buttonLabel', R.invalid())
        self._addArrayProperty('slides', Array())
        self.onClose = self._addCommand('onClose')
        self.onVideo = self._addCommand('onVideo')
        self.onViewLoaded = self._addCommand('onViewLoaded')
