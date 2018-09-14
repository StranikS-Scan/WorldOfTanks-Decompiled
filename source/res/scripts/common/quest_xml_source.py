# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/quest_xml_source.py
from copy import deepcopy
from pprint import pformat
import time
import ResMgr
import nations
import ArenaType
import battle_results_shared
from debug_utils import LOG_DEBUG, LOG_WARNING
from dossiers2.custom.layouts import accountDossierLayout, vehicleDossierLayout, StaticSizeBlockBuilder, BinarySetDossierBlockBuilder
from dossiers2.custom.records import RECORD_DB_IDS
from items import vehicles, tankmen
from constants import VEHICLE_CLASS_INDICES, ARENA_BONUS_TYPE, EVENT_TYPE, IGR_TYPE, ATTACK_REASONS, QUEST_RUN_FLAGS, DEFAULT_QUEST_START_TIME, DEFAULT_QUEST_FINISH_TIME
from bonus_readers import readBonusSection, readUTC
from optional_bonuses import walkBonuses, FilterVisitor, StripVisitor
_WEEKDAYS = {'Mon': 1,
 'Tue': 2,
 'Wed': 3,
 'Thu': 4,
 'Fri': 5,
 'Sat': 6,
 'Sun': 7}
_YEAR = 31556926
MAX_BONUS_LIMIT = 1000000

class XMLNode(object):
    __slots__ = ('name', 'value', 'questClientConditions', 'relatedGroup', 'info', 'bonus', 'groupContent')

    def __init__(self, name=''):
        self.name = name
        self.value = []
        self.questClientConditions = []
        self.relatedGroup = ''
        self.info = {}
        self.bonus = {}
        self.groupContent = None
        return

    def __repr__(self):
        dump = {'name': self.name,
         'conditions': self.questClientConditions,
         'nested': self.value}
        if self.relatedGroup:
            dump.update(group=self.relatedGroup)
        return pformat(dump, indent=4)

    def getChildNode(self, name, relatedGroup=None):
        childNode = None
        for subnode in self.value:
            if not isinstance(subnode, XMLNode):
                continue
            if subnode.name == name or relatedGroup is not None and subnode.relatedGroup == relatedGroup:
                childNode = subnode
                break

        return childNode

    def getFirstChildValue(self):
        return None if len(self.value) == 0 else self.value[0]

    def isExistChildNode(self, nodeName):
        for child in self.value:
            if isinstance(child, XMLNode):
                if child.name == nodeName or child.isExistChildNode(nodeName):
                    return True

        return False

    def addChild(self, childNode, needClientInfo=True):
        self.value.append(childNode)
        if not needClientInfo:
            return
        if isinstance(childNode, XMLNode):
            self.questClientConditions.append((childNode.name, childNode.questClientConditions))
        else:
            self.questClientConditions.append(('value', childNode))


class Source(object):

    def __init__(self):
        pass

    def readFromExternalFile(self, path, gStartTime, gFinishTime, curTime):
        ResMgr.purge(path)
        section = ResMgr.openSection(path)
        if section is None:
            raise Exception("Can not open '%s'" % path)
        return {} if not section.has_key('quests') else self.__readXML(section['quests'], curTime, gStartTime, gFinishTime)

    def readFromInternalFile(self, path, curTime):
        ResMgr.purge(path)
        section = ResMgr.openSection(path)
        if section is None:
            raise Exception("Can not open '%s'" % path)
        return {} if not section.has_key('quests') else self.__readXML(section['quests'], curTime)

    def __readXML(self, section, curTime, gStartTime=DEFAULT_QUEST_START_TIME, gFinishTime=DEFAULT_QUEST_FINISH_TIME):
        nodes = {}
        for typeName, questSection in section.items():
            enabled = questSection.readBool('enabled', False)
            if not enabled:
                continue
            eventType = EVENT_TYPE.NAME_TO_TYPE[typeName]
            mainNode = XMLNode('main')
            mainNode.info = info = self.__readHeader(eventType, questSection, curTime, gStartTime, gFinishTime)
            if not info['announceTime'] <= curTime <= info['finishTime']:
                LOG_WARNING('Skipping outdated quest', info['id'], curTime, info['announceTime'], info['finishTime'])
                continue
            if eventType == EVENT_TYPE.GROUP:
                mainNode.groupContent = tuple(self.__readGroupContent(questSection))
            conditionReaders = self.__getConditionReaders(eventType)
            availableBonuses = self.__getAvailableBonuses(eventType)
            commonNode = XMLNode('common')
            bonusNode = XMLNode('bonus')
            prebattleNode = XMLNode('preBattle')
            accountNode = XMLNode('account')
            prebattleNode.addChild(accountNode)
            vehicleNode = XMLNode('vehicle')
            prebattleNode.addChild(vehicleNode)
            battleNode = XMLNode('battle')
            prebattleNode.addChild(battleNode)
            postbattleNode = XMLNode('postBattle')
            mainNode.addChild(prebattleNode)
            mainNode.addChild(postbattleNode)
            mainNode.addChild(commonNode)
            mainNode.addChild(bonusNode)
            info['isIGR'] = accountNode.isExistChildNode('igrType')
            conditions = questSection['conditions']
            if conditions and conditions.has_key('preBattle'):
                condition = conditions['preBattle']
                if condition.has_key('account'):
                    self.__readBattleResultsConditionList(conditionReaders, condition['account'], accountNode)
                if eventType in EVENT_TYPE.LIKE_BATTLE_QUESTS:
                    if condition.has_key('vehicle'):
                        self.__readBattleResultsConditionList(conditionReaders, condition['vehicle'], vehicleNode)
                    if condition.has_key('battle'):
                        self.__readBattleResultsConditionList(conditionReaders, condition['battle'], battleNode)
            if eventType in EVENT_TYPE.LIKE_BATTLE_QUESTS and conditions and conditions.has_key('postBattle'):
                condition = conditions['postBattle']
                self.__readBattleResultsConditionList(conditionReaders, condition, postbattleNode)
            if conditions and conditions.has_key('common'):
                condition = conditions['common']
                self.__readBattleResultsConditionList(conditionReaders, condition, commonNode)
            daily = commonNode.getChildNode('daily')
            info['isDaily'] = daily is not None
            groupBy = commonNode.getChildNode('groupBy')
            info['groupBy'] = groupBy.getChildNode('groupName').getFirstChildValue() if groupBy else None
            inrow = commonNode.getChildNode('inrow')
            unit = commonNode.getChildNode('unit')
            bonusLimit = commonNode.getChildNode('bonusLimit')
            cumulative = commonNode.getChildNode('cumulative')
            vehicleKills = commonNode.getChildNode('vehicleKills')
            battles = commonNode.getChildNode('battles')
            battleCount = battles.getChildNode('count').getFirstChildValue() if battles else None
            if bonusLimit is None:
                bonusLimitNode = XMLNode('bonusLimit')
                bonusLimitNode.addChild(1 if eventType in EVENT_TYPE.ONE_BONUS_QUEST else MAX_BONUS_LIMIT)
                commonNode.addChild(bonusLimitNode)
            if eventType in EVENT_TYPE.LIKE_BATTLE_QUESTS:
                if (cumulative or unit or vehicleKills) and inrow:
                    raise Exception('battleQuest: Unexpected tags (vehicleKills, cumulative, unit/cumulative) with inrow')
                if not (cumulative or unit or vehicleKills or bonusLimit or battles) and (daily or groupBy):
                    raise Exception('battleQuest: daily and groupBy should be used with cumulative, unit, vehicleKills, bonusLimit or battles tags')
                if battles and not battleCount:
                    raise Exception('Invalid battles section')
            elif eventType in EVENT_TYPE.LIKE_TOKEN_QUESTS:
                if cumulative or unit or vehicleKills or groupBy or battles:
                    raise Exception('tokenQuest: Unexpected tags (cumulative, unit, vehicleKills, groupBy, battles)')
                if not bonusLimit and daily:
                    raise Exception('tokenQuest: daily should be used with bonusLimit tag')
            mainNode.bonus = walkBonuses(readBonusSection(availableBonuses, questSection['bonus'], eventType), FilterVisitor(eventType))
            questClientData = dict(info)
            questClientData['bonus'] = deepcopy(mainNode.bonus)
            questClientData['conditions'] = mainNode.questClientConditions
            if mainNode.groupContent:
                questClientData['groupContent'] = mainNode.groupContent
            self.__stripServerQuestData(questClientData)
            mainNode.info['questClientData'] = questClientData
            nodes.setdefault(eventType, []).append(mainNode)

        return nodes

    def __stripServerQuestData(self, questClientData):
        questClientData.pop('serverOnly', None)
        questClientData['bonus'] = walkBonuses(questClientData['bonus'], StripVisitor())
        return

    def __readHeader(self, eventType, questSection, curTime, gStartTime, gFinishTime):
        id = questSection.readString('id', '')
        if not id:
            raise Exception('Quest id must be specified.')
        if questSection.has_key('name'):
            questName = self.__readMetaSection(questSection['name'])
        else:
            questName = ''
        if questSection.has_key('description'):
            description = self.__readMetaSection(questSection['description'])
        else:
            description = ''
        startTime = readUTC(questSection, 'startTime', gStartTime)
        finishTime = readUTC(questSection, 'finishTime', gFinishTime)
        progressExpiryTime = readUTC(questSection, 'progressExpiryTime', finishTime)
        defaultAnnounceTime = gStartTime if gStartTime != DEFAULT_QUEST_START_TIME else startTime
        announceTime = readUTC(questSection, 'announceTime', defaultAnnounceTime)
        weekDayNames = questSection.readString('weekDays', '').split()
        weekDays = set([ _WEEKDAYS[val] for val in weekDayNames ])
        intervalsInString = questSection.readString('activeTimeIntervals', '').split()
        makeHM = lambda hm: tuple((int(v) for v in hm.split(':')))
        makeIntervals = lambda intervals: tuple((makeHM(v) for v in intervals.split('_')))
        activeTimeIntervals = [ makeIntervals(i) for i in intervalsInString ]
        if announceTime < gStartTime:
            raise Exception('Invalid announce time. announceTime:%s < gStartTime:%s' % (announceTime, gStartTime))
        if startTime < announceTime:
            raise Exception('Invalid announce time. startTime:%s < announceTime:%s' % (startTime, announceTime))
        if startTime < gStartTime:
            raise Exception('Invalid start time. startTime:%s < gStartTime:%s' % (startTime, gStartTime))
        if finishTime > gFinishTime:
            raise Exception('Invalid finish time. finishTime:%s > gFinishTime:%s' % (finishTime, gFinishTime))
        if progressExpiryTime < finishTime:
            raise Exception('Invalid progress expiry time. progressExpiryTime:%s < finishTime:%s' % (progressExpiryTime, finishTime))
        requiredToken = questSection.readString('requiredToken', '')
        if eventType == EVENT_TYPE.PERSONAL_QUEST:
            if not requiredToken:
                raise Exception('Personal quest must contain tag <requiredToken> with not empty token')
        runFlags = []
        if questSection.has_key('run'):
            for flagName, flagValue in questSection['run'].items():
                if flagName == 'on':
                    runFlags.append(QUEST_RUN_FLAGS.NAME_TO_TYPE[flagValue.asString])

        tOption = curTime > time.time()
        showCongrats = questSection.readBool('showCongrats', eventType in (EVENT_TYPE.POTAPOV_QUEST,))
        info = {'id': id,
         'hidden': questSection.readBool('hidden', False),
         'serverOnly': questSection.readBool('serverOnly', False),
         'name': questName,
         'type': eventType,
         'description': description,
         'progressExpiryTime': progressExpiryTime,
         'weekDays': weekDays,
         'activeTimeIntervals': activeTimeIntervals,
         'startTime': startTime if not tOption else time.time() - 300,
         'finishTime': finishTime,
         'announceTime': announceTime,
         'disableGui': questSection.readBool('disableGui', False),
         'showCongrats': showCongrats,
         'requiredToken': requiredToken,
         'Toption': None if not tOption else startTime,
         'priority': questSection.readInt('priority', 0),
         'uiDecoration': questSection.readInt('uiDecoration', 0),
         'runFlags': runFlags}
        if eventType == EVENT_TYPE.MOTIVE_QUEST:
            extraSubsectionsNames = ('advice', 'requirements', 'congratulation')
            for subsectionName in extraSubsectionsNames:
                if questSection.has_key(subsectionName):
                    info[subsectionName] = self.__readMetaSection(questSection[subsectionName])

        if eventType == EVENT_TYPE.RANKED_QUEST:
            if finishTime > curTime + _YEAR:
                raise Exception("'finishTime' section is missing or too far into the future", info['id'])
            seasonSectionName = 'conditions/common/season'
            if questSection.has_key(seasonSectionName):
                season = questSection[seasonSectionName].asInt
            else:
                raise Exception("'season' condition is compulsory", info['id'])
            cycleSectionName = 'conditions/common/cycle'
            if questSection.has_key(cycleSectionName):
                cycle = questSection[cycleSectionName].asInt
            else:
                cycle = None
            info['subtype'] = questSection['subtype'].asString
            info['ranked'] = (season, cycle)
        if eventType in EVENT_TYPE.QUESTS_WITH_SHOP_BUTTON:
            info['shopButton'] = questSection.readString('shopButton', 'hide')
        return info

    def __readGroupContent(self, questSection):
        if not questSection.has_key('groupContent'):
            raise Exception("'groupContent' section is compulsory")
        return questSection.readString('groupContent').split()

    def __getConditionReaders(self, eventType):
        condition_readers = {'greater': self.__readCondition_float,
         'equal': self.__readCondition_float,
         'less': self.__readCondition_float,
         'lessOrEqual': self.__readCondition_float,
         'greaterOrEqual': self.__readCondition_float,
         'and': self.__readBattleResultsConditionList,
         'or': self.__readBattleResultsConditionList,
         'not': self.__readBattleResultsConditionList,
         'token': self.__readBattleResultsConditionList,
         'id': self.__readCondition_string,
         'consume': self.__readCondition_consume,
         'inClan': self.__readClanIds,
         'vehiclesUnlocked': self.__readBattleResultsConditionList,
         'vehiclesOwned': self.__readBattleResultsConditionList,
         'classes': self.__readVehicleFilter_classes,
         'levels': self.__readVehicleFilter_levels,
         'nations': self.__readVehicleFilter_nations,
         'types': self.__readVehicleFilter_types,
         'dossier': self.__readBattleResultsConditionList,
         'record': self.__readCondition_dossierRecord,
         'average': self.__readCondition_int,
         'GR': self.__readBattleResultsConditionList,
         'igrType': self.__readCondition_IGRType,
         'premium': self.__readCondition_bool,
         'daily': self.__readCondition_true,
         'bonusLimit': self.__readCondition_int,
         'refSystemRalXPPool': self.__readBattleResultsConditionList,
         'refSystemRalBought10Lvl': self.__readCondition_true}
        if eventType in EVENT_TYPE.LIKE_BATTLE_QUESTS:
            condition_readers.update({'win': self.__readCondition_true,
             'isAlive': self.__readCondition_true,
             'isSquad': self.__readCondition_bool,
             'clanMembership': self.__readCondition_string,
             'allAlive': self.__readCondition_true,
             'aliveCnt': self.__readCondition_int,
             'achievements': self.__readCondition_achievements,
             'hasReceivedMultipliedXP': self.__readCondition_bool,
             'multiDamageEvent': self.__readBattleResultsConditionList,
             'killedByShot': self.__readCondition_int,
             'damagedByShot': self.__readCondition_int,
             'multiStunEvent': self.__readBattleResultsConditionList,
             'stunnedByShot': self.__readCondition_int,
             'unitVehicleDamage': self.__readBattleResultsConditionList,
             'unitVehicleKills': self.__readBattleResultsConditionList,
             'unitVehicleDescr': self.__readBattleResultsConditionList,
             'vehicleDamage': self.__readBattleResultsConditionList,
             'vehicleStun': self.__readBattleResultsConditionList,
             'vehicleKills': self.__readBattleResultsConditionList,
             'vehicleDescr': self.__readBattleResultsConditionList,
             'clanKills': self.__readBattleResultsConditionList,
             'lvlDiff': self.__readCondition_int,
             'classesDiversity': self.__readCondition_int,
             'limittedTime': self.__readCondition_int,
             'rammingInfo': self.__readCondition_rammingInfo,
             'distance': self.__readCondition_int,
             'whileMoving': self.__readCondition_true,
             'whileEnemyMoving': self.__readCondition_int,
             'soloAssist': self.__readCondition_true,
             'fireStarted': self.__readCondition_true,
             'whileEnemyInvisible': self.__readCondition_true,
             'whileInvisible': self.__readCondition_true,
             'attackReason': self.__readCondition_attackReason,
             'enemyImmobilized': self.__readCondition_true,
             'enemyInvader': self.__readCondition_true,
             'eventCount': self.__readCondition_true,
             'whileFullHealth': self.__readCondition_true,
             'whileEnemyFullHealth': self.__readCondition_true,
             'allInSpecifiedClasses': self.__readCondition_true,
             'enemyIsNotSpotted': self.__readCondition_true,
             'whileEnemyWithFlag': self.__readCondition_true,
             'installedModules': self.__readBattleResultsConditionList,
             'guns': self.__readCondition_installedModules,
             'engines': self.__readCondition_installedModules,
             'chassis': self.__readCondition_installedModules,
             'turrets': self.__readCondition_installedModules,
             'radios': self.__readCondition_installedModules,
             'optionalDevice': self.__readCondition_installedModules,
             'correspondedCamouflage': self.__readCondition_true,
             'unit': self.__readBattleResultsConditionList,
             'results': self.__readBattleResultsConditionList,
             'key': self.__readCondition_keyResults,
             'max': self.__readCondition_int,
             'total': self.__readCondition_int,
             'compareWithMaxHealth': self.__readCondition_true,
             'plus': self.__readBattleResultsConditionList,
             'exceptUs': self.__readCondition_true,
             'compareWithDeathCount': self.__readCondition_true,
             'mapCamouflageKind': self.__readBattleFilter_CamouflageKind,
             'bonusTypes': self.__readBattleFilter_BonusTypes,
             'geometryNames': self.__readBattleFilter_GeometryNames,
             'battles': self.__readBattleResultsConditionList,
             'count': self.__readCondition_int,
             'upperLimit': self.__readCondition_true,
             'inrow': self.__readCondition_true,
             'groupBy': self.__readBattleResultsConditionList,
             'groupName': self.__readCondition_groupBy,
             'cumulative': self.__readCondition_cumulative,
             'crits': self.__readBattleResultsConditionList,
             'destroyed': self.__readBattleResultsConditionList,
             'tankman': self.__readBattleResultsConditionList,
             'critical': self.__readBattleResultsConditionList,
             'crit': self.__readBattleResultsConditionList,
             'critName': self.__readCritName})
        if eventType in (EVENT_TYPE.BATTLE_QUEST,):
            condition_readers.update({'red': self.__readClanIds,
             'silver': self.__readClanIds,
             'gold': self.__readClanIds,
             'black': self.__readClanIds})
        if eventType in (EVENT_TYPE.RANKED_QUEST,):
            condition_readers.update({'season': self.__readCondition_int,
             'cycle': self.__readCondition_int,
             'rank': self.__readCondition_int,
             'step': self.__readCondition_int,
             'maxRank': self.__readBattleResultsConditionList,
             'ladderPts': self.__readBattleResultsConditionList})
        return condition_readers

    def __getAvailableBonuses(self, eventType):
        bonusTypes = {'gold',
         'credits',
         'crystal',
         'freeXP',
         'item',
         'equipment',
         'slots',
         'berths',
         'premium',
         'token',
         'goodie',
         'vehicle',
         'dossier',
         'tankmen',
         'customizations'}
        if eventType in (EVENT_TYPE.BATTLE_QUEST, EVENT_TYPE.PERSONAL_QUEST):
            bonusTypes.update(('xp', 'tankmenXP', 'xpFactor', 'creditsFactor', 'freeXPFactor', 'tankmenXPFactor'))
        return bonusTypes

    def __readCondition_groupBy(self, _, section, node):
        s = section.asString
        if s not in ('vehicle', 'nation', 'class', 'level'):
            raise Exception('Unknown groupBy name %s' % s)
        node.addChild(s)

    def __readCondition_installedModules(self, _, section, node):
        modules = set()
        for module in section.asString.split():
            if ':' in module:
                nationName, name = module.split(':')
                nationID = nations.INDICES[nationName]
            else:
                if node.name != 'optionalDevice':
                    raise Exception('module must be like nation:inNationName')
                name = module
            if node.name == 'guns':
                nationModules = vehicles.g_cache.guns(nationID)
            elif node.name == 'engines':
                nationModules = vehicles.g_cache.engines(nationID)
            elif node.name == 'turrets':
                nationModules = vehicles.g_cache.turrets(nationID)
            elif node.name == 'chassis':
                nationModules = vehicles.g_cache.chassis(nationID)
            elif node.name == 'radios':
                nationModules = vehicles.g_cache.radios(nationID)
            elif node.name == 'optionalDevice':
                idx = vehicles.g_cache.optionalDeviceIDs()[name]
                modules.add(vehicles.g_cache.optionalDevices()[idx]['compactDescr'])
                break
            else:
                raise Exception('Unknown tag %s' % node.name)
            for descr in nationModules.itervalues():
                if descr['name'] == name:
                    modules.add(descr['compactDescr'])
                    break
            else:
                raise Exception('Unknown module(%s) %s' % (node.name, module))

        node.addChild(modules)

    def __readCritName(self, _, section, node):
        critName = section.asString
        if critName not in vehicles.VEHICLE_DEVICE_TYPE_NAMES + vehicles.VEHICLE_TANKMAN_TYPE_NAMES:
            raise Exception('Invalid crit name (%s)' % critName)
        node.addChild(critName)

    def __readCondition_cumulative(self, _, section, node):
        for name, sub in section.items():
            if name not in battle_results_shared.VEH_FULL_RESULTS.names() and name not in battle_results_shared.VEH_BASE_RESULTS.names():
                raise Exception("Unsupported misc variable '%s'" % name)
            node.addChild((name, int(sub.asFloat)))

    def __readBattleResultsConditionList(self, conditionReaders, section, node):
        for name, sub in section.items():
            if name in 'meta':
                node.questClientConditions.append(('meta', self.__readMetaSection(sub)))
                continue
            subNode = XMLNode(name)
            if name in ('greater', 'equal', 'less', 'lessOrEqual', 'greaterOrEqual'):
                subNode.relatedGroup = 'operator'
            conditionReaders[name](conditionReaders, sub, subNode)
            node.addChild(subNode)

    def __readCondition_achievements(self, _, section, node):
        dossierRecordDBIDs = set()
        for achievement in section.asString.split():
            values = achievement.split(':')
            if len(values) == 2:
                dossierRecordDBIDs.add(RECORD_DB_IDS[values[0], values[1]])
            raise Exception('Invalid achievement format (%s). Must be blockName:record.' % achievement)

        node.addChild(dossierRecordDBIDs)

    def __readCondition_string(self, _, section, node):
        node.addChild(section.asString)

    def __readCondition_rammingInfo(self, _, section, node):
        rammingConditions = set([ rammingCondition for rammingCondition in section.asString.split() ])
        for rammingCondition in rammingConditions:
            if rammingCondition not in ('stayedAlive', 'dealtMoreDamage'):
                raise Exception('Unsupported kill by ramming condition %s, must be one of (%s %s)' % (rammingCondition, 'stayedAlive', 'dealtMoreDamage'))

        node.addChild(rammingConditions)

    def __readCondition_dossierRecord(self, _, section, node):
        record = section.asString
        records = record.split(':')
        if len(records) == 2:
            blockName, rec = records
            for blockBuilder in accountDossierLayout + vehicleDossierLayout:
                if type(blockBuilder) not in (StaticSizeBlockBuilder, BinarySetDossierBlockBuilder):
                    continue
                if blockBuilder.name == blockName:
                    if rec in blockBuilder.recordsLayout or rec.startswith('tankExpert') or rec.startswith('mechanicEngineer'):
                        break
            else:
                raise Exception('Invalid dossier record %s' % (record,))

        else:
            raise Exception('Old or invalid dossier record format (%s)' % (record,))
        node.addChild(record)

    def __readCondition_keyResults(self, _, section, node):
        name = section.asString
        if name not in battle_results_shared.VEH_BASE_RESULTS.names() and name not in battle_results_shared.COMMON_RESULTS.names() and name not in battle_results_shared.VEH_FULL_RESULTS.names() and name not in battle_results_shared.AVATAR_BASE_RESULTS.names() and name not in battle_results_shared.AVATAR_FULL_RESULTS.names():
            raise Exception("Unsupported battle result variable '%s'" % name)
        node.addChild(name)

    def __readCondition_true(self, _, section, node):
        node.addChild(True)

    def __readCondition_bool(self, _, section, node):
        node.addChild(section.asBool)

    def __readCondition_int(self, _, section, node):
        node.addChild(section.asInt)

    def __readCondition_float(self, _, section, node):
        node.addChild(section.asFloat)

    def __readCondition_consume(self, _, section, node):
        node.addChild(section.asInt)
        node.addChild(section.has_key('force'))

    def __readCondition_attackReason(self, _, section, node):
        attackReason = section.asInt
        if not 0 <= attackReason < len(ATTACK_REASONS):
            raise Exception('Invalid attack reason index')
        node.addChild(section.asInt)

    def __readCondition_set(self, _, section, node):
        node.addChild(set([ int(id) for id in section.asString.split() ]))

    def __readCondition_IGRType(self, _, section, node):
        igrType = section.asInt
        if igrType not in IGR_TYPE.RANGE:
            raise Exception('Invalid IGR type %s' % (igrType,))
        node.addChild(igrType)

    def __readBattleFilter_GeometryNames(self, _, section, node):
        arenaIDs = []
        for geometryName in section.asString.split():
            initialLen = len(arenaIDs)
            for id, descr in ArenaType.g_cache.iteritems():
                if descr.geometryName == geometryName:
                    arenaIDs.append(id)

            if initialLen == len(arenaIDs):
                raise Exception('Unknown geometry name %s' % geometryName)

        node.addChild(set(arenaIDs))

    def __readBattleFilter_BonusTypes(self, _, section, node):
        res = set()
        for bonusType in section.asString.split():
            if int(bonusType) not in ARENA_BONUS_TYPE.RANGE:
                raise Exception('Unknown bonus type %s' % bonusType)
            res.add(int(bonusType))

        node.addChild(res)

    def __readBattleFilter_CamouflageKind(self, _, section, node):
        camouflageKindLst = set([ vehicles.CAMOUFLAGE_KINDS[c] for c in section.asString.split() ])
        node.addChild(camouflageKindLst)

    def __readVehicleFilter_classes(self, _, section, node):
        classes = set([ VEHICLE_CLASS_INDICES[cls] for cls in section.asString.split() ])
        node.addChild(classes)

    def __readVehicleFilter_levels(self, _, section, node):
        res = set()
        for level in section.asString.split():
            if 1 <= int(level) <= 10:
                res.add(int(level))
            raise Exception('Unsupported vehicle level %s' % level)

        node.addChild(res)

    def __readClanIds(self, _, section, node):
        node.addChild(set([ int(val) for val in section.asString.split() ]))

    def __readVehicleFilter_nations(self, _, section, node):
        nationsLst = set([ nations.INDICES[nation] for nation in section.asString.split() ])
        node.addChild(nationsLst)

    def __readVehicleFilter_types(self, _, section, node):
        node.addChild(set(self.__readVehicleTypeList(section)))

    def __readVehicleTypeList(self, section):
        typeNames = section.asString.split()
        return [ vehicles.makeVehicleTypeCompDescrByName(typeName) for typeName in typeNames ]

    def __readMetaSection(self, section):
        if section is None:
            return {}
        else:
            meta = {}
            for local, sub in section.items():
                meta[local.strip()] = sub.readString('', '').strip()

            return meta
