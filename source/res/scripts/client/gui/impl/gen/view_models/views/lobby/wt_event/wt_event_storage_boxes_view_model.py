# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_storage_boxes_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.box_card_model import BoxCardModel

class WtEventStorageBoxesViewModel(ViewModel):
    __slots__ = ('onAwardOpen', 'onBuySpecialBox', 'onToEvent', 'onToMissions')

    def __init__(self, properties=4, commands=4):
        super(WtEventStorageBoxesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def boxCards(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getIsEnterFromHangar(self):
        return self._getBool(2)

    def setIsEnterFromHangar(self, value):
        self._setBool(2, value)

    def getIsLootBoxEnabled(self):
        return self._getBool(3)

    def setIsLootBoxEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtEventStorageBoxesViewModel, self)._initialize()
        self._addViewModelProperty('boxCards', UserListModel())
        self._addStringProperty('title', '')
        self._addBoolProperty('isEnterFromHangar', False)
        self._addBoolProperty('isLootBoxEnabled', False)
        self.onAwardOpen = self._addCommand('onAwardOpen')
        self.onBuySpecialBox = self._addCommand('onBuySpecialBox')
        self.onToEvent = self._addCommand('onToEvent')
        self.onToMissions = self._addCommand('onToMissions')
