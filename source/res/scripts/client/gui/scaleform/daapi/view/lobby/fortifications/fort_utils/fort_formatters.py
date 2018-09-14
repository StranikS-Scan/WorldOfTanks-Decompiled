# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/fort_formatters.py
import BigWorld
from gui.Scaleform.framework.managers.TextManager import TextIcons, TextManager
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from helpers import i18n
from gui.Scaleform.locale.RES_COMMON import RES_COMMON

def getDefRes(value, addIcon = True):
    valueStr = BigWorld.wg_getIntegralFormat(value)
    text = TextManager.reference().getText(TEXT_MANAGER_STYLES.DEFRES_TEXT, valueStr)
    if addIcon:
        icon = TextManager.reference().getIcon(TextIcons.NUT_ICON)
        return text + ' ' + icon
    else:
        return text


def getBonusText(strValue, buildingID, textsStyle = None, ctx = None):
    ctx = ctx or {}
    textsStyle = textsStyle or (TEXT_MANAGER_STYLES.NEUTRAL_TEXT, TEXT_MANAGER_STYLES.MAIN_TEXT)
    descrStr = i18n.makeString(FORTIFICATIONS.buildings_defresinfo(buildingID), **ctx)
    resultDescr = TextManager.reference().concatStyles(((textsStyle[0], strValue + ' ' if strValue else ''), (textsStyle[1], descrStr)))
    return resultDescr


def getDefResWithText(mainTextValue, defResValue, addIcon):
    mainText = TextManager.reference().getText(TEXT_MANAGER_STYLES.MAIN_TEXT, mainTextValue)
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


def getIconLevel(value):
    return '../maps/icons/filters/levels/level_{0}.png'.format(value)


def getDivisionIcon(defenderFortLevel, attackerFortLevel, determineAlert = True):
    battleDivision = FORT_BATTLE_DIVISIONS.CHAMPION
    if defenderFortLevel >= FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel:
        battleDivision = FORT_BATTLE_DIVISIONS.ABSOLUTE
    maxPlayers = battleDivision.maxCombatants
    tankLevel = battleDivision.maxVehicleLevel
    divisionID = battleDivision.divisionID
    tankIcon = battleDivision.iconPath
    showAlert = False
    if determineAlert:
        if defenderFortLevel < FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel <= attackerFortLevel:
            showAlert = True
        if defenderFortLevel >= FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel > attackerFortLevel:
            showAlert = True
    return {'showAlert': showAlert,
     'valueText': str(maxPlayers),
     'tankIconSource': tankIcon,
     'lvlIconSource': getIconLevel(tankLevel),
     'divisionID': divisionID}
