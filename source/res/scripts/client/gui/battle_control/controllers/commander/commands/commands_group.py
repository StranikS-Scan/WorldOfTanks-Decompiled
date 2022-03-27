# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/commands_group.py
from typing import TYPE_CHECKING
from gui.battle_control.controllers.commander.interfaces import ICommandsGroup
if TYPE_CHECKING:
    from gui.battle_control.controllers.commander.interfaces import ICommand
    from typing import Dict, Optional, Set

class CommandsGroup(ICommandsGroup):
    __slots__ = ('_vehicleCommands', '_groupID')

    def __init__(self, groupID):
        self._vehicleCommands = set()
        self._groupID = groupID

    def add(self, command):
        self._vehicleCommands.add(command)

    def remove(self, command):
        self._vehicleCommands.remove(command)

    @property
    def id(self):
        return self._groupID

    @property
    def commands(self):
        return list(self._vehicleCommands)

    @property
    def isGroupComplete(self):
        for command in self._vehicleCommands:
            if not command.isCompleted:
                return False

        return True


class CommandsGroupContainer(object):
    _CURRENT_COMMANDS_GROUP_ID = 0

    def __init__(self):
        super(CommandsGroupContainer, self).__init__()
        self.__groupCommands = {}

    def handleOnCommandEnqueued(self, command):
        groupID = command.groupID
        if groupID:
            group = self.__groupCommands.get(groupID, None)
            if not group:
                self.__groupCommands[groupID] = group = CommandsGroup(groupID)
            group.add(command)
        return

    def handleOnCommandDequeued(self, command):
        groupID = command.groupID
        group = self.__groupCommands.get(groupID, None)
        if group is not None and group.isGroupComplete:
            del self.__groupCommands[groupID]
        return

    def getCommandsGroup(self, groupID):
        return self.__groupCommands.get(groupID, None)

    @classmethod
    def getNextCommandsGroupID(cls):
        cls._CURRENT_COMMANDS_GROUP_ID += 1
        return cls._CURRENT_COMMANDS_GROUP_ID

    def reset(self):
        self.__groupCommands.clear()
