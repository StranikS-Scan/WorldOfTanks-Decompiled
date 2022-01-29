# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/select_charm_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel

class SelectCharmViewModel(ViewModel):
    __slots__ = ('onSelectCharm', 'goToSendEnvelopes')

    def __init__(self, properties=3, commands=2):
        super(SelectCharmViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    def getAvailableCharmsCount(self):
        return self._getNumber(1)

    def setAvailableCharmsCount(self, value):
        self._setNumber(1, value)

    def getCharms(self):
        return self._getArray(2)

    def setCharms(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(SelectCharmViewModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addNumberProperty('availableCharmsCount', 0)
        self._addArrayProperty('charms', Array())
        self.onSelectCharm = self._addCommand('onSelectCharm')
        self.goToSendEnvelopes = self._addCommand('goToSendEnvelopes')
