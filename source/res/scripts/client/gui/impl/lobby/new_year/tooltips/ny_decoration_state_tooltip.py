# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_state_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_state_tooltip_model import NyDecorationStateTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from items.components.ny_constants import TOY_SLOT_USAGE

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
        config = self.__lobbyCtx.getServerSettings().getNewYearGeneralConfig()
        if self.__atmosphereBonus == config.getAtmPointsConfigValue(isMega=True, toyUsage=TOY_SLOT_USAGE.PURE, slotUsage=TOY_SLOT_USAGE.PURE):
            descriptionRes = R.strings.ny.atmosphereBonus.tooltip.unusedMega
        elif self.__atmosphereBonus == config.getAtmPointsConfigValue(isMega=False, toyUsage=TOY_SLOT_USAGE.PURE, slotUsage=TOY_SLOT_USAGE.PURE):
            descriptionRes = R.strings.ny.atmosphereBonus.tooltip.unused
        else:
            descriptionRes = R.strings.ny.atmosphereBonus.tooltip.used
        with self.viewModel.transaction() as model:
            model.setAtmosphereBonus(self.__atmosphereBonus)
            model.setDescription(backport.text(descriptionRes()))
