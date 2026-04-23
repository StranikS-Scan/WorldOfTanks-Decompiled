# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/help_hint_model.py
from frameworks.wulf import ViewModel

class HelpHintModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HelpHintModel, self).__init__(properties=properties, commands=commands)

    def getBackground(self):
        return self._getString(0)

    def setBackground(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(HelpHintModel, self)._initialize()
        self._addStringProperty('background', '')
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
