# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/vehicle_parameters.py
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.shared.tooltips import ToolTipBaseData

class VehicleParametersAdvanced(ToolTipBaseData):
    _movies = {'relativePower': 'statFirepower',
     'relativeArmor': 'statSurvivability',
     'relativeMobility': 'statMobility',
     'relativeCamouflage': 'statConcealment',
     'relativeVisibility': 'statSpotting',
     'relativeAbility': 'abilityPreview'}

    def __init__(self, context):
        super(VehicleParametersAdvanced, self).__init__(context, None)
        return

    def getDisplayableData(self, paramName, *args, **kwargs):
        from gui.impl.lobby.crew.tooltips.advanced_tooltip_view import AdvancedTooltipView
        return DecoratedTooltipWindow(AdvancedTooltipView(self._movies[paramName], backport.text(R.strings.menu.tank_params.dyn(paramName)()), backport.text(R.strings.tooltips.advanced.dyn(paramName)())), useDecorator=False)
