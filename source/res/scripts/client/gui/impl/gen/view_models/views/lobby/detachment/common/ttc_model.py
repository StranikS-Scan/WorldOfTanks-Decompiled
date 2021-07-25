# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/ttc_model.py
from frameworks.wulf import ViewModel

class TtcModel(ViewModel):
    __slots__ = ('updateTTCPosition',)

    def __init__(self, properties=0, commands=1):
        super(TtcModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TtcModel, self)._initialize()
        self.updateTTCPosition = self._addCommand('updateTTCPosition')
