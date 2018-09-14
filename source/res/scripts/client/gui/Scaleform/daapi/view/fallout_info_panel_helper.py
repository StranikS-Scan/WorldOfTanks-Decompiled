# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/fallout_info_panel_helper.py
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.shared.formatters.text_styles import neutral, main

def getHelpTextAsDicts(arenaVisitor):
    pointsObjective = arenaVisitor.hasResourcePoints()
    isMultiteam = arenaVisitor.gui.isFalloutMultiTeam()
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


def getHelpText(arenaVisitor):
    result = []
    helpText = getHelpTextAsDicts(arenaVisitor)
    for item in helpText:
        result.append('\n'.join((item['head'], item['descr'])))

    return result
