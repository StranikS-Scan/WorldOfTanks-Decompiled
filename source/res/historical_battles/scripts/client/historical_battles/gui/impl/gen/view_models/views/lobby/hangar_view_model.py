# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from historical_battles.gui.impl.gen.view_models.views.common.selectable_view_model import SelectableViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_progresive_model import QuestProgresiveModel

class HangarViewModel(SelectableViewModel):
    __slots__ = ('onFrontmanChanged', 'onEscapePressed', 'onInfoClick', 'onCloseClick', 'onMousePressed', 'onVehicleChange')

    def __init__(self, properties=3, commands=8):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progress(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressType():
        return QuestProgresiveModel

    def getBanExpirationTime(self):
        return self._getNumber(1)

    def setBanExpirationTime(self, value):
        self._setNumber(1, value)

    def getSelectedFrontmanId(self):
        return self._getNumber(2)

    def setSelectedFrontmanId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('progress', QuestProgresiveModel())
        self._addNumberProperty('banExpirationTime', 0)
        self._addNumberProperty('selectedFrontmanId', 0)
        self.onFrontmanChanged = self._addCommand('onFrontmanChanged')
        self.onEscapePressed = self._addCommand('onEscapePressed')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onMousePressed = self._addCommand('onMousePressed')
        self.onVehicleChange = self._addCommand('onVehicleChange')
