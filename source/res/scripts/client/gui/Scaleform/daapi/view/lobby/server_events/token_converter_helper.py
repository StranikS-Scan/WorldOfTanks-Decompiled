# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/token_converter_helper.py
from copy import deepcopy
from typing import TYPE_CHECKING, NamedTuple
from optional_bonuses import TrackVisitor
if TYPE_CHECKING:
    from typing import Dict
    from gui.server_events.event_items import Quest

def convertTokens(token, bonusTokens, convertionData):
    convertion = TokenConvertionData(**convertionData)
    wasUsed = False
    if not convertion.tokenTo or token not in bonusTokens:
        return wasUsed
    tokenBonusData = bonusTokens[token]
    count = tokenBonusData['count']
    if convertion.limit:
        convertCount = min(convertion.limit, count)
        if convertion.limit <= count:
            wasUsed = True
        else:
            convertionData['limit'] -= count
    else:
        convertCount = count
    if convertCount == count:
        bonusTokens.pop(token)
    else:
        tokenBonusData['count'] -= convertCount
    newCount = bonusTokens.get(convertion.tokenTo, {}).get('count', 0) + int(round(convertCount * convertion.rate))
    bonusTokens.setdefault(convertion.tokenTo, deepcopy(tokenBonusData))['count'] = newCount
    return wasUsed


def convertTokensInBonusData(event, bonusData, questTokensConvertion, questTokensCount):
    bonusData = deepcopy(bonusData or event.getRawBonuses())
    tokens = bonusData.get('tokens', {})
    if not tokens:
        return bonusData
    tokensForConvertion = set(tokens).intersection(questTokensConvertion.keys())
    for token in tokensForConvertion:
        usedConverters = []
        tokenConvertionData = questTokensConvertion[token]
        for index, convertionData in enumerate(tokenConvertionData):
            wasUsed = convertTokens(token, tokens, convertionData)
            if wasUsed:
                usedConverters.append(index)
            break

        questTokensConvertion[token] = [ convertionData for index, convertionData in enumerate(tokenConvertionData) if index not in usedConverters ]
        if not questTokensConvertion[token]:
            questTokensConvertion.pop(token)

    for token in set(tokens).difference(questTokensCount.keys()):
        tokens.pop(token)

    return bonusData


def getBonusDataFromOneOfBonuses(event, pCur=None):
    bonusData = event.getRawBonuses()
    trackResult = {}
    if pCur:
        pCurInnerDict = pCur.itervalues().next()
        bonusTracks = pCurInnerDict.get('bonusTracks', [])
        if bonusTracks:
            trackReplay = TrackVisitor(bonusTracks[-1], 1, None)
            trackReplay.walkBonuses(bonusData, trackResult)
    return trackResult


class TokenConvertionData(NamedTuple('TokenConvertionData', [('tokenTo', str), ('limit', int), ('rate', float)])):

    def __new__(cls, **kwargs):
        defaults = dict(tokenTo='', limit=0, rate=1.0)
        defaults.update({k:kwargs[k] for k in defaults.viewkeys() & kwargs.viewkeys()})
        return super(TokenConvertionData, cls).__new__(cls, **defaults)
