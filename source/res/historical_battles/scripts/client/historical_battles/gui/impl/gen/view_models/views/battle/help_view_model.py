# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/battle/help_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.help_hint_model import HelpHintModel

class HelpViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HelpViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getHints(self):
        return self._getArray(1)

    def setHints(self, value):
        self._setArray(1, value)

    @staticmethod
    def getHintsType():
        return HelpHintModel

    def _initialize(self):
        super(HelpViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('hints', Array())
