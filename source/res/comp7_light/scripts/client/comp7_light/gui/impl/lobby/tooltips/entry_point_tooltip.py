# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/tooltips/entry_point_tooltip.py
from comp7_core.gui.impl.lobby.tooltips.entry_point_tooltip import Comp7CoreEntryPointTooltip
from comp7_light.gui.impl.gen.view_models.views.lobby.enums import SeasonName as Comp7LightSeasonName
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonState as Comp7LightSeasonState
from comp7_light.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_tooltip_model import EntryPointTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightEntryPointTooltip(Comp7CoreEntryPointTooltip):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        settings = ViewSettings(R.views.comp7_light.mono.lobby.entry_point_tooltip())
        settings.model = EntryPointTooltipModel()
        super(Comp7LightEntryPointTooltip, self).__init__(settings)

    @property
    def _modeController(self):
        return self.__comp7LightController

    @property
    def _seasonStateClazz(self):
        return Comp7LightSeasonState

    @property
    def _seasonNameClazz(self):
        return Comp7LightSeasonName
