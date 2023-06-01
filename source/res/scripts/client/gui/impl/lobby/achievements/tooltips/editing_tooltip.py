# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/tooltips/editing_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.achievements.tooltips.editing_tooltip_view_model import EditingTooltipViewModel, TooltipType
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class EditingTooltip(ViewImpl):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, tooltipType):
        settings = ViewSettings(R.views.lobby.achievements.tooltips.EditingTooltip(), model=EditingTooltipViewModel())
        self.__tooltipType = tooltipType
        super(EditingTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EditingTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EditingTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setTooltipType(self.__getTooltipType())
            model.setRequiredAchievementsCount(self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig().getLayoutLength() + 1)

    def _finalize(self):
        self.__tooltipType = None
        super(EditingTooltip, self)._finalize()
        return

    def __getTooltipType(self):
        if TooltipType.NOT_ENOUGH_ACHIEVEMENTS.value == self.__tooltipType:
            return TooltipType.NOT_ENOUGH_ACHIEVEMENTS
        if TooltipType.DISABLED.value == self.__tooltipType:
            return TooltipType.DISABLED
        if TooltipType.DISABLED_LAYOUT.value == self.__tooltipType:
            return TooltipType.DISABLED_LAYOUT
        return TooltipType.OTHER_PLAYER if TooltipType.OTHER_PLAYER.value == self.__tooltipType else None
