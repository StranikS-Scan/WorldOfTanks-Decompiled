# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/Button.py
"""
"""
import BigWorld
import GUI
import Keys
import TextStyles
from PyGUIBase import PyGUIBase
from VisualStateComponent import VisualState, VisualStateComponent
import Utils

def _getRadioParent(parent, groupDepth):
    while groupDepth > 1 and parent is not None:
        parent = parent.parent
        groupDepth -= 1

    return parent


def _sameRadioButtonGroup(comp, groupName):
    return comp.script and getattr(comp.script, 'buttonStyle', None) == Button.RADIOBUTTON_STYLE and comp.script.groupName == groupName


def _getRadioButtons(comp, groupName):
    if comp is None:
        return []
    else:
        radioButtons = []
        for name, child in comp.children:
            radioButtons += _getRadioButtons(child, groupName)
            if _sameRadioButtonGroup(child, groupName):
                radioButtons.append(child)

        return radioButtons
        return


class ButtonVisualState(VisualState):

    def __init__(self):
        VisualState.__init__(self)
        self.textStyle = ''
        self.iconTextureName = ''
        self.iconTextureMapping = None
        self.iconColour = (255, 255, 255, 255)
        return

    def onSave(self, dataSection):
        VisualState.onSave(self, dataSection)
        if self.textStyle:
            dataSection.writeString('textStyle', self.textStyle)
        iconSection = dataSection.createSection('icon')
        iconSection.writeString('textureName', self.iconTextureName)
        iconSection.writeString('materialFX', self.iconMaterialFX)
        if self.iconTextureMapping:
            mappingSection = iconSection.createSection('mapping')
            self._writeMappingSection(mappingSection, self.iconTextureMappingType, self.iconTextureMapping)
        iconSection.writeVector4('colour', self.iconColour)

    def onLoad(self, dataSection):
        VisualState.onLoad(self, dataSection)
        self.textStyle = dataSection.readString('textStyle', '')
        if dataSection.has_key('icon'):
            iconSection = dataSection._icon
            self.iconMaterialFX = iconSection.readString('materialFX', '')
            self.iconTextureName = iconSection.readString('textureName', '')
            if iconSection.has_key('mapping'):
                mappingSection = iconSection._mapping
                mappingType, mapping = self._readMappingSection(mappingSection)
                self.iconTextureMappingType = mappingType
                self.iconTextureMapping = mapping
            else:
                self.iconTextureMapping = None
            self.iconColour = iconSection.readVector4('colour', (255, 255, 255, 255))
        return

    def apply(self, componentScript):
        VisualState.apply(self, componentScript)
        if getattr(componentScript, 'buttonLabel', None) is not None and self.textStyle:
            TextStyles.setStyle(componentScript.buttonLabel, self.textStyle)
        if hasattr(componentScript, 'buttonIcon'):
            componentScript.buttonIcon.textureName = self.iconTextureName
            if self.iconTextureMapping:
                Utils.applyMapping(componentScript.buttonIcon, self.iconTextureMappingType, self.iconTextureMapping)
            componentScript.buttonIcon.colour = self.iconColour
            if self.iconMaterialFX != '':
                componentScript.buttonIcon.materialFX = self.iconMaterialFX
            else:
                componentScript.buttonIcon.materialFX = 'BLEND'
        return


class Button(PyGUIBase, VisualStateComponent):
    PRESSBUTTON_STYLE = 'pressbutton'
    TOGGLEBUTTON_STYLE = 'togglebutton'
    CHECKBOX_STYLE = 'checkbox'
    RADIOBUTTON_STYLE = 'radiobutton'
    TOGGLABLE_BUTTON_STYLES = (TOGGLEBUTTON_STYLE, CHECKBOX_STYLE, RADIOBUTTON_STYLE)
    NORMAL_STATE = 'normal'
    HOVER_STATE = 'hover'
    PRESSED_STATE = 'pressed'
    ACTIVE_STATE = 'active'
    DISABLED_STATE = 'disabled'
    HOVER_ACTIVE_STATE = 'hover_active'
    PRESSED_ACTIVE_STATE = 'pressed_active'
    DISABLED_ACTIVE_STATE = 'disabled_active'
    factoryString = 'PyGUI.Button'
    visualStateString = 'PyGUI.ButtonVisualState'

    def __init__(self, component):
        PyGUIBase.__init__(self, component)
        VisualStateComponent.__init__(self, component, Button.visualStateString)
        component.script = self
        self.component.focus = True
        self.component.mouseButtonFocus = True
        self.component.moveFocus = True
        self.component.crossFocus = True
        self.buttonStyle = Button.PRESSBUTTON_STYLE
        self.buttonPressed = False
        self.buttonActive = False
        self.buttonDisabled = False
        self.groupName = ''
        self.groupDepth = 1
        self.hovering = False
        self.onClick = lambda : None
        self.onActivate = lambda : None
        self.onDeactivate = lambda : None

    def _updateVisualState(self):
        if self.buttonDisabled:
            visualStateName = Button.DISABLED_STATE if not self.buttonActive else Button.DISABLED_ACTIVE_STATE
        elif self.buttonPressed and self.hovering:
            visualStateName = Button.PRESSED_STATE if not self.buttonActive else Button.PRESSED_ACTIVE_STATE
        elif self.hovering:
            visualStateName = Button.HOVER_STATE if not self.buttonActive else Button.HOVER_ACTIVE_STATE
        else:
            visualStateName = Button.NORMAL_STATE if not self.buttonActive else Button.ACTIVE_STATE
        self.setVisualState(visualStateName)

    def _onClick(self):
        if self.buttonDisabled:
            return
        if self.buttonStyle in Button.TOGGLABLE_BUTTON_STYLES:
            self._makeActive(not self.buttonActive)
            if self.buttonActive:
                self.onActivate()
            else:
                self.onDeactivate()
        self.onClick()

    def setDisabledState(self, state):
        if self.buttonDisabled == state:
            return
        self.buttonDisabled = state
        self._updateVisualState()

    def setToggleState(self, state):
        self._makeActive(state)
        self._updateVisualState()

    def _makeActive(self, active = True):
        if self.buttonStyle == Button.RADIOBUTTON_STYLE:
            if self.buttonActive == active:
                return
            if active:
                radioParent = _getRadioParent(self.component.parent, self.groupDepth)
                siblings = _getRadioButtons(radioParent, self.groupName)
                siblings = [ sibling for sibling in siblings if sibling.script != self ]
                for sibling in siblings:
                    if sibling.script.buttonActive:
                        sibling.script.buttonActive = False
                        sibling.script.onDeactivate()
                        sibling.script._updateVisualState()

        if self.buttonStyle in Button.TOGGLABLE_BUTTON_STYLES:
            self.buttonActive = active

    def handleMouseButtonEvent(self, comp, event):
        PyGUIBase.handleMouseButtonEvent(self, comp, event)
        if event.key == Keys.KEY_LEFTMOUSE:
            if event.isKeyDown() and not self.buttonPressed:
                self.buttonPressed = True
            elif not event.isKeyDown() and self.buttonPressed:
                self.buttonPressed = False
                self._onClick()
        self._updateVisualState()
        return True

    def handleMouseEnterEvent(self, comp):
        PyGUIBase.handleMouseEnterEvent(self, comp)
        self.buttonPressed = self.buttonPressed and BigWorld.isKeyDown(Keys.KEY_LEFTMOUSE)
        self.hovering = True
        self._updateVisualState()
        return True

    def handleMouseLeaveEvent(self, comp):
        self.hovering = False
        self._updateVisualState()
        return True

    def onSave(self, dataSection):
        PyGUIBase.onSave(self, dataSection)
        dataSection.writeBool('buttonDisabled', self.buttonDisabled)
        dataSection.writeString('buttonStyle', self.buttonStyle)
        if self.groupName != '':
            dataSection.writeString('groupName', self.groupName)
            dataSection.writeInt('groupDepth', self.groupDepth)
        VisualStateComponent.onSave(self, dataSection)

    def onLoad(self, dataSection):
        PyGUIBase.onLoad(self, dataSection)
        self.buttonStyle = dataSection.readString('buttonStyle')
        self.buttonDisabled = dataSection.readBool('buttonDisabled', False)
        self.groupName = dataSection.readString('groupName')
        self.groupDepth = dataSection.readInt('groupDepth', 1)
        VisualStateComponent.onLoad(self, dataSection)

    def onBound(self):
        self.buttonIcon = self.component
        self.buttonLabel = getattr(self.component, 'label', None)
        self._updateVisualState()
        return

    @staticmethod
    def create(texture, text = '', **kwargs):
        c = GUI.Window(texture)
        c.materialFX = 'BLEND'
        c.widthMode = 'CLIP'
        c.heightMode = 'CLIP'
        c.horizontalPositionMode = 'CLIP'
        c.verticalPositionMode = 'CLIP'
        label = GUI.Text(text)
        c.addChild(label, 'label')
        b = Button(c, **kwargs)
        b.toggleButton = kwargs.get('toggle', False)
        return b.component
