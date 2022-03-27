# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/triggers_blocks.py
import typing
import BigWorld
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    import helpers
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar

class TriggerMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class TriggerExternal(Block, TriggerMeta):

    def __init__(self, *args, **kwargs):
        super(TriggerExternal, self).__init__(*args, **kwargs)
        self._subscribeSlot = self._makeEventInputSlot('subscribe', self._onSubscribe)
        self._unsubscribeSlot = self._makeEventInputSlot('unsubscribe', self._onUnsubscribe)
        self._eventIDSlot = self._makeDataInputSlot('eventID', SLOT_TYPE.STR)
        self._isActiveInputSlot = self._makeDataInputSlot('isActive', SLOT_TYPE.BOOL)
        self._outSlot = self._makeEventOutputSlot('out')
        self._active = False

    def validate(self):
        return 'EventID value is required' if not self._eventIDSlot.hasValue() else super(TriggerExternal, self).validate()

    def onStartScript(self):
        isActive = self._isActiveInputSlot.getValue() if self._isActiveInputSlot.hasValue() else True
        if isActive:
            self.setActive(True)

    def onFinishScript(self):
        if self.isActive():
            self.setActive(False)

    def isActive(self):
        return self._active

    def setActive(self, value):
        if self.isActive() == value:
            return
        self._active = value
        if not IS_VS_EDITOR:
            if self._active:
                BigWorld.player().onTrigger += self._onTrigger
            else:
                BigWorld.player().onTrigger -= self._onTrigger

    def _onTrigger(self, eventId, *args, **kwargs):
        if self._eventIDSlot.getValue() == eventId:
            self._outSlot.call()

    def _onSubscribe(self):
        self.setActive(True)

    def _onUnsubscribe(self):
        self.setActive(False)


class TriggerFireEvent(Block, TriggerMeta):

    def __init__(self, *args, **kwargs):
        super(TriggerFireEvent, self).__init__(*args, **kwargs)
        self._inputSlot = self._makeEventInputSlot('in', self._execute)
        self._eventIDSlot = self._makeDataInputSlot('eventID', SLOT_TYPE.STR)
        self._sendToServerSlot = self._makeDataInputSlot('sendToServer', SLOT_TYPE.BOOL)
        self._outSlot = self._makeEventOutputSlot('out')

    @classmethod
    def blockIcon(cls):
        pass

    @property
    def _avatar(self):
        if helpers.isPlayerAvatar():
            return BigWorld.player()
        errorVScript(self, 'BigWorld.player is not player avatar.')

    def _execute(self):
        if not IS_VS_EDITOR:
            eventID = self._eventIDSlot.getValue()
            sendToServer = self._sendToServerSlot.getValue()
            BigWorld.player().fireClientTrigger(eventID, sendToServer)
        self._outSlot.call()
