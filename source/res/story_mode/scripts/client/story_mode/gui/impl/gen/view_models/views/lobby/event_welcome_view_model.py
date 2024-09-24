# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/event_welcome_view_model.py
from story_mode.gui.impl.gen.view_models.views.lobby.advertising_view_model import AdvertisingViewModel

class EventWelcomeViewModel(AdvertisingViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=2):
        super(EventWelcomeViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(EventWelcomeViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
