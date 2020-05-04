# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/event.py
import BigWorld
from constants import IS_EDITOR
from visual_script.block import Block, SLOT_TYPE, Meta, ASPECT
from visual_script_client.dependency import dependencyImporter
Avatar = dependencyImporter('Avatar')
if not IS_EDITOR:
    import TriggersManager
else:

    class TriggersManager(object):

        class ITriggerListener(object):
            pass


class SE20(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ServerEvent(Block, SE20):

    def __init__(self, *args, **kwargs):
        super(ServerEvent, self).__init__(*args, **kwargs)
        if not IS_EDITOR:
            player = BigWorld.player()
            if isinstance(player, Avatar.PlayerAvatar):
                BigWorld.player().onTrigger += self.__onTrigger
            else:
                self._writeLog('BigWorld.player() is not Avatar')
        self._eventID = self._makeDataInputSlot('eventID', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def __onTrigger(self, eventID, _):
        if self._eventID.getValue() == eventID:
            self._out.call()

    def onFinishScript(self):
        if not IS_EDITOR:
            player = BigWorld.player()
            if isinstance(player, Avatar.PlayerAvatar):
                BigWorld.player().onTrigger -= self.__onTrigger
            else:
                self._writeLog('BigWorld.player() is not Avatar')


class AreaTrigger(Block, SE20, TriggersManager.ITriggerListener):

    def __init__(self, *args, **kwargs):
        super(AreaTrigger, self).__init__(*args, **kwargs)
        self._areaID = self._makeDataInputSlot('area', SLOT_TYPE.STR)
        self._activated = self._makeEventOutputSlot('activated')
        self._deactivated = self._makeEventOutputSlot('deactivated')
        if not IS_EDITOR:
            TriggersManager.g_manager.addListener(self)

    def onFinishScript(self):
        if not IS_EDITOR:
            TriggersManager.g_manager.delListener(self)

    def onTriggerActivated(self, args):
        if self.__isCorrectArea(args):
            self._activated.call()

    def onTriggerDeactivated(self, args):
        if self.__isCorrectArea(args):
            self._deactivated.call()

    def __isCorrectArea(self, args):
        return args.get('type') == TriggersManager.TRIGGER_TYPE.AREA and args.get('name') == self._areaID.getValue()
