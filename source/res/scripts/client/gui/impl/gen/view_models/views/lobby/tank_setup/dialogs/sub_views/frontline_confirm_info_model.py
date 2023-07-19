# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/sub_views/frontline_confirm_info_model.py
from frameworks.wulf import ViewModel

class FrontlineConfirmInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FrontlineConfirmInfoModel, self).__init__(properties=properties, commands=commands)

    def getBonus(self):
        return self._getNumber(0)

    def setBonus(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(FrontlineConfirmInfoModel, self)._initialize()
        self._addNumberProperty('bonus', 0)
