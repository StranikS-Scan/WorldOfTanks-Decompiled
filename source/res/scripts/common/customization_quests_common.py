# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/customization_quests_common.py
from typing import Dict, Optional
from copy import deepcopy
from items import vehicles
from constants import CUSTOMIZATION_PROGRESS_PREFIX as PREFIX, EVENT_TYPE
from items.components.c11n_components import CustomizationType, QuestProgressForCustomization as qpc
SEPARATOR = '_'
TEMPLATE = PREFIX + SEPARATOR.join(['{styleId}', '{groupID}'])

def validateToken(token):
    if not token.startswith(PREFIX):
        return False
    words = token[len(PREFIX):].split(SEPARATOR)
    return False if len([ int(x) for x in words if x.isdigit() ]) != 2 else True


def serializeToken(styleId, group):
    return TEMPLATE.format(styleId=styleId, groupID=group)


def deserializeToken(token):
    ws = token[len(PREFIX):].split(SEPARATOR)
    return (int(ws[0]), int(ws[1]))


def validateCustomizationQuestToken(id, token):
    if validateToken(id):
        if token['count'] > 0 and not ('limit' in token and token['limit'] == token['count']):
            return (False, 'Use limits equale count for token: {}, count {}'.format(id, token['count']))
        styleId, groupId = deserializeToken(id)
        questStyles = vehicles.g_cache.customization20().getQuestProgressionStyles()
        if styleId not in questStyles:
            return (False, 'Invalid styleId token format: {}'.format(id))
        if id not in questStyles[styleId].questsProgression.getGroupTokens():
            return (False, 'Invalid groupId token format: {}'.format(id))
    return (True, '')


class CustQuestsCache(object):
    __slots__ = ('_groupByToken',)

    def __init__(self, groupByToken=None):
        if groupByToken is None:
            self._groupByToken = groupByToken = {}
            cache = vehicles.g_cache.customization20()
            for _, style in cache.getQuestProgressionStyles().iteritems():
                qp = style.questsProgression
                for tokenId in qp.getGroupTokens():
                    groupByToken[tokenId] = [ {'finishTime': finishTime,
                     'questIds': {et:[] for et in EVENT_TYPE.QUEST_USE_FOR_C11N_PROGRESS}} for finishTime in qp.getFinishTimes(tokenId) ]

        else:
            self._groupByToken = groupByToken
        return

    def addQuest(self, et, quest):
        if et not in EVENT_TYPE.QUEST_USE_FOR_C11N_PROGRESS:
            return
        cache = vehicles.g_cache.customization20()
        groupByToken = self._groupByToken
        for tokenId, info in quest['bonus'].get('tokens', {}).iteritems():
            if validateToken(tokenId):
                styleId, groupId = deserializeToken(tokenId)
                if tokenId not in groupByToken:
                    continue
                qp = cache.itemTypes[CustomizationType.STYLE][styleId].questsProgression
                level = qp.getLevel(tokenId, info['count'])
                groupByToken[tokenId][level]['questIds'][et].append(quest['info']['id'])

    def setFinishTime(self, tokenId, level, finishTime):
        if tokenId in self._groupByToken:
            levels = self._groupByToken[tokenId]
            if -1 < level < len(levels):
                levels[level]['finishTime'] = finishTime

    def __iter__(self):
        for token, levels in self._groupByToken.iteritems():
            for i, level in enumerate(levels):
                for et, questIds in level['questIds'].iteritems():
                    for id in questIds:
                        yield (token,
                         i,
                         et,
                         level['finishTime'],
                         id)

    def asDict(self):
        return self._groupByToken

    def copy(self):
        return CustQuestsCache(deepcopy(self._groupByToken))

    def updateQuests(self, custQuestCache):
        groupByToken = self._groupByToken
        for tokenId, levelsCombine in custQuestCache.asDict().iteritems():
            if tokenId not in groupByToken:
                groupByToken[tokenId] = deepcopy(levelsCombine)
                continue
            for level, info in enumerate(levelsCombine):
                destination = groupByToken[tokenId][level]
                for et in EVENT_TYPE.QUEST_USE_FOR_C11N_PROGRESS:
                    questIds = info['questIds'][et]
                    if questIds:
                        destination['questIds'][et] = deepcopy(questIds)
