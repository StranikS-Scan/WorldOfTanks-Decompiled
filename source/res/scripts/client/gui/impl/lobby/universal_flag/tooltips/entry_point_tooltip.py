# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/universal_flag/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.universal_flag.universal_flag_entry_tooltip_model import UniversalFlagEntryTooltipModel, TimerIconType
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IUniversalFlagEntryPointController
from helpers.time_utils import getServerUTCTime

class EntryPointTooltip(ViewImpl):
    __slots__ = ()
    __universalFlagEntryPointController = dependency.descriptor(IUniversalFlagEntryPointController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.universal_flag.tooltips.EntryPointTooltip())
        settings.model = UniversalFlagEntryTooltipModel()
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            self.__fillInfo(model=model)

    @replaceNoneKwargsModel
    def __fillInfo(self, model=None):
        controller = self.__universalFlagEntryPointController
        model.setTimerIconType(TimerIconType(controller.timerIconType.value))
        model.setTimerTime(controller.timerTime)
        model.setTimerText(controller.timerText)
        model.setTimestamp(getServerUTCTime())
        model.setCaption(controller.eventCaption)
        model.setDescription(controller.eventDescription)
        model.setTooltipBackground(controller.tooltipBackground)
