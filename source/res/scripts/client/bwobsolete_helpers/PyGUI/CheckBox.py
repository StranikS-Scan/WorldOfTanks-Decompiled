# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/CheckBox.py
import BigWorld, GUI
from Button import Button

class CheckBox(Button):
    factoryString = 'PyGUI.CheckBox'

    def __init__(self, component):
        Button.__init__(self, component)
        self.buttonStyle = Button.CHECKBOX_STYLE

    def onBound(self):
        self.buttonIcon = self.component.box
        self.buttonLabel = self.component.label
        self._updateVisualState()

    @staticmethod
    def createInternal(texture, text='', **kwargs):
        c = GUI.Window('')
        c.materialFX = GUI.Simple.eMaterialFX.BLEND
        c.widthMode = GUI.Simple.eSizeMode.CLIP
        c.heightMode = GUI.Simple.eSizeMode.CLIP
        c.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        c.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        box = GUI.Simple(texture)
        box.size = (0, 0)
        box.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        box.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        box.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        box.position.x = -1
        box.materialFX = GUI.Simple.eMaterialFX.BLEND
        box.widthMode = GUI.Simple.eSizeMode.PIXEL
        box.heightMode = GUI.Simple.eSizeMode.PIXEL
        box.width = 20
        box.height = 20
        c.addChild(box, 'box')
        label = GUI.Text(text)
        label.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        label.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        label.horizontalAnchor = GUI.Simple.eHAnchor.RIGHT
        label.position.x = 1
        label.colour = (128, 128, 128, 255)
        c.addChild(label, 'label')
        return c

    @staticmethod
    def create(texture, text='', **kwargs):
        b = CheckBox(CheckBox.createInternal(texture, text, **kwargs), **kwargs)
        return b.component
