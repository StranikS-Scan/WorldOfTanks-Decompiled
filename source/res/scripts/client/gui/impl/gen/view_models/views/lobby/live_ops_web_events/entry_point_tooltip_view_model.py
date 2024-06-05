# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/live_ops_web_events/entry_point_tooltip_view_model.py
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_base import EntryPointBase

class EntryPointTooltipViewModel(EntryPointBase):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EntryPointTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getEventStartDate(self):
        return self._getNumber(2)

    def setEventStartDate(self, value):
        self._setNumber(2, value)

    def getEventEndDate(self):
        return self._getNumber(3)

    def setEventEndDate(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(EntryPointTooltipViewModel, self)._initialize()
        self._addNumberProperty('eventStartDate', 0)
        self._addNumberProperty('eventEndDate', 0)
