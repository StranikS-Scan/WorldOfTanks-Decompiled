# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/common/fun_random_mode_state_model.py
from gui.impl.gen.view_models.views.lobby.hangar.mode_state_model import ModeStateModel

class FunRandomModeStateModel(ModeStateModel):
    __slots__ = ()
    MODE_ID = 'fun_random'

    def __init__(self, properties=3, commands=0):
        super(FunRandomModeStateModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(1)

    def setAssetsPointer(self, value):
        self._setString(1, value)

    def getSubModeAssetsPointer(self):
        return self._getString(2)

    def setSubModeAssetsPointer(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(FunRandomModeStateModel, self)._initialize()
        self._addStringProperty('assetsPointer', 'undefined')
        self._addStringProperty('subModeAssetsPointer', 'undefined')
