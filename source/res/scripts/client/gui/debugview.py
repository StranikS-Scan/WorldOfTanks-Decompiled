# Embedded file name: scripts/client/gui/DebugView.py
import BigWorld
import GUI
from gui import g_guiResetters

class DebugView():

    def __init__(self, textureName = '', parentGUI = None):
        self.__listKeynames = []
        self.__dictItems = {}
        self.__bAutoUpdate = False
        self.__align = [False,
         False,
         False,
         False]
        self.__margin = [0.0,
         0.0,
         0.0,
         0.0]
        self.__window = None
        self.__createMainWindow(parentGUI)
        g_guiResetters.add(self.__onChangeScreenResolution)
        self.setTextureName(textureName)
        self.setVisible(False)
        return

    def destroy(self):
        g_guiResetters.remove(self.__onChangeScreenResolution)
        self.clear()
        self.__destroyMainWindow()

    def clear(self):
        for curKeyname in self.__listKeynames[:]:
            self.removeItem(curKeyname)

    def setVisible(self, bValue):
        self.__window.visible = bool(bValue)

    def getVisible(self):
        return self.__window.visible

    def setPosition(self, pos3d):
        self.__window.position = tuple(pos3d)

    def getPosition(self):
        return self.__window.position

    def setSize(self, size):
        self.__window.size = tuple(size)

    def getSize(self):
        return self.__window.size

    def setTextureName(self, textureName):
        self.__window.textureName = str(textureName)

    def getTextureName(self):
        return self.__window.textureName

    def getParent(self):
        return self.__window.parent

    def getParentSize(self):
        parent = self.__window.parent
        if parent is not None:
            return parent.size
        else:
            return

    def setAutoUpdate(self, bValue):
        self.__bAutoUpdate = bool(bValue)

    def getAutoUpdate(self):
        return self.__bAutoUpdate

    def setAlign(self, value, index = None):
        if index is None:
            self.__align = [bool(value[0]),
             bool(value[1]),
             bool(value[2]),
             bool(value[3])]
        else:
            self.__align[index] = bool(value)
        return

    def getAlign(self, index = None):
        if index is None:
            return list(self.__align)
        else:
            return self.__align[index]

    def setMargin(self, value, index = None):
        if index is None:
            self.__margin = [float(value[0]),
             float(value[1]),
             float(value[2]),
             float(value[3])]
        else:
            self.__margin[index] = float(value)
        return

    def getMargin(self, index = None):
        if index is None:
            return list(self.__margin)
        else:
            return self.__margin[index]

    def getListKeynames(self):
        return list(self.__listKeynames)

    def getDictItems(self):
        return dict(self.__dictItems)

    def iterkeynames(self):
        return iter(self.__listKeynames)

    def iteritems(self):
        return self.__dictItems.itervalues()

    def getItemsCount(self):
        return len(self.__listKeynames)

    def getItem(self, keyname):
        return self.__dictItems.get(str(keyname), None)

    def addItem(self, keyname, item):
        if not isinstance(item, DebugViewItem):
            return
        else:
            try:
                newPos = self.__listKeynames.index(keyname)
                self.removeItem(keyname)
            except:
                newPos = None

            if newPos is not None:
                self.__listKeynames.insert(newPos, keyname)
            else:
                self.__listKeynames.append(keyname)
            self.__dictItems[keyname] = item
            self.__window.addChild(item._guiName)
            self.__window.addChild(item._guiValue)
            if self.__bAutoUpdate:
                self.update()
            return

    def removeItem(self, keyname):
        if keyname not in self.__listKeynames:
            return
        item = self.__dictItems[keyname]
        self.__listKeynames.remove(keyname)
        del self.__dictItems[keyname]
        self.__window.delChild(item._guiName)
        self.__window.delChild(item._guiValue)
        if self.__bAutoUpdate:
            self.update()
        item.destroy()

    def renameKeyname(self, keyname, newKeyname):
        if keyname not in self.__listKeynames:
            return
        item = self.__dictItems[keyname]
        del self.__dictItems[keyname]
        self.__dictItems[newKeyname] = item
        self.__listKeynames[self.__listKeynames.index(keyname)] = newKeyname
        if self.__bAutoUpdate:
            self.update()

    def rebuild(self):
        saved_parent = self.getParent()
        saved_position = self.getPosition()
        saved_size = self.getSize()
        saved_textureName = self.getTextureName()
        saved_visible = self.getVisible()
        for curItem in self.__dictItems.itervalues():
            self.__window.delChild(curItem._guiName)
            self.__window.delChild(curItem._guiValue)

        GUI.delRoot(self.__window)
        self.__window = None
        for curItem in self.__dictItems.itervalues():
            curItem._rebuild()

        self.__createMainWindow(saved_parent)
        self.setPosition(saved_position)
        self.setSize(saved_size)
        self.setTextureName(saved_textureName)
        self.setVisible(saved_visible)
        for curItem in self.__dictItems.itervalues():
            self.__window.addChild(curItem._guiName)
            self.__window.addChild(curItem._guiValue)

        if self.__bAutoUpdate:
            self.update()
        return

    def moveLine(self, keyname, deltaLine):
        if deltaLine == 0:
            return
        try:
            ind = self.__listKeynames.index(keyname)
        except:
            return

        if deltaLine < 0:
            block = self.__listKeynames[ind + deltaLine:ind]
            block.insert(0, keyname)
            self.__listKeynames[ind + deltaLine:ind + 1] = block
        else:
            block = self.__listKeynames[ind + 1, ind + 1 + deltaLine]
            block.append(keyname)
            self.__listKeynames[ind:ind + 1 + deltaLine] = block
        if self.__bAutoUpdate:
            self.update()

    def swapLines(self, keyname1, keyname2):
        if deltaLine == 0:
            return
        try:
            ind1 = self.__listKeynames.index(keyname1)
            ind2 = self.__listKeynames.index(keyname2)
        except:
            return

        self.__listKeynames[ind1] = keyname2
        self.__listKeynames[ind2] = keyname1
        if self.__bAutoUpdate:
            self.update()

    def update(self):
        self.normalizeLayout()

    def normalizeLayout(self):
        if not self.getVisible():
            return
        totalHeight = 0.0
        maxWidth1 = 0.0
        maxWidth2 = 0.0
        for curKeyname in self.__listKeynames:
            curItem = self.__dictItems[curKeyname]
            maxWidth1 = curItem._guiName.width if curItem._guiName.width > maxWidth1 else maxWidth1
            maxWidth2 = curItem._guiValue.width if curItem._guiValue.width > maxWidth2 else maxWidth2
            if curItem._guiName.height > curItem._guiValue.height:
                curLineHeight = curItem._guiName.height
            else:
                curLineHeight = curItem._guiValue.height
            totalHeight += curLineHeight

        totalWidth = maxWidth1 + maxWidth2
        self.__window.size = (totalWidth, totalHeight)
        curHeight = 0.0
        for curKeyname in self.__listKeynames:
            curItem = self.__dictItems[curKeyname]
            curItem._guiName.position = LU2BW((0.0, curHeight, 1.0), curItem._guiName.parent)
            curItem._guiValue.position = LU2BW((totalWidth - maxWidth2, curHeight, 1.0), curItem._guiValue.parent)
            if curItem._guiName.height > curItem._guiValue.height:
                curLineHeight = curItem._guiName.height
            else:
                curLineHeight = curItem._guiValue.height
            curHeight += curLineHeight

        size = self.getSize()
        pos = list(self.getPosition())
        if self.getAlign(3):
            if pos[1] - size[1] < self.getMargin(3) - 1.0:
                pos[1] -= pos[1] - size[1] + 1.0 - self.getMargin(3)
        if self.getAlign(2):
            if pos[0] + size[0] > 1.0 - self.getMargin(2):
                pos[0] -= pos[0] + size[0] - 1.0 + self.getMargin(2)
        if self.getAlign(1):
            if pos[1] > 1.0 - self.getMargin(1):
                pos[1] -= pos[1] - 1.0 + self.getMargin(1)
        if self.getAlign(0):
            if pos[0] < self.getMargin(0) - 1.0:
                pos[0] -= pos[0] + 1.0 - self.getMargin(0)
        self.__window.position = tuple(pos)

    def __createMainWindow(self, parentGUI):
        self.__window = GUI.Window()
        self.__window.horizontalAnchor = 'LEFT'
        self.__window.verticalAnchor = 'TOP'
        if parentGUI is None:
            GUI.addRoot(self.__window)
        else:
            parentGUI.addChild(self.__window)
        return

    def __destroyMainWindow(self):
        if self.__window.parent is not None:
            self.__window.parent.delChild(self.__window)
        else:
            GUI.delRoot(self.__window)
        self.__window = None
        return

    def __onChangeScreenResolution(self):
        self.rebuild()


class DebugViewItem():

    def __init__(self, name = '', value = '', divider = ' = '):
        self.__name = str(name)
        self.__value = str(value)
        self.__divider = str(divider)
        self.__createGUI()
        self.setFont(('default_smaller.font', 'default_smaller.font'))
        self.setColour(((255.0, 255.0, 255.0, 255.0), (255.0, 255.0, 255.0, 255.0)))
        self.setMaterialFX(('ADD', 'ADD'))

    def destroy(self):
        self.__destroyGUI()

    def setName(self, name):
        self.__name = str(name)
        self._guiName.text = self.__name + self.__divider

    def getName(self):
        return self._name

    def setValue(self, value):
        self.__value = str(value)
        self._guiValue.text = self.__value

    def getValue(self):
        return self.__value

    def setDivider(self, divider):
        self.__divider = str(divider)
        self._guiName.text = self.__name + self.__divider

    def getDivider(self):
        return self.__divider

    def setFont(self, font2):
        self._guiName.font = str(font2[0])
        self._guiValue.font = str(font2[1])

    def setFontName(self, font):
        self._guiValue.font = str(font)

    def setFontValue(self, font):
        self._guiName.font = str(font)

    def getFont(self):
        return (self._guiName.font, self._guiValue.font)

    def getFontName(self):
        return self._guiName.font

    def getFontValue(self):
        return self._guiValue.font

    def setColour(self, colour2):
        self._guiName.colour = tuple(colour2[0])
        self._guiValue.colour = tuple(colour2[1])

    def setColourName(self, colour):
        self._guiName.colour = tuple(colour)

    def setColourValue(self, colour):
        self._guiValue.colour = tuple(colour)

    def getColour(self):
        return (self._guiName.colour, self._guiValue.colour)

    def getColourName(self):
        return self._guiName.colour

    def getColourValue(self):
        return self._guiValue.colour

    def setMaterialFX(self, materialFX2):
        self._guiName.materialFX = str(materialFX2[0])
        self._guiValue.materialFX = str(materialFX2[1])

    def setMaterialFXName(self, materialFX):
        self._guiName.materialFX = str(materialFX)

    def setMaterialFXValue(self, materialFX):
        self._guiValue.materialFX = str(materialFX)

    def getMaterialFX(self):
        return (self._guiName.materialFX, self._guiValue.materialFX)

    def getMaterialFXName(self):
        return self._guiName.materialFX

    def getMaterialFXValue(self):
        return self._guiValue.materialFX

    def setVisible(self, bValue):
        self._guiName.visible = bool(bValue)
        self._guiValue.visible = bool(bValue)

    def getVisible(self):
        return self._guiName.visible

    def getHeight(self):
        return self._guiName.size[1]

    def _setPosition(self, pos2):
        self._guiName.position, self._guiValue.position = pos2

    def _getPosition(self):
        return (self._guiName.position, self._guiValue.position)

    def _rebuild(self):
        saved_font2 = self.getFont()
        saved_colour2 = self.getColour()
        saved_materialFX2 = self.getMaterialFX()
        saved_position2 = self._getPosition()
        saved_visible = self.getVisible()
        self.__createGUI()
        self.setFont(saved_font2)
        self.setColour(saved_colour2)
        self.setMaterialFX(saved_materialFX2)
        self._setPosition(saved_position2)
        self.setVisible(saved_visible)

    def __createGUI(self):
        self._guiName = GUI.Text(self.__name + self.__divider)
        self._guiName.horizontalAnchor = 'LEFT'
        self._guiName.verticalAnchor = 'TOP'
        self._guiValue = GUI.Text(self.__value)
        self._guiValue.horizontalAnchor = 'LEFT'
        self._guiValue.verticalAnchor = 'TOP'

    def __destroyGUI(self):
        raise self._guiName.parent is None or AssertionError
        raise self._guiValue.parent is None or AssertionError
        GUI.delRoot(self._guiName)
        self._guiName = None
        GUI.delRoot(self._guiValue)
        self._guiValue = None
        return


def LU2BW(point3d, parent = None):
    if parent is None:
        sizeX = -2.0
        sizeY = 2.0
    else:
        sizeX, sizeY = parent.size
        sizeX = -sizeX
    return (sizeX * 0.5 + point3d[0], sizeY * 0.5 - point3d[1], point3d[2])
