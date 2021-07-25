# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/maps_training_common/helpers.py
from collections import defaultdict
from bonus_readers import SUPPORTED_BONUSES_IDS, SUPPORTED_BONUSES_NAMES
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES, MAPS_REWARDS_INDEX
from maps_training_constants import DEFAULT_PROGRESS_VALUE, PROGRESS_DATA_MASK, VEHICLE_TYPE, MAX_SCENARIO_PROGRESS

def extractScenarioProgress(progress, team, veh_type):
    offset = VEHICLE_TYPE.OFFSET[team][veh_type]
    history_best_result = progress >> offset & PROGRESS_DATA_MASK
    return history_best_result


def getUpdatedScenarioProgress(progress, team, veh_type, new_level):
    offset = VEHICLE_TYPE.OFFSET[team][veh_type]
    history_best_result = extractScenarioProgress(progress, team, veh_type)
    if new_level > history_best_result:
        history_best_result = new_level
    new_progress = progress & ~(PROGRESS_DATA_MASK << offset)
    new_progress |= history_best_result << offset
    return new_progress


def packMapsTrainingScenarios(scenarios):
    out = []
    for team, teamConfig in scenarios.items():
        packedTeam = []
        for vehClass, i in VEHICLE_CLASS_INDICES.items():
            config = teamConfig.get(vehClass)
            if config is None:
                continue
            duration = [config['duration']['initial'], config['duration']['max']]
            goals = [ config['goals'][vClass] for vClass in VEHICLE_CLASSES ]
            packedTeam.append([i, duration, goals])

        out.append([team, packedTeam])

    return out


def unpackMapsTrainingScenarios(scenarios):
    out = {}
    for team, teamConf in scenarios:
        out[team] = {}
        for vehClassIndex, durationConf, goalsConf in teamConf:
            vehClass = VEHICLE_CLASSES[vehClassIndex]
            duration = dict(zip(['initial', 'max'], durationConf))
            goals = dict(zip(VEHICLE_CLASSES, goalsConf))
            out[team][vehClass] = {'duration': duration,
             'goals': goals}

    return out


def packMapsTrainingRewards(rewards):
    out = [ [] for _ in range(len(rewards)) ]
    for stageName, stageRewards in rewards.iteritems():
        stageOut = []
        for rewardName, rewardData in stageRewards.iteritems():
            rewardIndex = SUPPORTED_BONUSES_IDS.get(rewardName)
            if rewardIndex is None and rewardName == 'items':
                rewardIndex = SUPPORTED_BONUSES_IDS['item']
                rewardData = [ (rewardID, rewardData[rewardID]) for rewardID in sorted(rewardData) ]
            if rewardIndex is not None:
                stageOut.append((rewardIndex, rewardData))

        out[MAPS_REWARDS_INDEX[stageName]] = stageOut

    return out


def unpackMapsTrainingRewards(rewards):
    out = {}
    for stageIndex, stageRewards in enumerate(rewards):
        stageName = MAPS_REWARDS_INDEX.keys()[MAPS_REWARDS_INDEX.values().index(stageIndex)]
        out[stageName] = stageOut = {}
        for rewardIndex, rewardData in stageRewards:
            rewardName = SUPPORTED_BONUSES_NAMES[rewardIndex]
            if rewardIndex == SUPPORTED_BONUSES_IDS['item']:
                rewardName = 'items'
                rewardData = dict(rewardData)
            stageOut[rewardName] = rewardData

    return out


def getMapsTrainingAwards(mapRewards, historyBestResult, currentResult, mapComplete):
    rewards = {}
    if currentResult == MAX_SCENARIO_PROGRESS and historyBestResult < currentResult:
        if mapComplete:
            rewards.update(mapRewards['mapComplete'])
        rewards.update(mapRewards['scenarioComplete'])
    return rewards
