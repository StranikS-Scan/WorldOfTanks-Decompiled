# Embedded file name: scripts/client/gui/Scaleform/daapi/view/fallout_info_panel_helper.py
from gui.battle_control.arena_info import hasResourcePoints, getIsMultiteam
import win_points
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.shared.formatters.text_styles import neutral, main

def getHelpTextAsDicts(arenaType = None, arenaBonusType = None):
    pointsObjective = hasResourcePoints(arenaType, arenaBonusType)
    isMultiteam = getIsMultiteam()
    if pointsObjective:
        objectiveHead = neutral(FALLOUT.INFOPANEL_RESOURCEPOINTS_HEAD)
        objectiveDescr = main(FALLOUT.INFOPANEL_RESOURCEPOINTS_DESCR)
    else:
        objectiveHead = neutral(FALLOUT.INFOPANEL_GETFLAGS_HEAD)
        objectiveDescr = main(FALLOUT.INFOPANEL_GETFLAGS_DESCR)
    secretsWinHead = neutral(FALLOUT.INFOPANEL_SECRETWIN_HEAD)
    secretsWinDescr = main(FALLOUT.INFOPANEL_SECRETWIN_DESCR)
    repairHead = neutral(FALLOUT.INFOPANEL_REPAIR_HEAD)
    repairDescr = main(FALLOUT.INFOPANEL_REPAIR_DESCR)
    if isMultiteam:
        garageHead = neutral(FALLOUT.INFOPANEL_GARAGEMULTITEAM_HEAD)
        garageDescr = main(FALLOUT.INFOPANEL_GARAGEMULTITEAM_DESCR)
    else:
        garageHead = neutral(FALLOUT.INFOPANEL_GARAGE_HEAD)
        garageDescr = main(FALLOUT.INFOPANEL_GARAGE_DESCR)
    return [{'head': objectiveHead,
      'descr': objectiveDescr},
     {'head': secretsWinHead,
      'descr': secretsWinDescr},
     {'head': repairHead,
      'descr': repairDescr},
     {'head': garageHead,
      'descr': garageDescr}]


def getHelpText(arenaType = None, arenaBonusType = None):
    result = []
    helpText = getHelpTextAsDicts(arenaType, arenaBonusType)
    for item in helpText:
        result.append('\n'.join((item['head'], item['descr'])))

    return result


def getCosts(arenaType, isSolo = False, forVehicle = True):
    costKill = 0
    costFlags = set()
    costDamage = set()
    if hasattr(arenaType, 'winPoints'):
        winPoints = win_points.g_cache[arenaType.winPoints]
        costKill = winPoints.pointsForKill(isSolo, forVehicle)
        costFlags = set(winPoints.pointsForFlag(isSolo))
        costDamage = winPoints.pointsForDamage(isSolo, forVehicle)
    return (costKill, costFlags, costDamage)
