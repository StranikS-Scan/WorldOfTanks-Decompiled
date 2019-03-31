# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/PyGUI/RadioButton.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld, GUI
from Button import Button
from CheckBox import CheckBox

class RadioButton(CheckBox):
    factoryString = 'PyGUI.RadioButton'

    def __init__(self, component):
        CheckBox.__init__(self, component)
        self.buttonStyle = Button.RADIOBUTTON_STYLE

    @staticmethod
    def create(texture, text='', groupName='', **kwargs):
        b = RadioButton(CheckBox.createInternal(texture, text, **kwargs), **kwargs)
        b.groupName = groupName
        return b.component
