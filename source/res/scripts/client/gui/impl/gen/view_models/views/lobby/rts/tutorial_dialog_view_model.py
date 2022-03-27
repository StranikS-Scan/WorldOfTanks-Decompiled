# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/tutorial_dialog_view_model.py
from enum import Enum
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class State(Enum):
    INVITATION = 'invitation'
    VICTORY = 'victory'
    DEFEAT = 'defeat'


class Placeholder(Enum):
    HEADER = 'header'
    SUBHEADER = 'subheader'
    BUTTONS_DESCRIPTION = 'buttonsDescription'
    VICTORY_LAYER = 'victoryLayer'
    BACKGROUND = 'background'


class TutorialDialogViewModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=2):
        super(TutorialDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(5))

    def setState(self, value):
        self._setString(5, value.value)

    def _initialize(self):
        super(TutorialDialogViewModel, self)._initialize()
        self._addStringProperty('state')
