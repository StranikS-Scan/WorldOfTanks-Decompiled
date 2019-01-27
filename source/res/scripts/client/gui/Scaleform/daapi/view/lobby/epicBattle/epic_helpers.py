# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_helpers.py
from gui import SystemMessages
from gui.shared.gui_items.processors.common import EpicPrestigeTrigger
from helpers import dependency
from items import vehicles
from shared_utils import first
from gui.shared.utils import decorators
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
FRONTLINE_PRESTIGE_TOKEN_BASE = 'epicmetagame:prestige:'
FRONTLINE_PRESTIGE_TOKEN_TEMPLATE = FRONTLINE_PRESTIGE_TOKEN_BASE + '%d'
FRONTLINE_PRESTIGE_LEVEL_BASE = 'epicmetagame:levelup:'
FRONTLINE_PRESTIGE_LEVEL_TEMPLATE = FRONTLINE_PRESTIGE_LEVEL_BASE + '%d'
FRONTLINE_TOKEN_PRESTIGE_POINTS = 'prestige_point'
FRONTLINE_HIDDEN_TAG = 'fr_hidden'
FRONTLINE_VEH_BOUGHT_TOKEN_TEMPLATE = 'fr_reward_%s'
_EPIC_GAME_PARAMS = {'artillery': {'cooldownTime': 'Cooldown',
               'delay': 'Deployment',
               'areaRadius': 'Dispersion',
               'shotsNumber': 'Shells',
               'duration-artillery': 'Duration'},
 'bomber': {'cooldownTime': 'Cooldown',
            'delay': 'Deployment',
            'areaLength_areaWidth-dropArea': 'Targeted Area',
            'bombsNumber': 'Bombs',
            'shellCompactDescr': 'Stun'},
 'recon': {'cooldownTime': 'Cooldown',
           'delay': 'Deployment',
           '#epic_battle:abilityInfo/params/recon/revealedArea/value': 'Revealed Area',
           'spottingDuration': 'Spotting Duration'},
 'inspire': {'cooldownTime': 'Cooldown',
             'radius': 'Effect Radius',
             'duration-inspire': 'Duration',
             'crewIncreaseFactor': 'Crew Performance',
             'inactivationDelay': 'Effect Cooldown'},
 'smoke': {'cooldownTime': 'Cooldown',
           'minDelay': 'Deployment',
           'areaLength_areaWidth-targetedArea': 'Targeted Area (length, width)',
           'projectilesNumber': 'Grenades',
           'totalDuration': 'Smoke Lifetime'},
 'passive_engineering': {'resupplyCooldownFactor': 'Resupply Circle Refresh',
                         'resupplyHealthPointsFactor': 'Resupply Speed',
                         'captureSpeedFactor': 'Capture Speed',
                         'captureBlockBonusTime': 'Capture Block Time'}}

def getAwardsForPrestige(prestige):
    return _getFormattedAwardsForQuest(FRONTLINE_PRESTIGE_TOKEN_TEMPLATE % prestige)


def getAwardsForLevel(level):
    return _getFormattedAwardsForQuest(FRONTLINE_PRESTIGE_LEVEL_TEMPLATE % level)


def getAllAwardsForLevel():
    return _getAllAwardsForTokenBase(FRONTLINE_PRESTIGE_LEVEL_BASE)


def getAllAwardsForPrestige():
    return _getAllAwardsForTokenBase(FRONTLINE_PRESTIGE_TOKEN_BASE)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def _getAllAwardsForTokenBase(tokenBase, eventsCache=None):
    awardsData = dict()
    allQuests = eventsCache.getAllQuests()
    for questKey, questData in allQuests.iteritems():
        _, _, questNum = questKey.partition(tokenBase)
        if questNum:
            questAwards = list()
            questBonuses = questData.getBonuses()
            for bonusGroup in questBonuses:
                questAwards.extend(bonusGroup.getWrappedEpicBonusList())

            awardsData[int(questNum)] = questAwards

    return awardsData


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def _getFormattedAwardsForQuest(questKey, eventsCache=None):
    awardsData = []
    allQuests = eventsCache.getAllQuests()
    questData = allQuests.get(questKey, None)
    if questData is not None:
        questBonuses = questData.getBonuses()
        for bonusGroup in questBonuses:
            awardsData.extend(bonusGroup.getWrappedEpicBonusList())

    return awardsData


def checkIfVehicleIsHidden(intCD):
    return FRONTLINE_HIDDEN_TAG in vehicles.getVehicleType(intCD).tags


def getFrontLineSkills():
    epicMetaGameCtrl = dependency.instance(IEpicBattleMetaGameController)
    equipments = vehicles.g_cache.equipments()
    result = []
    for skillID, skillData in epicMetaGameCtrl.getAllSkillsInformation().iteritems():
        skillInfo = dict()
        firstSkill = first(skillData.levels.itervalues())
        skillInfo['icon'] = firstSkill.icon
        skillInfo['longDescr'] = firstSkill.longDescr
        skillInfo['name'] = firstSkill.name
        skillInfo['shortDescr'] = firstSkill.shortDescr
        skillInfo['skillID'] = skillID
        skillInfo['params'] = dict()
        for _, skillLevelData in skillData.levels.iteritems():
            skillInfo.setdefault('levels', []).append(skillLevelData.eqID)
            curLvlEq = equipments[skillLevelData.eqID]
            for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
                paramName = _EPIC_GAME_PARAMS.get(skillLevelData.icon, {}).get(tooltipIdentifier, None)
                if paramName:
                    if hasattr(curLvlEq, tooltipIdentifier):
                        skillInfo['params'].setdefault(paramName, []).append(getattr(curLvlEq, tooltipIdentifier))
                    else:
                        skillInfo['params'].setdefault(paramName, []).append(0)

        result.append(skillInfo)

    return result


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getEpicGamePlayerPrestigePoints(eventsCache=None):
    return eventsCache.questsProgress.getTokenCount(FRONTLINE_TOKEN_PRESTIGE_POINTS) if FRONTLINE_TOKEN_PRESTIGE_POINTS in eventsCache.questsProgress.getTokenNames() else 0


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def checkEpicRewardVehAlreadyBought(vehIntCD, eventsCache=None):
    tokenName = FRONTLINE_VEH_BOUGHT_TOKEN_TEMPLATE % vehIntCD
    return tokenName in eventsCache.questsProgress.getTokenNames()


@decorators.process('updating')
def triggerPrestige():
    result = yield EpicPrestigeTrigger().request()
    if result.userMsg:
        SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
