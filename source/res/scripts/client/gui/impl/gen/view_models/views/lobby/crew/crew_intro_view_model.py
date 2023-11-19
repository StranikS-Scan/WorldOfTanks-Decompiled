# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_intro_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CrewIntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(CrewIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getScreenName(self):
        return self._getString(0)

    def setScreenName(self, value):
        self._setString(0, value)

    def getSlides(self):
        return self._getArray(1)

    def setSlides(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSlidesType():
        return int

    def _initialize(self):
        super(CrewIntroViewModel, self)._initialize()
        self._addStringProperty('screenName', '')
        self._addArrayProperty('slides', Array())
        self.onClose = self._addCommand('onClose')
