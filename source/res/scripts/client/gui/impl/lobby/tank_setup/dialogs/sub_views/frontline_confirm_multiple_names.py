# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/sub_views/frontline_confirm_multiple_names.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sub_views.frontline_confirm_multiple_names_model import FrontlineConfirmMultipleNamesModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FrontlineConfirmMultipleNames(ViewImpl):
    __slots__ = ('_names',)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.tanksetup.dialogs.sub_views.FrontlineConfirmMultipleNames

    def __init__(self):
        settings = ViewSettings(self._LAYOUT_DYN_ACCESSOR())
        settings.model = FrontlineConfirmMultipleNamesModel()
        self._names = []
        super(FrontlineConfirmMultipleNames, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FrontlineConfirmMultipleNames, self).getViewModel()

    def addName(self, name):
        self._names.append(name)

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            names = vm.getNames()
            names.clear()
            for name in self._names:
                names.addString(name)
