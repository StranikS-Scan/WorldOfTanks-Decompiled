# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/gui_utils.py
import BigWorld
import GUI
import Math
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

def setAnchor(component, hor, vert):
    component.horizontalAnchor = hor
    component.verticalAnchor = vert


def setPixMode(component):
    component.heightMode = 'PIXEL'
    component.widthMode = 'PIXEL'
    component.verticalPositionMode = 'PIXEL'
    component.horizontalPositionMode = 'PIXEL'


def pixToClipVector2(pixVector):
    scrRes = GUI.screenResolution()
    return Math.Vector2(2.0 * pixVector[0] / scrRes[0], -2.0 * pixVector[1] / scrRes[1])


def buildTexMapping(texCoords, texSize, fullTexSize):
    maximum = texCoords + texSize
    return ((texCoords[0] / fullTexSize[0], texCoords[1] / fullTexSize[1]),
     (texCoords[0] / fullTexSize[0], maximum[1] / fullTexSize[1]),
     (maximum[0] / fullTexSize[0], maximum[1] / fullTexSize[1]),
     (maximum[0] / fullTexSize[0], texCoords[1] / fullTexSize[1]))


def getMousePosition():
    mousePos = GUI.mcursor().position
    clipX = (mousePos.x + 1) / 2
    clipY = (1 - mousePos.y) / 2
    scale = dependency.instance(ISettingsCore).interfaceScale.get()
    mouseX = clipX * BigWorld.screenWidth() / scale
    mouseY = clipY * BigWorld.screenHeight() / scale
    return (mouseX, mouseY)
