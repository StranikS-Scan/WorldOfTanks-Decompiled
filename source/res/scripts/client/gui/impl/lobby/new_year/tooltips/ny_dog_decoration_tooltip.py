# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_dog_decoration_tooltip.py
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_dog_decoration_tooltip_model import NyDogDecorationTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import time_utils
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_sacks_helper import getNYDogConfig
from new_year.ny_toy_info import NewYearCurrentToyInfo

class NyDogDecorationTooltip(ViewImpl):
    __slots__ = ('__toyID', '__state')

    def __init__(self, toyID, state, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDogDecorationTooltip())
        settings.model = NyDogDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__toyID = int(toyID)
        self.__state = state
        super(NyDogDecorationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyDogDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = NewYearCurrentToyInfo(self.__toyID)
        timeTillEndEvent = int(getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime())
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setType(toy.getToyType())
            model.setIcon(toy.getIcon(size='large'))
            model.setDescription(toy.getDesc())
            model.setTimeTill(timeTillEndEvent)
            model.setState(self.__state)
            model.setSackRequiredLevel(self.__getSackRequiredLevel())

    def __getSackRequiredLevel(self):
        level = 1
        for level, tier in enumerate(getNYDogConfig().getLevels()):
            toys = [ toyInfo[0] for toyInfo in tier['toys'] ]
            if self.__toyID in toys:
                break

        return level
