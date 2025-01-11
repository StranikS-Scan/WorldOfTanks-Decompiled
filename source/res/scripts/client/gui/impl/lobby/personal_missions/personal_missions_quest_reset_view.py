# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_quest_reset_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_quest_reset_view_model import PersonalMissionsQuestResetViewModel
from gui.impl.pub import ViewImpl, WindowImpl

class PersonalMissionsQuestResetView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PersonalMissionsQuestResetViewModel()
        super(PersonalMissionsQuestResetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsQuestResetView, self).getViewModel()


class PersonalMissionsQuestResetWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PersonalMissionsQuestResetWindow, self).__init__(WindowFlags.WINDOW, content=PersonalMissionsQuestResetView(R.views.lobby.personal_missions.PersonalMissionsQuestResetView()), parent=parent)
