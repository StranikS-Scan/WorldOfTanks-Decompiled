# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/perks_reset_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_model import DialogTankmanModel

class PerksResetDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=2):
        super(PerksResetDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanBefore(self):
        return self._getViewModel(6)

    @staticmethod
    def getTankmanBeforeType():
        return DialogTankmanModel

    @property
    def tankmanAfter(self):
        return self._getViewModel(7)

    @staticmethod
    def getTankmanAfterType():
        return DialogTankmanModel

    def getTitle(self):
        return self._getString(8)

    def setTitle(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(PerksResetDialogModel, self)._initialize()
        self._addViewModelProperty('tankmanBefore', DialogTankmanModel())
        self._addViewModelProperty('tankmanAfter', DialogTankmanModel())
        self._addStringProperty('title', '')
