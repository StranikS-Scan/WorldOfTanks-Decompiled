# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/fort_formatters.py
import BigWorld
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons, TextManager
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from helpers import i18n

def getDefRes(value, addIcon = True):
    valueStr = BigWorld.wg_getIntegralFormat(value)
    text = TextManager.reference().getText(TextType.DEFRES_TEXT, valueStr)
    if addIcon:
        icon = TextManager.reference().getIcon(TextIcons.NUT_ICON)
        return text + ' ' + icon
    else:
        return text


def getBonusText(strValue, buildingID, textsStyle = None, ctx = None):
    ctx = ctx or {}
    textsStyle = textsStyle or (TextType.NEUTRAL_TEXT, TextType.MAIN_TEXT)
    descrStr = i18n.makeString(FORTIFICATIONS.buildings_defresinfo(buildingID), **ctx)
    resultDescr = TextManager.reference().concatStyles(((textsStyle[0], strValue + ' '), (textsStyle[1], descrStr)))
    return resultDescr


def getDefResWithText(mainTextValue, defResValue, addIcon):
    mainText = TextManager.reference().getText(TextType.MAIN_TEXT, mainTextValue)
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
