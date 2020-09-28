# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_postbattle_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.event_task_model import EventTaskModel

class WtEventPostbattleViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventPostbattleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventTasks(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(WtEventPostbattleViewModel, self)._initialize()
        self._addViewModelProperty('eventTasks', UserListModel())
