# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_state_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_state_tooltip_model import NyDecorationStateTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class NyDecorationStateTooltip(ViewImpl):
    __slots__ = ('__atmosphereBonus',)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, atmosphereBonus, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDecorationStateTooltip())
        settings.model = NyDecorationStateTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__atmosphereBonus = atmosphereBonus
        super(NyDecorationStateTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyDecorationStateTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setAtmosphereBonus(self.__atmosphereBonus)
            model.setDescription(backport.text(R.strings.ny.atmosphereBonus.tooltip.description()))
