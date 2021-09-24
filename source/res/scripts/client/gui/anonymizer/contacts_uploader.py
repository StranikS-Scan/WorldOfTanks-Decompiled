# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/anonymizer/contacts_uploader.py
import logging
import typing
import BigWorld
import AccountCommands
from constants import BattleUserActions, REQUEST_COOLDOWN
from messenger.proto.events import g_messengerEvents
from messenger.proto import proto_getter
from messenger.m_constants import PROTO_TYPE, CLIENT_ACTION_ID
_logger = logging.getLogger(__name__)

class ContactsUploader(object):
    __slots__ = ('__arenaUniqueID', '__callbackID', '__idToActions', '__idToNames')

    def __init__(self):
        self.__callbackID = None
        self.__arenaUniqueID = None
        self.__idToActions = {}
        self.__idToNames = {}
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @property
    def isProcessing(self):
        return self.__arenaUniqueID is not None

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def init(self):
        g_messengerEvents.shadow.onActionFailed += self._onShadowActionFailed
        g_messengerEvents.shadow.onActionDone += self._onShadowActionDone

    def fini(self):
        self.stop()
        g_messengerEvents.shadow.onActionFailed -= self._onShadowActionFailed
        g_messengerEvents.shadow.onActionDone -= self._onShadowActionDone

    def start(self, arenaUniqueID, contactsBlob):
        _logger.info('contacts uploader starts upload arenaID %s', arenaUniqueID)
        self.__arenaUniqueID = arenaUniqueID
        for (contactDBID, contactName), actions in contactsBlob.iteritems():
            actionsList = []
            if BattleUserActions.REMOVE_FRIEND & actions:
                actionsList.append(CLIENT_ACTION_ID.REMOVE_FRIEND)
            if BattleUserActions.REMOVE_IGNORED & actions:
                actionsList.append(CLIENT_ACTION_ID.REMOVE_IGNORED)
            if BattleUserActions.ADD_FRIEND & actions:
                actionsList.append(CLIENT_ACTION_ID.ADD_FRIEND)
            if BattleUserActions.ADD_IGNORED & actions:
                actionsList.append(CLIENT_ACTION_ID.ADD_IGNORED)
            if actionsList:
                self.__idToNames[contactDBID] = contactName
                self.__idToActions[contactDBID] = actionsList

        if self.__idToActions:
            self.__tryUploadContact()
        else:
            self._flushArenaRelations()

    def stop(self):
        _logger.info('Contacts Uploader: finish uploading previous arena. Stopped.')
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__arenaUniqueID = None
        self.__idToActions.clear()
        self.__idToNames.clear()
        return

    def _onShadowActionFailed(self, dbID, actionID, error):
        _logger.debug('Contacts Uploader: on shadow action failed dbID:%s, action:%s, error:%s', dbID, actionID, error)
        self._onShadowActionDone(dbID, actionID)

    def _onShadowActionDone(self, dbID, actionID):
        _logger.debug('Contacts Uploader: on shadow action done dbID:%s, action:%s', dbID, actionID)
        if dbID in self.__idToActions:
            actionsList = self.__idToActions[dbID]
            if actionsList[0] == actionID:
                actionsList.pop(0)
                if actionsList:
                    self.__tryUploadContact(dbID, actionsList)
                else:
                    del self.__idToActions[dbID]
                    del self.__idToNames[dbID]
                    BigWorld.callback(0.0, self.__tryUploadContact)
                return
        _logger.warning('Contacts Uploader: got feedback on action which is not setted up by me')

    def _flushArenaRelations(self):
        self.__callbackID = None
        _logger.debug('Contacts Uploader: try to flush arena relations for arenaID:%s', self.__arenaUniqueID)
        BigWorld.player().flushArenaRelations(self.__arenaUniqueID, self.__onFlushResponse)
        return

    def __onFlushResponse(self, _, resultID, __):
        if resultID != AccountCommands.RES_SUCCESS:
            _logger.debug('Contacts Uploader: server error, delaying flush for arenaID:%s', self.__arenaUniqueID)
            self.__callbackID = BigWorld.callback(REQUEST_COOLDOWN.FLUSH_RELATIONS, self._flushArenaRelations)

    def __tryUploadContact(self, dbID=None, leftActions=None):
        if not self.isProcessing:
            _logger.warning('Contacts Uploader: abort uploading because of stop processing')
            return
        elif not self.__idToActions:
            self._flushArenaRelations()
            return
        else:
            dbID = self.__idToActions.keys()[0] if dbID is None else dbID
            action = self.__idToActions[dbID][0] if leftActions is None else leftActions[0]
            name = self.__idToNames[dbID]
            _logger.debug('Contacts Uploader: starting uploading action dbID:%s, name:%s, action:%s', dbID, name, action)
            if CLIENT_ACTION_ID.REMOVE_FRIEND == action:
                self.proto.contacts.removeFriend(dbID, shadowMode=True)
            elif CLIENT_ACTION_ID.REMOVE_IGNORED == action:
                self.proto.contacts.removeIgnored(dbID, shadowMode=True)
            elif CLIENT_ACTION_ID.ADD_FRIEND == action:
                self.proto.contacts.addFriend(dbID, name, shadowMode=True)
            elif CLIENT_ACTION_ID.ADD_IGNORED == action:
                self.proto.contacts.addIgnored(dbID, name, shadowMode=True)
            return
