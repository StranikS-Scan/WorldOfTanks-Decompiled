# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/sub_views/frontline_confirm_title.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sub_views.frontline_confirm_title_model import FrontlineConfirmTitleModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FrontlineConfirmTitle(ViewImpl):
    __slots__ = ('_titleText', '_vehicleType', '_isMultipleReserves', '_selectedSkillName')
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.tanksetup.dialogs.sub_views.FrontlineConfirmTitle

    def __init__(self, titleText, vehicleType, isMultipleReserves=False, selectedSkillName=''):
        settings = ViewSettings(self._LAYOUT_DYN_ACCESSOR())
        settings.model = FrontlineConfirmTitleModel()
        self._titleText = titleText
        self._vehicleType = vehicleType
        self._selectedSkillName = selectedSkillName
        self._isMultipleReserves = isMultipleReserves
        super(FrontlineConfirmTitle, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FrontlineConfirmTitle, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setTitleText(self._titleText)
            vm.setVehicleType(self._vehicleType)
            vm.setSelectedSkillName(self._selectedSkillName)
            vm.setIsMultipleReserves(self._isMultipleReserves)
