# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_entry_widget_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearEntryWidgetModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def getLevelIconDefaultSrc(self):
        return self._getResource(0)

    def setLevelIconDefaultSrc(self, value):
        self._setResource(0, value)

    def getLevelIconSmallSrc(self):
        return self._getResource(1)

    def setLevelIconSmallSrc(self, value):
        self._setResource(1, value)

    def getTankName(self):
        return self._getString(2)

    def setTankName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearEntryWidgetModel, self)._initialize()
        self._addResourceProperty('levelIconDefaultSrc', Resource.INVALID)
        self._addResourceProperty('levelIconSmallSrc', Resource.INVALID)
        self._addStringProperty('tankName', '')
        self.onWidgetClick = self._addCommand('onWidgetClick')
