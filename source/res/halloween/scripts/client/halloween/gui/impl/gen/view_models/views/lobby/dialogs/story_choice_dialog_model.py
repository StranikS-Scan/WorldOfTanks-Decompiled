# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/dialogs/story_choice_dialog_model.py
from halloween.gui.impl.gen.view_models.views.lobby.dialogs.hw_dialog_model import HwDialogModel

class StoryChoiceDialogModel(HwDialogModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=3):
        super(StoryChoiceDialogModel, self).__init__(properties=properties, commands=commands)

    def getChoice(self):
        return self._getString(0)

    def setChoice(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(StoryChoiceDialogModel, self)._initialize()
        self._addStringProperty('choice', '')
