# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_collection_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.collection_item_model import CollectionItemModel
from gui.impl.gen.view_models.views.lobby.wt_event.progression_item_model import ProgressionItemModel

class WtEventCollectionViewModel(ViewModel):
    __slots__ = ('onInfoPageOpen', 'onProgressBarAnimation')

    def __init__(self, properties=11, commands=2):
        super(WtEventCollectionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bossCollection(self):
        return self._getViewModel(0)

    @property
    def hunterCollection(self):
        return self._getViewModel(1)

    @property
    def progression(self):
        return self._getViewModel(2)

    def getDaysLeft(self):
        return self._getString(3)

    def setDaysLeft(self, value):
        self._setString(3, value)

    def getPreviousCommon(self):
        return self._getNumber(4)

    def setPreviousCommon(self, value):
        self._setNumber(4, value)

    def getCommonCurrent(self):
        return self._getNumber(5)

    def setCommonCurrent(self, value):
        self._setNumber(5, value)

    def getCommonTotal(self):
        return self._getNumber(6)

    def setCommonTotal(self, value):
        self._setNumber(6, value)

    def getBossCurrent(self):
        return self._getNumber(7)

    def setBossCurrent(self, value):
        self._setNumber(7, value)

    def getBossTotal(self):
        return self._getNumber(8)

    def setBossTotal(self, value):
        self._setNumber(8, value)

    def getHunterCurrent(self):
        return self._getNumber(9)

    def setHunterCurrent(self, value):
        self._setNumber(9, value)

    def getHunterTotal(self):
        return self._getNumber(10)

    def setHunterTotal(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(WtEventCollectionViewModel, self)._initialize()
        self._addViewModelProperty('bossCollection', UserListModel())
        self._addViewModelProperty('hunterCollection', UserListModel())
        self._addViewModelProperty('progression', UserListModel())
        self._addStringProperty('daysLeft', '')
        self._addNumberProperty('previousCommon', 0)
        self._addNumberProperty('commonCurrent', 0)
        self._addNumberProperty('commonTotal', 0)
        self._addNumberProperty('bossCurrent', 0)
        self._addNumberProperty('bossTotal', 0)
        self._addNumberProperty('hunterCurrent', 0)
        self._addNumberProperty('hunterTotal', 0)
        self.onInfoPageOpen = self._addCommand('onInfoPageOpen')
        self.onProgressBarAnimation = self._addCommand('onProgressBarAnimation')