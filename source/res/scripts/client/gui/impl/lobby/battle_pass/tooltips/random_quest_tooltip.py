# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/random_quest_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.random_quest_tooltip_model import RandomQuestTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import first
from tutorial.control.game_vars import getVehicleByIntCD
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest

class RandomQuestTooltip(ViewImpl):
    __slots__ = ('__quest',)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, requiredToken):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.RandomQuestTooltip())
        settings.model = RandomQuestTooltipModel()
        super(RandomQuestTooltip, self).__init__(settings)
        self.__quest = first(self.__eventsCache.getQuestsByTokenRequirement(requiredToken))

    @property
    def viewModel(self):
        return super(RandomQuestTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RandomQuestTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setExpireTime(self.__quest.getFinishTime())
            model.setCondition(self.__quest.getDescription())
            model.setVehicleName(self._getQuestVehicleReqs().shortUserName)

    def _getQuestVehicleReqs(self):
        vehicleTypeCD = self.__quest.vehicleReqs.getAvailableVehicleCD()
        return getVehicleByIntCD(int(vehicleTypeCD))
