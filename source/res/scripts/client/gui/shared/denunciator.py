# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/denunciator.py
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import dependency
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from messenger import MessengerEntry, g_settings
from messenger.storage import storage_getter
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared import IItemsCache

class DENUNCIATIONS(object):
    APPEAL = 'appeal'
    INCORRECT_BEHAVIOR = 'incorrectBehavior'
    NOT_FAIR_PLAY = 'notFairPlay'
    FORBIDDEN_NICK = 'forbiddenNick'
    BOT = 'bot'
    ORDER = (INCORRECT_BEHAVIOR,
     NOT_FAIR_PLAY,
     FORBIDDEN_NICK,
     BOT)
    ENEMY_ORDER = (NOT_FAIR_PLAY, FORBIDDEN_NICK, BOT)


DENUNCIATIONS_MAP = {DENUNCIATIONS.INCORRECT_BEHAVIOR: constants.DENUNCIATION.INCORRECT_BEHAVIOR,
 DENUNCIATIONS.NOT_FAIR_PLAY: constants.DENUNCIATION.NOT_FAIR_PLAY,
 DENUNCIATIONS.FORBIDDEN_NICK: constants.DENUNCIATION.FORBIDDEN_NICK,
 DENUNCIATIONS.BOT: constants.DENUNCIATION.BOT}

class Denunciator(object):

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def makeAppeal(self, violatorID, userName, topic, arenaUniqueID, ctx=None):
        topicID = DENUNCIATIONS_MAP.get(topic)
        player = BigWorld.player()
        violatorKind = self._getViolatorKind(player, violatorID, ctx)
        denunciationsLeft = self.getDenunciationsLeft()
        try:
            player.makeDenunciation(violatorID, topicID, violatorKind, arenaUniqueID)
            if self._shouldSaveInLocalStorage():
                self.playerCtx.addDenunciationFor(violatorID, topicID, arenaUniqueID)
        except (AttributeError, TypeError):
            LOG_ERROR('Cannot make a denunciation')
            return

        message = self._formSystemMessage(userName, topicID, denunciationsLeft)
        self._makeNotification(message)

    def isAppealsEnabled(self):
        return self.getDenunciationsLeft() > 0

    def isAppealsForTopicEnabled(self, violatorID, topicID, arenaUniqueID):
        return self.isAppealsEnabled() and not self.playerCtx.hasDenunciationFor(violatorID, topicID, arenaUniqueID)

    def getDenunciationsLeft(self):
        raise NotImplementedError()

    def getDenunciationsPerDay(self):
        return constants.BATTLE_DENUNCIATIONS_PER_DAY

    def _shouldSaveInLocalStorage(self):
        return True

    def _getViolatorKind(self, player, violatorID, ctx=None):
        raise NotImplementedError()

    def _formSystemMessage(self, userName, topicID, _):
        topicStr = i18n.makeString(MENU.denunciation(topicID))
        message = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_SUCCESS)
        message = message % {'name': userName,
         'topic': topicStr}
        return message

    def _makeNotification(self, message):
        raise NotImplementedError()


class LobbyDenunciator(Denunciator):
    itemsCache = dependency.descriptor(IItemsCache)

    def getDenunciationsLeft(self):
        return self.itemsCache.items.stats.battleDenunciationsLeft

    def _getViolatorKind(self, player, violatorID, ctx=None):
        if ctx is None:
            return constants.VIOLATOR_KIND.UNKNOWN
        else:
            return constants.VIOLATOR_KIND.ALLY if ctx.children.get('isAlly') else constants.VIOLATOR_KIND.ENEMY

    def _makeNotification(self, message):
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Information)


class BattleDenunciator(Denunciator):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getDenunciationsLeft(self):
        return getattr(BigWorld.player(), 'denunciationsLeft', 0)

    @classmethod
    def getArenaUniqueID(cls):
        return BigWorld.player().arenaUniqueID

    def _getViolatorKind(self, player, violatorID, ctx=None):
        arenaDP = self.sessionProvider.getArenaDP()
        vehicleID = arenaDP.getVehIDBySessionID(str(violatorID))
        violator = arenaDP.getVehicleInfo(vehicleID)
        return constants.VIOLATOR_KIND.ALLY if player.team == violator.team else constants.VIOLATOR_KIND.ENEMY

    def _makeNotification(self, message):
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message}))


class LobbyChatDenunciator(LobbyDenunciator):
    itemsCache = dependency.descriptor(IItemsCache)

    def getDenunciationsLeft(self):
        return self.itemsCache.items.stats.hangarDenunciationsLeft

    def getDenunciationsPerDay(self):
        return constants.HANGAR_DENUNCIATIONS_PER_DAY

    def isAppealsForTopicEnabled(self, violatorID, topicID, arenaUniqueID):
        if not self.isAppealsEnabled():
            return False
        hangarDenunciations = self.itemsCache.items.stats.hangarDenunciations
        violatorTopicIDs = hangarDenunciations.get(violatorID, set())
        return topicID not in violatorTopicIDs

    def _getViolatorKind(self, player, violatorID, ctx=None):
        return constants.VIOLATOR_KIND.HANGAR_CHAT_MEMBER

    def _shouldSaveInLocalStorage(self):
        return False

    def _formSystemMessage(self, userName, _, denunciationsLeft):
        message = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_HANGARCHATSUCCESS_BODY)
        message = message % {'name': userName,
         'countLeft': denunciationsLeft - 1,
         'countPerDay': self.getDenunciationsPerDay()}
        return message

    def _makeNotification(self, message):
        header = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_HANGARCHATSUCCESS_TITLE)
        SystemMessages.pushMessage(text=message, messageData={'header': header}, type=SystemMessages.SM_TYPE.InformationHeader)
