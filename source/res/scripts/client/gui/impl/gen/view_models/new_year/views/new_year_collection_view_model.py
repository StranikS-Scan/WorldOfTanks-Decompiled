# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_collection_view_model.py
from frameworks.wulf import ViewModel

class NewYearCollectionViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick',)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(NewYearCollectionViewModel, self)._initialize()
        self._addStringProperty('title', 'collection view')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
