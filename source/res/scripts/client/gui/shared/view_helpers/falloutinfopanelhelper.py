# Embedded file name: scripts/client/gui/shared/view_helpers/FalloutInfoPanelHelper.py
import BigWorld
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.framework.managers.TextManager import TextManager
from helpers.i18n import makeString

def getHelpTextAsDicts(arenaType):
    costKill, costFlags = getCosts(arenaType)
    flagsHead = __getText(TEXT_MANAGER_STYLES.NEUTRAL_TEXT, FALLOUT.INFOPANEL_GETFLAGS_HEAD)
    flagsDescr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_GETFLAGS_DESCR)
    secretsWinHead = __getText(TEXT_MANAGER_STYLES.NEUTRAL_TEXT, FALLOUT.INFOPANEL_SECRETWIN_HEAD)
    formatter = BigWorld.wg_getNiceNumberFormat
    scorePatterns = []
    if costKill > 0:
        costKillText = makeString(FALLOUT.INFOPANEL_SECRETWIN_DESCR_COST, cost=formatter(costKill))
        secretsWinDescrFirstPrefixStr = TextManager.getText(TEXT_MANAGER_STYLES.STATUS_WARNING_TEXT, costKillText)
        secretsWinDescrFirstStr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_SECRETWIN_DESCR_FIRSTSTR)
        scorePatterns.append(secretsWinDescrFirstPrefixStr + secretsWinDescrFirstStr)
    if costFlags:
        costFlagTextPatterns = []
        for c in costFlags:
            costFlagTextPatterns.append(TextManager.getText(TEXT_MANAGER_STYLES.STATUS_WARNING_TEXT, makeString(FALLOUT.INFOPANEL_SECRETWIN_DESCR_COST, cost=formatter(c))))

        secretsWinJoinPattern = TextManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, ', ')
        secretsWinDescrSecondPrefixStr = secretsWinJoinPattern.join(costFlagTextPatterns)
        secretsWinDescrSecondStr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_SECRETWIN_DESCR_SECONDSTR)
        scorePatterns.append(secretsWinDescrSecondPrefixStr + secretsWinDescrSecondStr)
    joinPattern = TextManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, ';\n')
    secretsWinDescr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_SECRETWIN_DESCR) % {'scorePattern': joinPattern.join(scorePatterns)}
    repairHead = __getText(TEXT_MANAGER_STYLES.NEUTRAL_TEXT, FALLOUT.INFOPANEL_REPAIR_HEAD)
    repairDescr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_REPAIR_DESCR)
    garageHead = __getText(TEXT_MANAGER_STYLES.NEUTRAL_TEXT, FALLOUT.INFOPANEL_GARAGE_HEAD)
    garageDescr = __getText(TEXT_MANAGER_STYLES.MAIN_TEXT, FALLOUT.INFOPANEL_GARAGE_DESCR)
    return [{'head': flagsHead,
      'descr': flagsDescr},
     {'head': secretsWinHead,
      'descr': secretsWinDescr},
     {'head': repairHead,
      'descr': repairDescr},
     {'head': garageHead,
      'descr': garageDescr}]


def getHelpText(arenaType):
    result = []
    helpText = getHelpTextAsDicts(arenaType)
    for item in helpText:
        result.append(item['head'] + '\n' + item['descr'])

    return result


def getCosts(arenaType):
    costKill = 0
    if hasattr(arenaType, 'winPoints'):
        costKill = arenaType.winPoints['winPointsForKill']
    costFlags = set()
    if hasattr(arenaType, 'flagSpawnPoints'):
        for f in arenaType.flagSpawnPoints:
            costFlags.add(f['winPoints'])

    return (costKill, costFlags)


def __getText(style, textId):
    return TextManager.getText(style, makeString(textId))
