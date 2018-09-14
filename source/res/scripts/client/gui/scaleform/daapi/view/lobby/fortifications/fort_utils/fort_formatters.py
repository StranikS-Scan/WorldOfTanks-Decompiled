# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/fort_formatters.py
import BigWorld
from helpers import i18n
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.formatters import icons, text_styles

def getDefRes(value, addIcon = True):
    text = text_styles.defRes(BigWorld.wg_getIntegralFormat(value))
    if addIcon:
        icon = icons.nut()
        return text + ' ' + icon
    else:
        return text


def getBonusText(strValue, buildingID, textsStyle = None, ctx = None):
    ctx = ctx or {}
    textsStyle = textsStyle or (text_styles.neutral, text_styles.main)
    descrStr = i18n.makeString(FORTIFICATIONS.buildings_defresinfo(buildingID), **ctx)
    return ''.join((textsStyle[0](strValue + ' ' if strValue else ''), textsStyle[1](descrStr)))


def getDefResWithText(mainTextValue, defResValue, addIcon):
    mainText = text_styles.main(mainTextValue)
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
