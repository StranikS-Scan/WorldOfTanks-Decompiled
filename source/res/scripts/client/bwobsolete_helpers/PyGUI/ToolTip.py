# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/ToolTip.py
import BigWorld
import GUI
from functools import partial
from Utils import clipSize
from bwdebug import ERROR_MSG
import PyGUIBase
from Window import Window

class ToolTipInfo(object):

    def __init__(self, component=None, templateName=None, infoDictionary={}, infoArea=None, delayType=None, placement=None):
        if templateName:
            self.templateName = templateName
            self.infoDictionary = infoDictionary
            self.infoArea = infoArea
            self.delayType = delayType
            self.placement = placement

    def onLoad(self, dataSection):
        self.templateName = dataSection._templateName.asString
        self.infoDictionary = {}
        if dataSection.has_key('items'):
            itemsDataSection = dataSection._items
            for key, value in itemsDataSection.items():
                self.infoDictionary[key] = value.asString

        self.infoArea = None
        if dataSection.has_key('infoArea'):
            infoArea = [0,
             0,
             0,
             0]
            infoAreaDataSection = dataSection._infoArea
            infoArea[0] = infoAreaDataSection.readFloat('top')
            infoArea[1] = infoAreaDataSection.readFloat('left')
            infoArea[2] = infoAreaDataSection.readFloat('bottom')
            infoArea[3] = infoAreaDataSection.readFloat('right')
            self.infoArea = tuple(infoArea)
        self.delayType = None
        if dataSection.has_key('delayType'):
            if dataSection._delayType.asString == 'delay':
                self.delayType = ToolTip.DELAYED_TOOL_TIP
            else:
                self.delayType = ToolTip.IMMEDIATE_TOOL_TIP
        self.placement = None
        if dataSection.has_key('placement'):
            self.placement = dataSection._placement.asString
        return

    def onSave(self, dataSection):
        dataSection.writeString('templateName', self.templateName)
        if len(self.infoDictionary) > 0:
            itemsDataSection = dataSection.createSection('items')
            for key, value in self.infoDictionary.iteritems():
                itemsDataSection.writeString(key, value)

        if self.infoArea:
            infoAreaDataSection = dataSection.createSection('items')
            infoAreaDataSection.writeFloat('top', self.infoArea[0])
            infoAreaDataSection.writeFloat('left', self.infoArea[1])
            infoAreaDataSection.writeFloat('bottom', self.infoArea[2])
            infoAreaDataSection.writeFloat('right', self.infoArea[3])
        if self.delayType:
            delayString = 'delay' if self.delayType == ToolTip.DELAYED_TOOL_TIP else 'immediate'
            dataSection.writeString('delayType', delayString)
        if self.placement:
            dataSection.writeString('placement', self.placement)


class ToolTip(Window):
    IMMEDIATE_TOOL_TIP = 1
    DELAYED_TOOL_TIP = 2
    PLACE_BELOW = 'below'
    PLACE_ABOVE = 'above'
    PLACE_LEFT = 'left'
    PLACE_RIGHT = 'right'
    DELAY_TIME = 0.5
    GAP_SIZE = 0.01

    def __init__(self, component):
        Window.__init__(self, component)
        self.items = []

    def setupToolTip(self, toolTipInfo, infoArea):
        self.toolTipInfo = toolTipInfo
        self.infoArea = infoArea
        items = {}
        for item in self.items:
            items[item] = ''

        for key, value in toolTipInfo.infoDictionary.items():
            items[key] = value

        for key, value in items.items():
            try:
                component = getattr(self.component, key)
            except AttributeError:
                continue

            if isinstance(component, GUI.Text):
                component.text = value
            component.textureName = value

        self.doLayout(None)
        return

    def onSave(self, dataSection):
        Window.onSave(self, dataSection)
        if len(self.items) > 0:
            itemSection = dataSection.createSection('items')
            for item in self.items:
                itemSection.createSection(item)

    def onLoad(self, dataSection):
        Window.onLoad(self, dataSection)
        if dataSection.has_key('items'):
            itemSection = dataSection._items
            for item in itemSection.keys():
                self.items.append(item)

    def doLayout(self, parent):
        mousePos = GUI.mcursor().position
        placement = self.toolTipInfo.placement if self.toolTipInfo.placement else ToolTip.PLACE_ABOVE
        zorder = self.component.position.z
        self.component.position = self.getToolTipPosition(mousePos, self.infoArea, placement)
        self.component.position.z = zorder

    def getToolTipPosition(self, mousePos, infoArea, placement):
        width, height = clipSize(self.component)
        if placement == ToolTip.PLACE_BELOW:
            position = [mousePos[0], infoArea[3] - ToolTip.GAP_SIZE - height / 2]
        elif placement == ToolTip.PLACE_ABOVE:
            position = [mousePos[0], infoArea[1] + ToolTip.GAP_SIZE + height / 2]
        elif placement == ToolTip.PLACE_LEFT:
            position = [infoArea[0] - ToolTip.GAP_SIZE - width / 2, mousePos[1]]
        elif placement == ToolTip.PLACE_RIGHT:
            position = [infoArea[2] + ToolTip.GAP_SIZE + width / 2, mousePos[1]]
        if position[0] - width / 2 < -1.0:
            if placement == ToolTip.PLACE_LEFT:
                position[0] = infoArea[2] + ToolTip.GAP_SIZE + width / 2
            else:
                position[0] = -1.0 + ToolTip.GAP_SIZE + width / 2
        elif position[0] + width / 2 > 1.0:
            if placement == ToolTip.PLACE_RIGHT:
                position[0] = infoArea[0] - ToolTip.GAP_SIZE - width / 2
            else:
                position[0] = 1.0 - ToolTip.GAP_SIZE - width / 2
        if position[1] - height / 2 < -1.0:
            if placement == ToolTip.PLACE_BELOW:
                position[1] = infoArea[1] + ToolTip.GAP_SIZE + height / 2
            else:
                position[1] = -1.0 + ToolTip.GAP_SIZE + height / 2
        elif position[1] + height / 2 > 1.0:
            if placement == ToolTip.PLACE_ABOVE:
                position[1] = infoArea[3] - ToolTip.GAP_SIZE - height / 2
            else:
                position[1] = 1.0 - ToolTip.GAP_SIZE - height / 2
        return (position[0], position[1], 0.0)


class ToolTipManager(object):
    instance = None

    def __init__(self, rootGUI, zorder):
        self.rootGUI = rootGUI
        self.toolTipZOrder = zorder
        self.toolTipGUIs = {}
        self.toolTipGUI = None
        self.infoAreaTop = 0
        self.infoAreaLeft = 0
        self.infoAreaBottom = 0
        self.infoAreaRight = 0
        self.showToolTipCallback = None
        ToolTipManager.instance = self
        return

    def addToolTipTemplate(self, templateName, guiFileName):
        if not self.toolTipGUIs.has_key(templateName):
            toolTipGUI = GUI.load(guiFileName)
            toolTipGUI.horizontalAnchor = 'CENTER'
            toolTipGUI.verticalAnchor = 'CENTER'
            toolTipGUI.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
            toolTipGUI.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
            toolTipGUI.position.z = self.toolTipZOrder
            self.toolTipGUIs[templateName] = toolTipGUI
        return self.toolTipGUIs[templateName]

    def setupToolTip(self, component, toolTipInfo):
        if not self.toolTipGUIs.has_key(toolTipInfo.templateName):
            ERROR_MSG("Setting up tool tip with missing template '%s'" % (toolTipInfo.templateName,))
            return
        else:
            if self.toolTipGUI != self.toolTipGUIs[toolTipInfo.templateName] and self.toolTipGUI in self.rootGUI.children:
                self.rootGUI.delChild(self.toolTipGUI)
                self.toolTipGUI = None
            if toolTipInfo.infoArea:
                infoArea = toolTipInfo.infoArea
            else:
                infoArea = (0.0,
                 0.0,
                 component.width,
                 component.height)
            self.infoAreaLeft, self.infoAreaTop = component.localToScreen((infoArea[0], infoArea[1]))
            self.infoAreaRight, self.infoAreaBottom = component.localToScreen((infoArea[2], infoArea[3]))
            showFunction = partial(self._showToolTip, component, toolTipInfo)
            if self.showToolTipCallback is not None:
                BigWorld.cancelCallback(self.showToolTipCallback)
                self.showToolTipCallback = None
            if toolTipInfo.delayType and toolTipInfo.delayType == ToolTip.IMMEDIATE_TOOL_TIP:
                showFunction()
                self.showToolTipCallback = None
            else:
                self.showToolTipCallback = BigWorld.callback(ToolTip.DELAY_TIME, showFunction)
            return

    def handleMouseEvent(self, event):
        if self.showToolTipCallback or self.toolTipGUI:
            mpos = event.cursorPosition
            if mpos.x < self.infoAreaLeft or mpos.x > self.infoAreaRight or mpos.y < self.infoAreaBottom or mpos.y > self.infoAreaTop:
                if self.toolTipGUI:
                    self.rootGUI.delChild(self.toolTipGUI)
                    self.toolTipGUI = None
                if self.showToolTipCallback:
                    BigWorld.cancelCallback(self.showToolTipCallback)
                    self.showToolTipCallback = None
                    self.toolTipGUI = None
        return

    def _showToolTip(self, component, toolTipInfo):
        self.toolTipGUI = self.toolTipGUIs[toolTipInfo.templateName]
        self.showToolTipCallback = None
        infoArea = (self.infoAreaLeft,
         self.infoAreaTop,
         self.infoAreaRight,
         self.infoAreaBottom)
        self.toolTipGUI.script.setupToolTip(toolTipInfo, infoArea)
        self.rootGUI.addChild(self.toolTipGUI)
        return
