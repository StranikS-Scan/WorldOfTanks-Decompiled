# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/tooltip/platoon_event_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.platoon.event_difficulty_model import EventDifficultyModel

class EventTooltip(ViewImpl):

    def __init__(self, level, header='', body=''):
        self.__header = header
        self.__body = body
        self.__level = level
        settings = ViewSettings(R.views.lobby.platoon.EventTooltips(), model=EventDifficultyModel())
        super(EventTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setTooltipDifficultyHeader(self.__header)
            model.setTooltipDifficulty(self.__body)
            model.setLevel(self.__level)
