# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/rts/help_actions_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class HelpActionsItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(HelpActionsItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getAction(self):
        return self._getResource(1)

    def setAction(self, value):
        self._setResource(1, value)

    def getKeyHint(self):
        return self._getString(2)

    def setKeyHint(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getResource(3)

    def setDescription(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(HelpActionsItemModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('action', R.invalid())
        self._addStringProperty('keyHint', '')
        self._addResourceProperty('description', R.invalid())
