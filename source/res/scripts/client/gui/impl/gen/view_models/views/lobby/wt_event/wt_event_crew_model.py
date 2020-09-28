# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_crew_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.crew_member_model import CrewMemberModel

class WtEventCrewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventCrewModel, self).__init__(properties=properties, commands=commands)

    @property
    def crew(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(WtEventCrewModel, self)._initialize()
        self._addViewModelProperty('crew', UserListModel())
