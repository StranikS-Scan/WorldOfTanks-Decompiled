# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/meta_intro_view_model.py
from frameworks.wulf import ViewModel

class MetaIntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(MetaIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MetaIntroViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('name', '')
        self.onClose = self._addCommand('onClose')
