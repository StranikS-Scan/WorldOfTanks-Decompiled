# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/tooltips/mission_progress_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.tooltips.mission_progress_tooltip_model import MissionProgressTooltipModel
from gui.impl.lobby.personal_missions_30.views_helpers import getMissionConfigData
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.lobby.personal_missions_30.views_helpers import ConditionsConfig
    from gui.server_events.event_items import PersonalMission

class MissionProgressTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, mission):
        settings = ViewSettings(layoutID=R.views.mono.personal_missions_30.tooltips.mission_progress_tooltip(), model=MissionProgressTooltipModel())
        super(MissionProgressTooltip, self).__init__(settings)
        self.__mission = mission

    @property
    def viewModel(self):
        return super(MissionProgressTooltip, self).getViewModel()

    def _onLoading(self):
        with self.viewModel.transaction() as tx:
            questConfig = getMissionConfigData(self.__mission)
            totalMissionsAmount = questConfig.maxProgressValue
            tx.setTotalMissionsAmount(totalMissionsAmount)
            battlesUniqueVehicles = sorted(self.__mission.getConditionsProgress().get('battlesUniqueVehicles', set()))
            tx.setCompletedMissionsAmount(totalMissionsAmount if self.__mission.isCompleted() else len(battlesUniqueVehicles))
            vehicleNames = [ self.__itemsCache.items.getItemByCD(vehCD).shortUserName for vehCD in battlesUniqueVehicles ]
            fillStringsArray(vehicleNames, tx.getVehicles())
