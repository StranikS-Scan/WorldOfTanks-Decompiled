# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/sub_views/frontline_confirm_info.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sub_views.frontline_confirm_info_model import FrontlineConfirmInfoModel
from gui.impl.pub import ViewImpl

class FrontlineConfirmInfo(ViewImpl):
    __slots__ = ('_bonus',)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.tanksetup.dialogs.sub_views.FrontlineConfirmInfo

    def __init__(self, bonus):
        settings = ViewSettings(self._LAYOUT_DYN_ACCESSOR())
        settings.model = FrontlineConfirmInfoModel()
        self._bonus = bonus
        super(FrontlineConfirmInfo, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FrontlineConfirmInfo, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setBonus(self._bonus)
