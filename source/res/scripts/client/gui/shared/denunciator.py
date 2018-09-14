# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/denunciator.py
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.battle_control import g_sessionProvider
from gui.shared import g_itemsCache
from messenger import MessengerEntry, g_settings
_DENUNCIATIONS_MAP = {'offend': constants.DENUNCIATION.OFFEND,
 'notFairPlay': constants.DENUNCIATION.NOT_FAIR_PLAY,
 'forbiddenNick': constants.DENUNCIATION.FORBIDDEN_NICK,
 'bot': constants.DENUNCIATION.BOT,
 'flood': constants.DENUNCIATION.FLOOD,
 'swindle': constants.DENUNCIATION.SWINDLE,
 'blackmail': constants.DENUNCIATION.BLACKMAIL}

class DENUNCIATIONS(object):
    APPEAL = 'appeal'
    OFFEND = 'offend'
    NOT_FAIR_PLAY = 'notFairPlay'
    FORBIDDEN_NICK = 'forbiddenNick'
    BOT = 'bot'
    FLOOD = 'flood'
    SWINDLE = 'swindle'
    BLACKMAIL = 'blackmail'


class Denunciator(object):
    """Denunciation creation helper.
    """

    def makeAppeal(self, violatorID, userName, topic):
        topicID = _DENUNCIATIONS_MAP.get(topic)
        player = BigWorld.player()
        violatorKind = self._getViolatorKind(player, violatorID)
        try:
            player.makeDenunciation(violatorID, topicID, violatorKind)
        except (AttributeError, TypeError):
            LOG_ERROR('Cannot make a denunciation')
            return

        topicStr = i18n.makeString(MENU.denunciation(topicID))
        message = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_SUCCESS)
        message = message % {'name': userName,
         'topic': topicStr}
        self._makeNotification(message)

    def isAppealsEnabled(self):
        return self.getDenunciationsLeft() > 0

    def getDenunciationsLeft(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def _getViolatorKind(self, player, violatorID):
        raise NotImplementedError()

    def _makeNotification(self, message):
        raise NotImplementedError()


class LobbyDenunciator(Denunciator):

    def _getViolatorKind(self, player, violatorID):
        return constants.VIOLATOR_KIND.UNKNOWN

    def _makeNotification(self, message):
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Information)


class BattleDenunciator(Denunciator):

    def _getViolatorKind(self, player, violatorID):
        arenaDP = g_sessionProvider.getArenaDP()
        vehicleID = arenaDP.getVehIDByAccDBID(violatorID)
        violator = arenaDP.getVehicleInfo(vehicleID)
        if player.team == violator.team:
            return constants.VIOLATOR_KIND.ALLY
        else:
            return constants.VIOLATOR_KIND.ENEMY

    def _makeNotification(self, message):
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message}))
