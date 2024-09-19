# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_tankmen_voiceover_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.tankman_model import TankmanModel

class WtEventTankmenVoiceoverViewModel(ViewModel):
    __slots__ = ('showShop', 'close')

    def __init__(self, properties=1, commands=2):
        super(WtEventTankmenVoiceoverViewModel, self).__init__(properties=properties, commands=commands)

    def getTankmen(self):
        return self._getArray(0)

    def setTankmen(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTankmenType():
        return TankmanModel

    def _initialize(self):
        super(WtEventTankmenVoiceoverViewModel, self)._initialize()
        self._addArrayProperty('tankmen', Array())
        self.showShop = self._addCommand('showShop')
        self.close = self._addCommand('close')
