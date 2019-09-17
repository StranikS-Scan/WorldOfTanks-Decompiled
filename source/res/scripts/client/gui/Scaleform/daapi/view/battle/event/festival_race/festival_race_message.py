# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/festival_race_message.py
from collections import deque
from typing import TYPE_CHECKING
import BigWorld
from gui.Scaleform.daapi.view.meta.FestivalRaceMessagesViewMeta import FestivalRaceMessagesViewMeta
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
if TYPE_CHECKING:
    from client.Vehicle import Vehicle
MESSAGE_DURATION = 2.0
MESSAGE_DELAY = 0.5

class MessageType(object):
    FORSAGE = 'forsage'
    REPAIR = 'repair'
    NO_REPAIR = 'norepair'
    TRACK_RETURN = 'trackReturn'


class FestivalRaceMessageView(FestivalRaceMessagesViewMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FestivalRaceMessageView, self).__init__()
        self.__messageList = deque()
        self.__hideMessageCallbackID = None
        self.__showNextMessageCallbackID = None
        self.__lastConsumableItem = None
        self.__callbackId = None
        self.__callbackEventReturnId = None
        self.__isReturnedOnMap = True
        return

    def _populate(self):
        super(FestivalRaceMessageView, self)._populate()
        self.__addListeners()

    def __addListeners(self):
        ctrl = self.sessionProvider.dynamic.eventRepair
        if ctrl is not None:
            ctrl.onPlayerRepaired += self.__onRepair
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        mCtrl = self.sessionProvider.dynamic.eventGameMessages
        if mCtrl is not None:
            mCtrl.invalidZoneEntered += self.__onInvalidZoneEntered
            mCtrl.invalidZoneExit += self.__onInvalidZoneExit
        return

    def __onInvalidZoneExit(self, sender):
        if not sender.isPlayerVehicle:
            return
        self.__isReturnedOnMap = True

    def __onInvalidZoneEntered(self, sender):
        if not sender.isPlayerVehicle:
            return
        else:
            self.__isReturnedOnMap = False
            if self.__callbackEventReturnId is None:
                self.__callbackEventReturnId = BigWorld.callback(0.01, self.__showZoneEnteredMessage)
            return

    def __showZoneEnteredMessage(self):
        if not self.__isReturnedOnMap:
            messageText = backport.text(R.strings.festival.festival.msg.return_to_track())
            message = (MessageType.TRACK_RETURN, messageText, '')
            self.__tryToShowMessage(message)
            self.__callbackEventReturnId = None
        return

    def __onEquipmentUpdated(self, intCD, item):
        self.__lastConsumableItem = item
        if self.__callbackId is None:
            self.__callbackId = BigWorld.callback(0.01, self.__showSpeedBoostMessage)
        return

    def __showSpeedBoostMessage(self):
        self.__callbackId = None
        if self.__lastConsumableItem.isReady:
            messageText = backport.text(R.strings.festival.festival.msg.forsage_refilled())
            message = (MessageType.FORSAGE, messageText, '')
            self.__tryToShowMessage(message)
        return

    def __onRepair(self, amount, repaired):
        if repaired:
            messageType = MessageType.REPAIR
            messageText = backport.text(R.strings.festival.festival.msg.repaired())
            amountText = '+' + str(amount) + '%'
        else:
            messageType = MessageType.NO_REPAIR
            messageText = backport.text(R.strings.festival.festival.msg.not_repaired())
            amountText = ''
        message = (messageType, messageText, amountText)
        self.__tryToShowMessage(message)

    def __tryToShowMessage(self, data):
        self.__messageList.append(data)
        if len(self.__messageList) == 1:
            self.__showNextMessage(fromQueue=False)

    def __showNextMessage(self, fromQueue=True):
        if fromQueue:
            self.__showNextMessageCallbackID = None
            self.__messageList.popleft()
        if not self.__messageList:
            return
        else:
            message = self.__messageList[0]
            self.as_showMessageS(*message)
            self.__hideMessageCallbackID = BigWorld.callback(MESSAGE_DURATION, self.__hideMessage)
            return

    def __hideMessage(self):
        self.__hideMessageCallbackID = None
        self.as_hideMessageS()
        self.__showNextMessageCallbackID = BigWorld.callback(MESSAGE_DELAY, self.__showNextMessage)
        return

    def __removeListeners(self):
        ctrl = self.sessionProvider.dynamic.eventRepair
        if ctrl is not None:
            ctrl.onPlayerRepaired -= self.__onRepair
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        mCtrl = self.sessionProvider.dynamic.eventGameMessages
        if mCtrl is not None:
            mCtrl.invalidZoneEntered -= self.__onInvalidZoneEntered
            mCtrl.invalidZoneExit -= self.__onInvalidZoneExit
        return

    def _dispose(self):
        self.__messageList.clear()
        self.__messageList = None
        self.__removeListeners()
        if self.__hideMessageCallbackID:
            BigWorld.cancelCallback(self.__hideMessageCallbackID)
        if self.__showNextMessageCallbackID:
            BigWorld.cancelCallback(self.__showNextMessageCallbackID)
        super(FestivalRaceMessageView, self)._dispose()
        return
