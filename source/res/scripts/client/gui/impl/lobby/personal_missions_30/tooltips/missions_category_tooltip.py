# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/tooltips/missions_category_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.tooltips.missions_category_tooltip_model import MissionsCategoryTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import PMOperation
    from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory

class MissionsCategoryTooltip(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, category, operation):
        settings = ViewSettings(R.views.mono.personal_missions_30.tooltips.missions_category_tooltip(), model=MissionsCategoryTooltipModel())
        self.__category = category
        self.__operation = operation
        super(MissionsCategoryTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MissionsCategoryTooltip, self).getViewModel()

    def _onLoading(self):
        minLevel, maxLevel = self.__eventsCache.getPersonalMissions().getVehicleLevelRestrictions(self.__operation.getID())
        with self.viewModel.transaction() as vm:
            vm.setCategory(self.__category)
            vm.setOperationName(self.__operation.getShortUserName())
            vm.setMinLevel(minLevel)
            vm.setMaxLevel(maxLevel)
