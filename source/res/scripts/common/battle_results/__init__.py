# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_results/__init__.py
import importlib
from DictPackers import Meta, MergeDictPacker
from battle_pass_integration import getAllIntergatedGameModes
from battle_results_common import BATTLE_RESULTS, BATTLE_PASS_RESULTS
from battle_results_constants import BATTLE_RESULT_ENTRY_TYPE as ENTRY_TYPE, PATH_TO_CONFIG, POSSIBLE_TYPES, ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE
from constants import ARENA_BONUS_TYPE
g_config = {'checksums': {},
 'bonusTypes': {},
 'allResults': Meta()}

def __processBonusTypeResults(config, allResults, bonusType, serverResults):
    modeConfig = {}
    for name, transportType, default, packer, aggFunc, entryType in allResults:
        if transportType is None:
            pass
        value = (name,
         transportType,
         default,
         packer,
         aggFunc)
        if name in serverResults:
            if value != serverResults[name]:
                basePacker = serverResults[name][3]
                if isinstance(basePacker, MergeDictPacker) and isinstance(packer, MergeDictPacker):
                    basePacker.merge(packer)
                    if name in set((item[0] for item in modeConfig.get(entryType, []))):
                        continue
        else:
            serverResults[name] = value
        if entryType == ENTRY_TYPE.SERVER:
            continue
        modeConfig.setdefault(entryType, []).append(value)
        if entryType == ENTRY_TYPE.ACCOUNT_ALL:
            modeConfig.setdefault(ENTRY_TYPE.ACCOUNT_SELF, []).append(value)
        if entryType == ENTRY_TYPE.VEHICLE_ALL:
            modeConfig.setdefault(ENTRY_TYPE.VEHICLE_SELF, []).append(value)

    config['bonusTypes'][bonusType] = bonusTypeConfig = {}
    for entryType, resultsList in modeConfig.iteritems():
        meta = Meta(*resultsList)
        config['checksums'][meta.getChecksum()] = meta
        bonusTypeConfig[entryType] = meta

    return


def setBattleResultsConfig(config):
    serverResults = {}
    battlePassIntergated = getAllIntergatedGameModes()
    for bonusType, path in PATH_TO_CONFIG.iteritems():
        if path.startswith('.'):
            path = 'battle_results' + path
        module = importlib.import_module(path)
        allResults = BATTLE_RESULTS + module.BATTLE_RESULTS
        if bonusType in battlePassIntergated:
            allResults += BATTLE_PASS_RESULTS
        __processBonusTypeResults(config, allResults, bonusType, serverResults)

    __processBonusTypeResults(config, BATTLE_RESULTS, 'default', serverResults)
    config['allResults'] = Meta(*sorted(serverResults.values(), key=lambda x: x[0]))


def packClientBattleResults(data, bonusType, packingType):
    if bonusType not in g_config['bonusTypes']:
        bonusType = 'default'
    return g_config['bonusTypes'][bonusType][packingType].pack(data)


def unpackClientBattleResults(data):
    checksum = data[0]
    return None if checksum not in g_config['checksums'] else g_config['checksums'][checksum].unpack(data)


def getBattleResultsNames():
    return g_config['allResults'].names()


def getBattleResultsSysMsgType(bonusType):
    return ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE[ARENA_BONUS_TYPE.REGULAR] if bonusType not in ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE else ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE[bonusType]


def init():
    setBattleResultsConfig(g_config)
