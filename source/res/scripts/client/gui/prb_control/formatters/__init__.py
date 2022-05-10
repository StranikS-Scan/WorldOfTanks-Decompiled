# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/__init__.py
import time
from datetime import datetime
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prb_getters
from helpers import html, i18n
from helpers.time_utils import makeLocalServerTime
DETACHMENT_IS_NOT_SET = -1

def makePrebattleWaitingID(requestName):
    return '{0:>s}/{1:>s}'.format(prb_getters.getPrebattleTypeName().lower(), requestName)


def getPrebattleLocalizedString(string, led=None, escapeHtml=False):
    result = ''
    if led:
        result = i18n.encodeUtf8(led.get(string, ''))
        if escapeHtml:
            html.escape(result)
    return result


def getPrebattleEventName(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString('event_name', led, escapeHtml) if led else ''


def getPrebattleSessionName(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString('session_name', led, escapeHtml) if led else ''


def getPrebattleDescription(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString('desc', led, escapeHtml) if led else ''


def getPrebattleFullDescription(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    description = ''
    if led:
        eventName = getPrebattleLocalizedString('event_name', led, escapeHtml)
        sessionName = getPrebattleLocalizedString('session_name', led, escapeHtml)
        description = '{0:>s}: {1:>s}'.format(eventName, sessionName)
    return description


def getPrebattleOpponents(extraData, escapeHtml=False):
    first = ''
    second = ''
    if 'opponents' in extraData:
        opponents = extraData['opponents']
        first = i18n.encodeUtf8(opponents.get('1', {}).get('name', ''))
        second = i18n.encodeUtf8(opponents.get('2', {}).get('name', ''))
        if escapeHtml:
            first = html.escape(first)
            second = html.escape(second)
    return (first, second)


def getPrebattleOpponentsString(extraData, escapeHtml=False):
    first, second = getPrebattleOpponents(extraData, escapeHtml=escapeHtml)
    result = ''
    if first and second:
        result = i18n.makeString('#menu:opponents', firstOpponent=first, secondOpponent=second)
    elif 'type' in extraData:
        result = extraData['type']
    return result


def getPrebattleStartTimeString(startTime):
    startTimeString = backport.getLongTimeFormat(startTime)
    if startTime - time.time() > 86400:
        startTimeString = '{0:>s} {1:>s}'.format(backport.getLongDateFormat(startTime), startTimeString)
    return startTimeString


def getBattleSessionStartTimeString(startTime):
    startTimeString = getPrebattleStartTimeString(startTime)
    return '{} {}'.format(backport.text(R.strings.prebattle.title.battleSession.startTime()), startTimeString)


def getStartTimeLeft(startTime):
    if startTime:
        startTime = makeLocalServerTime(startTime)
        if datetime.utcfromtimestamp(startTime) > datetime.utcnow():
            return (datetime.utcfromtimestamp(startTime) - datetime.utcnow()).seconds


def getBattleSessionDetachment(extraData, clanDBID):
    detachment = DETACHMENT_IS_NOT_SET
    vehicleLvl = extraData.get('front_level', 0)
    teamIndex = 0
    for opponentIndex, opponentData in extraData.get('opponents', {}).items():
        if opponentData.get('id') == clanDBID:
            prebattleDetachmentId = opponentData.get('detachment')
            detachment = prebattleDetachmentId if prebattleDetachmentId is not None else DETACHMENT_IS_NOT_SET
            teamIndex = int(opponentIndex)

    return (detachment, vehicleLvl, teamIndex)
