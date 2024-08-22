# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/perks_reset_dialog_model.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.tankman_skills_change_base_dialog_model import TankmanSkillsChangeBaseDialogModel

class PerksResetDialogModel(TankmanSkillsChangeBaseDialogModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=2):
        super(PerksResetDialogModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(8)

    def setTitle(self, value):
        self._setString(8, value)

    def getResetGracePeriodLeft(self):
        return self._getNumber(9)

    def setResetGracePeriodLeft(self, value):
        self._setNumber(9, value)

    def getHasFreeFirstReset(self):
        return self._getBool(10)

    def setHasFreeFirstReset(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(PerksResetDialogModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('resetGracePeriodLeft', 0)
        self._addBoolProperty('hasFreeFirstReset', False)
