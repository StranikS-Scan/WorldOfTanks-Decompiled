# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/complete_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_overlay_view_model import BaseOverlayViewModel

class CompleteModel(BaseOverlayViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=2):
        super(CompleteModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getSubTitle(self):
        return self._getResource(3)

    def setSubTitle(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(CompleteModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
