# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_vehicles_bonus_tooltip.py
from frameworks.wulf import View, ViewSettings, ViewModel
from gui.impl.gen import R

class NewYearVehiclesBonusTooltip(View):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_vehicle_bonus.NewYearVehiclesBonus())
        settings.model = ViewModel()
        super(NewYearVehiclesBonusTooltip, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(NewYearVehiclesBonusTooltip, self)._initialize()
