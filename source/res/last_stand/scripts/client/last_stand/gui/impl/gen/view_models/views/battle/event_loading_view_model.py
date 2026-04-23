# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/battle/event_loading_view_model.py
from frameworks.wulf import ViewModel

class EventLoadingViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EventLoadingViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(EventLoadingViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
