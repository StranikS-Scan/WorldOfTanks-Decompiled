# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/renaming_model.py
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_wgnp_overlay_view_model import BaseWgnpOverlayViewModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_name_model import FieldNameModel

class RenamingModel(BaseWgnpOverlayViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=4):
        super(RenamingModel, self).__init__(properties=properties, commands=commands)

    @property
    def name(self):
        return self._getViewModel(9)

    @staticmethod
    def getNameType():
        return FieldNameModel

    def _initialize(self):
        super(RenamingModel, self)._initialize()
        self._addViewModelProperty('name', FieldNameModel())
