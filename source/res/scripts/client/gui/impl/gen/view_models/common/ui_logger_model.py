# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/ui_logger_model.py
from frameworks.wulf import ViewModel

class UiLoggerModel(ViewModel):
    __slots__ = ('log',)

    def __init__(self, properties=0, commands=1):
        super(UiLoggerModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(UiLoggerModel, self)._initialize()
        self.log = self._addCommand('log')
