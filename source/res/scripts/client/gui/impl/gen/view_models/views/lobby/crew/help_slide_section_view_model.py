# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/help_slide_section_view_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SlideSectionSize(Enum):
    SMALL = 'small'
    BIG = 'big'


class HelpSlideSectionViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HelpSlideSectionViewModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getSize(self):
        return SlideSectionSize(self._getString(2))

    def setSize(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(HelpSlideSectionViewModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('size')
