# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/dialogs/research_steps_dialog.py
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.research_steps_main_content import ResearchStepsMainContent
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ResearchStepsDialog(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=3):
        super(ResearchStepsDialog, self).__init__(properties=properties, commands=commands)

    @property
    def dealPanel(self):
        return self._getViewModel(11)

    @staticmethod
    def getDealPanelType():
        return DealPanelModel

    @property
    def mainContent(self):
        return self._getViewModel(12)

    @staticmethod
    def getMainContentType():
        return ResearchStepsMainContent

    def _initialize(self):
        super(ResearchStepsDialog, self)._initialize()
        self._addViewModelProperty('dealPanel', DealPanelModel())
        self._addViewModelProperty('mainContent', ResearchStepsMainContent())
