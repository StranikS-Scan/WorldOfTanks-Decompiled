# Embedded file name: scripts/client/gui/Scaleform/daapi/view/fallout_info_panel_helper.py
import BigWorld
import constants
from gui.battle_control.arena_info import hasResourcePoints
import win_points
from gui.Scaleform.locale.FALLOUT import FALLOUT
from helpers.i18n import makeString
from gui.shared.formatters.text_styles import neutral, main, warning

def getHelpTextAsDicts(arenaType = None, arenaBonusType = None, isSolo = False):
    pointsObjective = hasResourcePoints(arenaType, arenaBonusType)
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


def getHelpText(arenaType = None, arenaBonusType = None, isSolo = False):
    result = []
    helpText = getHelpTextAsDicts(arenaType, arenaBonusType, isSolo)
    for item in helpText:
        result.append('\n'.join((item['head'], item['descr'])))

    return result


def getCosts(arenaType, isSolo = False):
    costKill = 0
    costFlags = set()
    if hasattr(arenaType, 'winPoints'):
        winPoints = win_points.g_cache[arenaType.winPoints]
        costKill = winPoints.pointsForKill(isSolo)
        costFlags = set(winPoints.pointsForFlag(isSolo))
    return (costKill, costFlags)
