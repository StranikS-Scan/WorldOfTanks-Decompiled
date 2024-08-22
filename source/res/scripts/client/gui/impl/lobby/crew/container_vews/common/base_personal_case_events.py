# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/common/base_personal_case_events.py
from gui.impl.lobby.container_views.base.events import ComponentEventsBase

class BasePersonalCaseComponentViewEvents(ComponentEventsBase):

    def __init__(self):
        super(BasePersonalCaseComponentViewEvents, self).__init__()
        self.onChangeVehicleClick = self._createEvent()
        self.onRetrainClick = self._createEvent()
