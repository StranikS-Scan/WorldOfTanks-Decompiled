# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/event_entry_point_view_model.py
from story_mode.gui.impl.gen.view_models.views.lobby.entry_point_view_model import EntryPointViewModel

class EventEntryPointViewModel(EntryPointViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=3):
        super(EventEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(4)

    def setStartDate(self, value):
        self._setNumber(4, value)

    def getEndDate(self):
        return self._getNumber(5)

    def setEndDate(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(EventEntryPointViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
