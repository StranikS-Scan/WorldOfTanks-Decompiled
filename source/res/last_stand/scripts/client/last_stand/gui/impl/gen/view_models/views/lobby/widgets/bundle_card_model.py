# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/bundle_card_model.py
from frameworks.wulf import ViewModel

class BundleCardModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(BundleCardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getDescriptionKey(self):
        return self._getString(1)

    def setDescriptionKey(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BundleCardModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('descriptionKey', '')
        self.onClick = self._addCommand('onClick')
