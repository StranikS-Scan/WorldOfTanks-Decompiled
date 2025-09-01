# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/hotkey_updaters.py
import typing
from collections import namedtuple
import CommandMapping
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
HotKeyCommand = namedtuple('HotKeyCommand', ['command', 'key', 'satelliteKeys'])

class IHotKeysView(object):

    def setHotkeys(self, hotKeyCommands):
        raise NotImplementedError


class HotKeysUpdater(ViewUpdater):

    def initialize(self):
        super(HotKeysUpdater, self).initialize()
        CommandMapping.g_instance.onMappingChanged += self._onMappingChanged
        self._onMappingChanged()

    def finalize(self):
        CommandMapping.g_instance.onMappingChanged -= self._onMappingChanged
        super(HotKeysUpdater, self).finalize()

    def _onMappingChanged(self, *_):
        raise NotImplementedError


class HotKeysViewUpdater(HotKeysUpdater):
    _DEFAULT_KEYS = (None, ())

    def __init__(self, commands, view):
        super(HotKeysViewUpdater, self).__init__(view)
        self.__commands = commands

    def _onMappingChanged(self, *_):
        self.view.setHotkeys([ HotKeyCommand(command, *(CommandMapping.g_instance.getCommandKeys(command) or self._DEFAULT_KEYS)) for command in self.__commands ])
