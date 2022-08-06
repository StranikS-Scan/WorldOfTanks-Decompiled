# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/__init__.py
from __future__ import unicode_literals
import time
from datetime import datetime
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prb_getters
from helpers import html, i18n
from helpers.time_utils import makeLocalServerTime
DETACHMENT_IS_NOT_SET = -1

def makePrebattleWaitingID(requestName):
    return u'{0:>s}/{1:>s}'.format(prb_getters.getPrebattleTypeName().lower(), requestName)


def getPrebattleLocalizedString(string, led=None, escapeHtml=False):
    result = u''
    if led:
        result = led.get(string, u'')
        if escapeHtml:
            html.escape(result)
    return result


def getPrebattleEventName(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString(u'event_name', led, escapeHtml) if led else u''


def getPrebattleSessionName(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString(u'session_name', led, escapeHtml) if led else u''


def getPrebattleDescription(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    return getPrebattleLocalizedString(u'desc', led, escapeHtml) if led else u''


def getPrebattleFullDescription(extraData=None, escapeHtml=False):
    led = prb_getters.getPrebattleLocalizedData(extraData)
    description = u''
    if led:
        eventName = getPrebattleLocalizedString(u'event_name', led, escapeHtml)
        sessionName = getPrebattleLocalizedString(u'session_name', led, escapeHtml)
        description = u'{0:>s}: {1:>s}'.format(eventName, sessionName)
    return description


def getPrebattleOpponents(extraData, escapeHtml=False):
    first = u''
    second = u''
    if u'opponents' in extraData:
        opponents = extraData[u'opponents']
        first = opponents.get(u'1', {}).get(u'name', u'')
        second = opponents.get(u'2', {}).get(u'name', u'')
        if escapeHtml:
            first = html.escape(first)
            second = html.escape(second)
    return (first, second)


def getPrebattleOpponentsString(extraData, escapeHtml=False):
    first, second = getPrebattleOpponents(extraData, escapeHtml=escapeHtml)
    result = u''
    if first and second:
        result = i18n.makeString(u'#menu:opponents', firstOpponent=first, secondOpponent=second)
    elif u'type' in extraData:
        result = extraData[u'type']
    return result


def getPrebattleStartTimeString(startTime):
    startTimeString = backport.getLongTimeFormat(startTime)
    if startTime - time.time() > 86400:
        startTimeString = u'{0:>s} {1:>s}'.format(backport.getLongDateFormat(startTime), startTimeString)
    return startTimeString


def getBattleSessionStartTimeString(startTime):
    startTimeString = getPrebattleStartTimeString(startTime)
    return u'{} {}'.format(backport.text(R.strings.prebattle.title.battleSession.startTime()), startTimeString)


def getStartTimeLeft(startTime):
    if startTime:
        startTime = makeLocalServerTime(startTime)
        if datetime.utcfromtimestamp(startTime) > datetime.utcnow():
            return (datetime.utcfromtimestamp(startTime) - datetime.utcnow()).seconds


def getBattleSessionDetachment(extraData, clanDBID):
    detachment = DETACHMENT_IS_NOT_SET
    vehicleLvl = extraData.get(u'front_level', 0)
    teamIndex = 0
    for opponentIndex, opponentData in extraData.get(u'opponents', {}).items():
        if opponentData.get(u'id') == clanDBID:
            prebattleDetachmentId = opponentData.get(u'detachment')
            detachment = prebattleDetachmentId if prebattleDetachmentId is not None else DETACHMENT_IS_NOT_SET
            teamIndex = int(opponentIndex)

    return (detachment, vehicleLvl, teamIndex)
