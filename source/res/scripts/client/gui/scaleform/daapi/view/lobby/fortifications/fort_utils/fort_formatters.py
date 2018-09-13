# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/fort_formatters.py
import BigWorld
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text

def getDefRes(value, addIcon = True):
    valueStr = BigWorld.wg_getIntegralFormat(value)
    text = fort_text.getText(fort_text.PURPLE_TEXT, valueStr)
    if addIcon:
        icon = fort_text.getIcon(fort_text.NUT_ICON)
        return text + ' ' + icon
    else:
        return text


def getBonusText(strValue, buildingID, textsStyle = None):
    textsStyle = textsStyle or (fort_text.NEUTRAL_TEXT, fort_text.STANDARD_TEXT)
    descrStr = i18n.makeString(FORTIFICATIONS.buildings_defresinfo(buildingID))
    resultDescr = fort_text.concatStyles(((textsStyle[0], strValue + ' '), (textsStyle[1], descrStr)))
    return resultDescr


def getDefResWithText(mainTextValue, defResValue, addIcon):
    mainText = fort_text.getText(fort_text.MAIN_TEXT, mainTextValue)
    defResText = getDefRes(defResValue, addIcon)
    return mainText + defResText


def getTextLevel(value):
    value = max(value, 1)
    levels = ['I',
     'II',
     'III',
     'IV',
     'V',
     'VI',
     'VII',
     'VIII',
     'IX',
     'X']
    return levels[value - 1]
