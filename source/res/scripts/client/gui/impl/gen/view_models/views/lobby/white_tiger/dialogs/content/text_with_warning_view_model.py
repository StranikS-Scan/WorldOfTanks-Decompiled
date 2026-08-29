# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/white_tiger/dialogs/content/text_with_warning_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.image_substitution_view_model import ImageSubstitutionViewModel

class TextWithWarningViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TextWithWarningViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def warningImageSubstitution(self):
        return self._getViewModel(0)

    @staticmethod
    def getWarningImageSubstitutionType():
        return ImageSubstitutionViewModel

    def getMainText(self):
        return self._getString(1)

    def setMainText(self, value):
        self._setString(1, value)

    def getWarningText(self):
        return self._getString(2)

    def setWarningText(self, value):
        self._setString(2, value)

    def getPunishmentText(self):
        return self._getString(3)

    def setPunishmentText(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(TextWithWarningViewModel, self)._initialize()
        self._addViewModelProperty('warningImageSubstitution', ImageSubstitutionViewModel())
        self._addStringProperty('mainText', '')
        self._addStringProperty('warningText', '')
        self._addStringProperty('punishmentText', '')
