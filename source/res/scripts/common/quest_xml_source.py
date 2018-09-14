# Embedded file name: scripts/common/quest_xml_source.py
import time
import items
import ResMgr
import nations
import ArenaType
import battle_results_shared
from functools import partial
from dossiers2.custom.layouts import accountDossierLayout, vehicleDossierLayout, StaticSizeBlockBuilder, DictBlockBuilder, ListBlockBuilder, BinarySetDossierBlockBuilder
from dossiers2.custom.records import RECORD_DB_IDS
from account_shared import validateCustomizationItem
from items import vehicles, tankmen
from constants import VEHICLE_CLASS_INDICES, ARENA_BONUS_TYPE, EVENT_TYPE, IGR_TYPE, ATTACK_REASONS, FORT_QUEST_SUFFIX
_WEEKDAYS = {'Mon': 1,
 'Tue': 2,
 'Wed': 3,
 'Thu': 4,
 'Fri': 5,
 'Sat': 6,
 'Sun': 7}
MAX_BONUS_LIMIT = 1000000

class XMLNode:
    __slots__ = ('name', 'value', 'questClientConditions', 'relatedGroup', 'info', 'bonus', 'groupContent')

    def __init__(self, name = ''):
        self.name = name
        self.value = []
        self.questClientConditions = []
        self.relatedGroup = ''
        self.info = {}
        self.bonus = {}
        self.groupContent = None
        return

    def getChildNode(self, name, relatedGroup = None):
        childNode = None
        for subnode in self.value:
            if not isinstance(subnode, XMLNode):
                continue
            if subnode.name == name or relatedGroup is not None and subnode.relatedGroup == relatedGroup:
                childNode = subnode
                break

        return childNode

    def getFirstChildValue(self):
        if len(self.value) == 0:
            return None
        else:
            return self.value[0]

    def isExistChildNode(self, nodeName):
        for child in self.value:
            if isinstance(child, XMLNode):
                if child.name == nodeName or child.isExistChildNode(nodeName):
                    return True

        return False

    def addChild(self, childNode, needClientInfo = True):
        self.value.append(childNode)
        if not needClientInfo:
            return
        if isinstance(childNode, XMLNode):
            self.questClientConditions.append((childNode.name, childNode.questClientConditions))
        else:
            self.questClientConditions.append(('value', childNode))


class Source:

    def __init__(self):
        pass

    def readFromExternalFile(self, path, gStartTime, gFinishTime, curTime):
        ResMgr.purge(path)
        section = ResMgr.openSection(path)
        if section is None:
            raise Exception, "Can not open '%s'" % path
        return self.__readXML(section, gStartTime, gFinishTime, curTime)

    def readFromInternalFile(self, path, curTime):
        ResMgr.purge(path)
        section = ResMgr.openSection(path)
        if section is None:
            raise Exception, "Can not open '%s'" % path
        if not section.has_key('quests'):
            return {}
        else:
            gStartTime = 1
            gFinishTime = 4102444800L
            return self.__readXML(section['quests'], gStartTime, gFinishTime, curTime)

    def __readXML(self, section, gStartTime, gFinishTime, curTime):
        nodes = {}
        for typeName, questSection in section.items():
            enabled = questSection.readBool('enabled', False)
            if not enabled:
                continue
            eventType = EVENT_TYPE.NAME_TO_TYPE[typeName]
            mainNode = XMLNode('main')
            mainNode.info = info = self.__readHeader(eventType, questSection, gStartTime, gFinishTime, curTime)
            if eventType == EVENT_TYPE.GROUP:
                mainNode.groupContent = tuple(self.__readGroupContent(questSection))
            conditionReaders = self.__getConditionReaders(eventType)
            bonusReaders = self.__getBonusReaders(eventType)
            bonusNode = XMLNode('bonus')
            prebattleNode = XMLNode('preBattle')
            prebattleNode.addChild(bonusNode, False)
            mainNode.addChild(prebattleNode)
            accountNode = XMLNode('account')
            prebattleNode.addChild(accountNode)
            vehicleNode = XMLNode('vehicle')
            prebattleNode.addChild(vehicleNode)
            battleNode = XMLNode('battle')
            prebattleNode.addChild(battleNode)
            postbattleNode = XMLNode('postBattle')
            mainNode.addChild(postbattleNode)
            postbattleNode.addChild(bonusNode, False)
            mainNode.addChild(bonusNode)
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
            if conditions and conditions.has_key('bonus'):
                condition = conditions['bonus']
                self.__readBattleResultsConditionList(conditionReaders, condition, bonusNode)
            daily = bonusNode.getChildNode('daily')
            info['isDaily'] = daily is not None
            groupBy = bonusNode.getChildNode('groupBy')
            info['groupBy'] = groupBy.getChildNode('groupName').getFirstChildValue() if groupBy else None
            info['isIGR'] = accountNode.isExistChildNode('igrType')
            inrow = bonusNode.getChildNode('inrow')
            unit = bonusNode.getChildNode('unit')
            bonusLimit = bonusNode.getChildNode('bonusLimit')
            cumulative = bonusNode.getChildNode('cumulative')
            vehicleKills = bonusNode.getChildNode('vehicleKills')
            battles = bonusNode.getChildNode('battles')
            battleCount = battles.getChildNode('count').getFirstChildValue() if battles else None
            if bonusLimit is None:
                bonusLimitNode = XMLNode('bonusLimit')
                bonusLimitNode.addChild(1 if eventType in EVENT_TYPE.ONE_BONUS_QUEST else MAX_BONUS_LIMIT)
                bonusNode.addChild(bonusLimitNode)
            if eventType in EVENT_TYPE.LIKE_BATTLE_QUESTS:
                if (cumulative or unit or vehicleKills) and inrow:
                    raise Exception, 'battleQuest: Unexpected tags (vehicleKills, cumulative, unit/cumulative) with inrow'
                if not (cumulative or unit or vehicleKills or bonusLimit or battles) and (daily or groupBy):
                    raise Exception, 'battleQuest: daily and groupBy should be used with cumulative, unit, vehicleKills, bonusLimit or battles tags'
                if battles and not battleCount:
                    raise Exception, 'Invalid battles section'
            elif eventType in EVENT_TYPE.LIKE_TOKEN_QUESTS:
                if cumulative or unit or vehicleKills or groupBy or battles:
                    raise Exception, 'tokenQuest: Unexpected tags (cumulative, unit, vehicleKills, groupBy, battles)'
                if not bonusLimit and daily:
                    raise Exception, 'tokenQuest: daily should be used with bonusLimit tag'
            mainNode.bonus = self.__readBonusSection(bonusReaders, eventType, questSection['bonus'], gFinishTime)
            questClientData = dict(info)
            questClientData.pop('serverOnly', None)
            questClientData['bonus'] = mainNode.bonus
            questClientData['conditions'] = mainNode.questClientConditions
            if mainNode.groupContent:
                questClientData['groupContent'] = mainNode.groupContent
            mainNode.info['questClientData'] = questClientData
            nodes.setdefault(eventType, []).append(mainNode)

        return nodes

    def __readHeader(self, eventType, questSection, gStartTime, gFinishTime, curTime):
        id = questSection.readString('id', '')
        if not id:
            raise Exception, 'Quest id must be specified.'
        if questSection.has_key('name'):
            questName = self.__readMetaSection(questSection['name'])
        else:
            questName = ''
        if questSection.has_key('description'):
            description = self.__readMetaSection(questSection['description'])
        else:
            description = ''
        progressExpiryTime = self.__generateUTC(questSection.readString('progressExpiryTime'), 'progressExpiryTime', gFinishTime)
        startTime = self.__generateUTC(questSection.readString('startTime'), 'startTime', gStartTime)
        finishTime = self.__generateUTC(questSection.readString('finishTime'), 'finishTime', gFinishTime)
        weekDayNames = questSection.readString('weekDays', '').split()
        weekDays = set([ _WEEKDAYS[val] for val in weekDayNames ])
        intervalsInString = questSection.readString('activeTimeIntervals', '').split()
        makeHM = lambda hm: tuple((int(v) for v in hm.split(':')))
        makeIntervals = lambda intervals: tuple((makeHM(v) for v in intervals.split('_')))
        activeTimeIntervals = [ makeIntervals(i) for i in intervalsInString ]
        if startTime < gStartTime:
            raise Exception, 'Invalid start time. startTime:%s < gStartTime:%s' % (startTime, gStartTime)
        if finishTime > gFinishTime:
            raise Exception, 'Invalid finish time. finishTime:%s > gFinishTime:%s' % (finishTime, gFinishTime)
        if progressExpiryTime < gFinishTime:
            raise Exception, 'Invalid progress expiry time. progressExpiryTime:%s < gFinishTime:%s' % (progressExpiryTime, gFinishTime)
        requiredToken = questSection.readString('requiredToken', '')
        if eventType == EVENT_TYPE.PERSONAL_QUEST:
            if not requiredToken:
                raise Exception, 'Personal quest must contain tag <requiredToken> with not empty token'
        if eventType == EVENT_TYPE.FORT_QUEST:
            if FORT_QUEST_SUFFIX not in id:
                raise Exception, 'Fort quest must contain "stronghold" in its id.'
        elif FORT_QUEST_SUFFIX in id:
            raise Exception, 'Quest must not contain "stronghold" in its id.'
        tOption = curTime > time.localtime()
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
         'gStartTime': gStartTime,
         'gFinishTime': gFinishTime,
         'disableGui': questSection.readBool('disableGui', False),
         'requiredToken': requiredToken,
         'Toption': None if not tOption else startTime,
         'priority': questSection.readInt('priority', 0),
         'uiDecoration': questSection.readInt('uiDecoration', 0)}
        return info

    def __readGroupContent(self, questSection):
        if not questSection.has_key('groupContent'):
            raise Exception("'groupContent' section is compulsory")
        return questSection.readString('groupContent').split()

    def __getConditionReaders(self, eventType):
        condition_readers = {'greater': self.__readCondition_int,
         'equal': self.__readCondition_int,
         'less': self.__readCondition_int,
         'lessOrEqual': self.__readCondition_int,
         'greaterOrEqual': self.__readCondition_int,
         'and': self.__readBattleResultsConditionList,
         'or': self.__readBattleResultsConditionList,
         'not': self.__readBattleResultsConditionList,
         'token': self.__readBattleResultsConditionList,
         'id': self.__readCondition_string,
         'consume': self.__readCondition_consume,
         'clanIDs': self.__readClanIds,
         'inClan': self.__readBattleResultsConditionList,
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
             'unitVehicleDamage': self.__readBattleResultsConditionList,
             'unitVehicleKills': self.__readBattleResultsConditionList,
             'unitVehicleDescr': self.__readBattleResultsConditionList,
             'vehicleDamage': self.__readBattleResultsConditionList,
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
             'installedModules': self.__readBattleResultsConditionList,
             'guns': self.__readCondition_installedModules,
             'engines': self.__readCondition_installedModules,
             'chassis': self.__readCondition_installedModules,
             'turrets': self.__readCondition_installedModules,
             'radios': self.__readCondition_installedModules,
             'optionalDevice': self.__readCondition_installedModules,
             'correspondedCamouflage': self.__readCondition_true,
             'historicalBattleIDs': self.__readCondition_set,
             'unit': self.__readBattleResultsConditionList,
             'results': self.__readBattleResultsConditionList,
             'key': self.__readCondition_keyResults,
             'max': self.__readCondition_int,
             'total': self.__readCondition_int,
             'compareWithMaxHealth': self.__readCondition_true,
             'plus': self.__readBattleResultsConditionList,
             'exceptUs': self.__readCondition_true,
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
        return condition_readers

    def __getBonusReaders(self, eventType):
        bonus_readers = {'gold': self.__readBonus_int,
         'credits': self.__readBonus_int,
         'freeXP': self.__readBonus_int,
         'item': self.__readBonus_item,
         'equipment': self.__readBonus_equipment,
         'slots': self.__readBonus_int,
         'berths': self.__readBonus_int,
         'premium': self.__readBonus_int,
         'token': self.__readBonus_tokens,
         'goodie': self.__readBonus_goodies,
         'vehicle': partial(self.__readBonus_vehicle, eventType),
         'dossier': self.__readBonus_dossier,
         'tankmen': partial(self.__readBonus_tankmen, eventType),
         'customizations': partial(self.__readBonus_customizations, eventType)}
        if eventType in (EVENT_TYPE.BATTLE_QUEST, EVENT_TYPE.FORT_QUEST, EVENT_TYPE.PERSONAL_QUEST):
            bonus_readers.update({'xp': self.__readBonus_int,
             'tankmenXP': self.__readBonus_int,
             'xpFactor': self.__readBonus_factor,
             'creditsFactor': self.__readBonus_factor,
             'freeXPFactor': self.__readBonus_factor,
             'tankmenXPFactor': self.__readBonus_factor})
        return bonus_readers

    def __readCondition_groupBy(self, _, section, node):
        s = section.asString
        if s not in ('vehicle', 'nation', 'class', 'level'):
            raise Exception, 'Unknown groupBy name %s' % s
        node.addChild(s)

    def __readCondition_installedModules(self, _, section, node):
        modules = set()
        for module in section.asString.split():
            if ':' in module:
                nationName, name = module.split(':')
                nationID = nations.INDICES[nationName]
            else:
                if node.name != 'optionalDevice':
                    raise Exception, 'module must be like nation:inNationName'
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
                raise Exception, 'Unknown tag %s' % node.name
            for descr in nationModules.itervalues():
                if descr['name'] == name:
                    modules.add(descr['compactDescr'])
                    break
            else:
                raise Exception, 'Unknown module(%s) %s' % (node.name, module)

        node.addChild(modules)

    def __readCritName(self, _, section, node):
        critName = section.asString
        if critName not in vehicles.VEHICLE_DEVICE_TYPE_NAMES + vehicles.VEHICLE_TANKMAN_TYPE_NAMES:
            raise Exception, 'Invalid crit name (%s)' % critName
        node.addChild(critName)

    def __readCondition_cumulative(self, _, section, node):
        for name, sub in section.items():
            if name not in battle_results_shared.VEH_FULL_RESULTS.names():
                raise Exception, "Unsupported misc variable '%s'" % name
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
            else:
                raise Exception, 'Invalid achievement format (%s). Must be blockName:record.' % achievement

        node.addChild(dossierRecordDBIDs)

    def __readCondition_string(self, _, section, node):
        node.addChild(section.asString)

    def __readCondition_rammingInfo(self, _, section, node):
        rammingConditions = set([ rammingCondition for rammingCondition in section.asString.split() ])
        for rammingCondition in rammingConditions:
            if rammingCondition not in ('stayedAlive', 'dealtMoreDamage'):
                raise Exception, 'Unsupported kill by ramming condition %s, must be one of (%s %s)' % (rammingCondition, 'stayedAlive', 'dealtMoreDamage')

        node.addChild(rammingConditions)

    def __readCondition_dossierRecord(self, _, section, node):
        record = section.asString
        records = record.split(':')
        if len(records) == 2:
            blockName, rec = records
            for blockBuilder in accountDossierLayout + vehicleDossierLayout:
                if type(blockBuilder) != StaticSizeBlockBuilder:
                    continue
                if blockBuilder.name == blockName:
                    if rec in blockBuilder.recordsLayout or rec.startswith('tankExpert') or rec.startswith('mechanicEngineer'):
                        break
            else:
                raise Exception, 'Invalid dossier record %s' % (record,)

        else:
            raise Exception, 'Old or invalid dossier record format (%s)' % (record,)
        node.addChild(record)

    def __readCondition_keyResults(self, _, section, node):
        name = section.asString
        if name not in battle_results_shared.VEH_BASE_RESULTS.names() and name not in battle_results_shared.COMMON_RESULTS.names() and name not in battle_results_shared.VEH_FULL_RESULTS.names():
            raise Exception, "Unsupported battle result variable '%s'" % name
        node.addChild(name)

    def __readCondition_true(self, _, section, node):
        node.addChild(True)

    def __readCondition_bool(self, _, section, node):
        node.addChild(section.asBool)

    def __readCondition_int(self, _, section, node):
        node.addChild(section.asInt)

    def __readCondition_consume(self, _, section, node):
        node.addChild(section.asInt)
        node.addChild(section.has_key('force'))

    def __readCondition_attackReason(self, _, section, node):
        attackReason = section.asInt
        if not 0 <= attackReason < len(ATTACK_REASONS):
            raise Exception, 'Invalid attack reason index'
        node.addChild(section.asInt)

    def __readCondition_set(self, _, section, node):
        node.addChild(set([ int(id) for id in section.asString.split() ]))

    def __readCondition_IGRType(self, _, section, node):
        igrType = section.asInt
        if igrType not in IGR_TYPE.RANGE:
            raise Exception, 'Invalid IGR type %s' % (igrType,)
        node.addChild(igrType)

    def __readBattleFilter_GeometryNames(self, _, section, node):
        arenaIDs = []
        for geometryName in section.asString.split():
            initialLen = len(arenaIDs)
            for id, descr in ArenaType.g_cache.iteritems():
                if descr.geometryName == geometryName:
                    arenaIDs.append(id)

            if initialLen == len(arenaIDs):
                raise Exception, 'Unknown geometry name %s' % geometryName

        node.addChild(set(arenaIDs))

    def __readBattleFilter_BonusTypes(self, _, section, node):
        res = set()
        for bonusType in section.asString.split():
            if int(bonusType) not in ARENA_BONUS_TYPE.RANGE:
                raise Exception, 'Unknown bonus type %s' % bonusType
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
            else:
                raise Exception, 'Unsupported vehicle level %s' % level

        node.addChild(res)

    def __readClanIds(self, _, section, node):
        node.addChild(set([ int(val) for val in section.asString.split() ]))

    def __readVehicleFilter_nations(self, _, section, node):
        nationsLst = set([ nations.INDICES[nation] for nation in section.asString.split() ])
        node.addChild(nationsLst)

    def __readVehicleFilter_types(self, _, section, node):
        node.addChild(set(self.__readVehicleTypeList(section)))

    def __readVehicleTypeList(self, section):
        res = []
        typeNames = section.asString.split()
        for typeName in typeNames:
            nationIdx, innationIdx = vehicles.g_list.getIDsByName(typeName)
            vehType = vehicles.g_cache.vehicle(nationIdx, innationIdx)
            res.append(vehType.compactDescr)

        return res

    def __readBonus_int(self, bonus, name, section, _gFinishTime):
        value = section.asInt
        if value <= 0:
            raise Exception, 'Negative value (%s)' % name
        bonus[name] = section.asInt

    def __readBonus_factor(self, bonus, name, section, _gFinishTime):
        value = section.asFloat
        if value <= 0:
            raise Exception, 'Negative value (%s)' % name
        bonus[name] = value

    def __readBonus_equipment(self, bonus, _name, section, _gFinishTime):
        eqName = section.asString
        cache = vehicles.g_cache
        eqID = cache.equipmentIDs().get(eqName)
        if eqID is None:
            raise Exception, "Unknown equipment '%s'" % eqName
        eqCompDescr = cache.equipments()[eqID].compactDescr
        count = 1
        if section.has_key('count'):
            count = section['count'].asInt
        bonus.setdefault('items', {})[eqCompDescr] = count
        return

    def __readBonus_item(self, bonus, _name, section, _gFinishTime):
        compDescr = section.asInt
        try:
            descr = vehicles.getDictDescr(compDescr)
            if descr['itemTypeName'] not in items.SIMPLE_ITEM_TYPE_NAMES:
                raise Exception, 'Wrong compact descriptor (%d). Not simple item.' % compDescr
        except:
            raise Exception, 'Wrong compact descriptor (%d)' % compDescr

        count = 1
        if section.has_key('count'):
            count = section['count'].asInt
        bonus.setdefault('items', {})[compDescr] = count

    def __readBonus_vehicle(self, eventType, bonus, _name, section, gFinishTime):
        nationID, innationID = vehicles.g_list.getIDsByName(section.asString)
        vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationID, innationID)
        extra = {}
        if section.has_key('tankmen'):
            self.__readBonus_tankmen(eventType, extra, vehTypeCompDescr, section['tankmen'], gFinishTime)
        else:
            if section.has_key('noCrew'):
                extra['noCrew'] = True
            if section.has_key('crewLvl'):
                extra['crewLvl'] = section['crewLvl'].asInt
            if section.has_key('crewFreeXP'):
                extra['crewFreeXP'] = section['crewFreeXP'].asInt
        if section.has_key('rent'):
            self.__readBonus_rent(extra, None, section['rent'], gFinishTime)
        if section.has_key('customCompensation'):
            credits = section['customCompensation'].readInt('credits', 0)
            gold = section['customCompensation'].readInt('gold', 0)
            extra['customCompensation'] = (credits, gold)
        bonus.setdefault('vehicles', {})[vehTypeCompDescr] = extra
        return

    def __readBonus_tankmen(self, eventType, bonus, vehTypeCompDescr, section, _gFinishTime):
        lst = []
        for subsection in section.values():
            tmanDescr = subsection.asString
            if tmanDescr:
                try:
                    tman = tankmen.TankmanDescr(tmanDescr)
                    if type(vehTypeCompDescr) == int:
                        _, vehNationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
                        if vehNationID != tman.nationID or vehicleTypeID != tman.vehicleTypeID:
                            raise Exception, 'Vehicle and tankman mismatch.'
                except Exception as e:
                    raise Exception, 'Invalid tankmen compact descr. Error: %s' % (e,)

                lst.append(tmanDescr)
                continue
            tmanData = {'isFemale': subsection.readBool('isFemale', False),
             'firstNameID': subsection.readInt('firstNameID', -1),
             'lastNameID': subsection.readInt('lastNameID', -1),
             'role': subsection.readString('role', ''),
             'iconID': subsection.readInt('iconID', -1),
             'roleLevel': subsection.readInt('roleLevel', 50),
             'freeXP': subsection.readInt('freeXP', 0),
             'fnGroupID': subsection.readInt('fnGroupID', 0),
             'lnGroupID': subsection.readInt('lnGroupID', 0),
             'iGroupID': subsection.readInt('iGroupID', 0),
             'isPremium': subsection.readBool('isPremium', False),
             'nationID': subsection.readInt('nationID', -1),
             'vehicleTypeID': subsection.readInt('vehicleTypeID', -1),
             'skills': subsection.readString('skills', '').split(),
             'freeSkills': subsection.readString('freeSkills', '').split()}
            for record in ('firstNameID', 'lastNameID', 'iconID'):
                if tmanData[record] == -1:
                    tmanData[record] = None

            try:
                if type(vehTypeCompDescr) == int:
                    _, vehNationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
                    if vehNationID != tmanData['nationID'] or vehicleTypeID != tmanData['vehicleTypeID']:
                        raise Exception, 'Vehicle and tankman mismatch.'
                if eventType != EVENT_TYPE.POTAPOV_QUEST:
                    lst.append(tankmen.makeTmanDescrByTmanData(tmanData))
                else:
                    lst.append(tmanData)
            except Exception as e:
                raise Exception, '%s: %s' % (e, tmanData)

        bonus['tankmen'] = lst
        return

    def __readBonus_rent(self, bonus, _name, section, _gFinishTime):
        rent = {}
        if section.has_key('expires'):
            rent['expires'] = {}
            subsection = section['expires']
            if subsection.has_key('after'):
                rent['expires']['after'] = subsection['after'].asInt
            if subsection.has_key('at'):
                rent['expires']['at'] = subsection['at'].asInt
        if section.has_key('compensation'):
            credits = section['compensation'].readInt('credits', 0)
            gold = section['compensation'].readInt('gold', 0)
            rent['compensation'] = (credits, gold)
        bonus['rent'] = rent

    def __readBonus_customizations(self, eventType, bonus, _name, section, _gFinishTime):
        lst = []
        for subsection in section.values():
            custData = {'isPermanent': subsection.readBool('isPermanent', False),
             'value': subsection.readInt('value', 0),
             'custType': subsection.readString('custType', ''),
             'id': (subsection.readInt('nationID', -1), subsection.readInt('innationID', -1))}
            if subsection.has_key('boundVehicle'):
                custData['vehTypeCompDescr'] = vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName(subsection.readString('boundVehicle', '')))
            elif subsection.has_key('boundToCurrentVehicle'):
                if eventType in EVENT_TYPE.LIKE_TOKEN_QUESTS:
                    raise Exception, "Unsupported tag 'boundToCurrentVehicle' in 'like token' quests"
                custData['boundToCurrentVehicle'] = True
            if custData['custType'] == 'emblems':
                custData['id'] = custData['id'][1]
            isValid, reason = validateCustomizationItem(custData)
            if not isValid:
                raise Exception, reason
            if 'boundToCurrentVehicle' in custData:
                customization = vehicles.g_cache.customization
                if custData['custType'] == 'camouflages':
                    nationID, innationID = custData['id']
                    descr = customization(nationID)['camouflages'][innationID]
                    if descr['allow'] or descr['deny']:
                        raise Exception, 'Unsupported camouflage because allow and deny tags %s, %s, %s' % (custData, descr['allow'], descr['deny'])
                elif custData['custType'] == 'inscriptions':
                    nationID, innationID = custData['id']
                    groupName = customization(nationID)['inscriptions'][innationID][0]
                    allow, deny = customization(nationID)['inscriptionGroups'][groupName][3:5]
                    if allow or deny:
                        raise Exception, 'Unsupported inscription because allow and deny tags %s, %s, %s' % (custData, allow, deny)
                elif custData['custType'] == 'emblems':
                    innationID = custData['id']
                    groups, emblems, _ = vehicles.g_cache.playerEmblems()
                    allow, deny = groups[emblems[innationID][0]][4:6]
                    if allow or deny:
                        raise Exception, 'Unsupported inscription because allow and deny tags %s, %s, %s' % (custData, allow, deny)
            lst.append(custData)

        bonus['customizations'] = lst

    def __readBonus_tokens(self, bonus, _name, section, gFinishTime):
        id = section['id'].asString
        token = bonus.setdefault('tokens', {})[id] = {}
        expires = token.setdefault('expires', {})
        self.__readBonus_expires(id, expires, section, gFinishTime)
        if section.has_key('limit'):
            token['limit'] = section['limit'].asInt
        if section.has_key('count'):
            token['count'] = section['count'].asInt

    def __readBonus_goodies(self, bonus, _name, section, gFinishTime):
        id = section['id'].asInt
        goodie = bonus.setdefault('goodies', {})[id] = {}
        if section.has_key('limit'):
            goodie['limit'] = section['limit'].asInt
        if section.has_key('count'):
            goodie['count'] = section['count'].asInt
        else:
            goodie['count'] = 1

    def __readBonus_expires(self, id, expires, section, gFinishTime):
        if section['expires'].has_key('after'):
            expires['after'] = section['expires']['after'].asInt
        else:
            at = section['expires'].asString
            expires['at'] = self.__generateUTC(at, 'expires')
            if expires['at'] < gFinishTime:
                raise Exception('Invalid expiry time for %s: %s' % (id, at))

    def __readBonus_dossier(self, bonus, _name, section, _gFinishTime):
        blockName, record = section['name'].asString.split(':')
        operation = 'add'
        if section.has_key('type'):
            operation = section['type'].asString
        if operation not in ('add', 'append', 'set'):
            raise Exception, 'Invalid dossier record %s' % operation
        value = section['value'].asInt
        unique = False
        if section.has_key('unique'):
            unique = section['unique'].asBool
        for blockBuilder in accountDossierLayout + vehicleDossierLayout:
            if blockBuilder.name == blockName:
                blockType = type(blockBuilder)
                if blockType in (StaticSizeBlockBuilder, BinarySetDossierBlockBuilder):
                    if (record in blockBuilder.recordsLayout or record.startswith('tankExpert') or record.startswith('mechanicEngineer')) and operation in ('add', 'set'):
                        break
                elif blockType == DictBlockBuilder and operation == 'add':
                    break
                elif blockType == ListBlockBuilder and operation == 'append':
                    break
        else:
            raise Exception, 'Invalid dossier record %s or unsupported block' % (blockName + ':' + record,)

        bonus.setdefault('dossier', {})[blockName, record] = {'value': value,
         'unique': unique,
         'type': operation}

    def __readBonusSection(self, bonusReaders, eventType, section, gFinishTime):
        if section is None:
            return {}
        else:
            bonus = {}
            if eventType == EVENT_TYPE.FORT_QUEST:
                for name, sub in section.items():
                    if name.startswith('pack_'):
                        words = name.split('_')
                        if len(words) != 2:
                            raise Exception, 'Invalid pack format (pack_id, where id between 1 and 10)'
                        packID = int(words[1])
                        if not 1 <= packID <= 10:
                            raise Exception, 'Invalid pack format (pack_id, where id between 1 and 10)'
                        if packID in bonus:
                            raise Exception, 'Invalid pack. Already defined.'
                        bonus[packID] = self.__readBonusSubSection(bonusReaders, sub, gFinishTime)

            else:
                bonus = self.__readBonusSubSection(bonusReaders, section, gFinishTime)
            return bonus

    def __readBonusSubSection(self, bonusReaders, section, gFinishTime):
        if section is None:
            return {}
        else:
            bonus = {}
            for name, sub in section.items():
                if name in ('meta',):
                    bonus['meta'] = self.__readMetaSection(sub)
                    continue
                if name not in bonusReaders:
                    continue
                bonusReaders[name](bonus, name, sub, gFinishTime)

            return bonus

    def __readMetaSection(self, section):
        if section is None:
            return {}
        else:
            meta = {}
            for local, sub in section.items():
                meta[local.strip()] = sub.readString('', '').strip()

            return meta

    def __generateUTC(self, timeData, field, default = None):
        try:
            if timeData is None:
                raise Exception, 'Wrong timeData'
            if timeData != '':
                timeData = time.strptime(timeData, '%d.%m.%Y %H:%M')
                timeData = int(time.mktime(timeData))
            else:
                if default is None:
                    raise Exception, 'Wrong default'
                return default
        except:
            raise Exception, 'Invalid %s format (%s). Format must be like %s, for example 23.01.2011 00:00.' % (field, timeData, "'%d.%m.%Y %H:%M'")

        return timeData
