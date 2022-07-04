# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/hangar_spaces_switcher.py
from collections import namedtuple
import ResMgr
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpaceReloader
from skeletons.gui.shared.hangar_spaces_switcher import IHangarSpacesSwitcher

class _AttributesProxy(object):

    def __init__(self, attrs=None):
        super(_AttributesProxy, self).__init__()
        self.__attributes = set(attrs) if attrs else set()

    def __getattr__(self, attr):
        if attr not in self.__attributes:
            raise AttributeError
        return attr

    def add(self, attrs):
        self.__attributes.update(attrs)

    def clear(self):
        self.__attributes.clear()


_HangarSpaceSwitchParams = namedtuple('_HangarSpaceSwitchParams', ('spaceName', 'waitingMessage', 'waitingBackground'))

class HangarSpacesSwitcher(IHangarSpacesSwitcher):
    _hangarSpaceReloader = dependency.descriptor(IHangarSpaceReloader)

    def __init__(self):
        self.__hangarSpacesSwitchParams = {}
        self.__itemsToSwitch = None
        return

    def init(self):
        self.__readHangarSpacesSwitchSettings()
        self.__itemsToSwitch = _AttributesProxy(self.__hangarSpacesSwitchParams.keys())
        g_eventBus.addListener(events.HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, self.__switchToHangarSpaceEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def destroy(self):
        g_eventBus.removeListener(events.HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, self.__switchToHangarSpaceEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpacesSwitchParams.clear()
        self.__itemsToSwitch = None
        return

    @property
    def itemsToSwitch(self):
        return self.__itemsToSwitch

    @property
    def currentItem(self):
        currSpacePath = self._hangarSpaceReloader.hangarSpacePath
        if not currSpacePath:
            return None
        else:
            for itemKey, itemParams in self.__hangarSpacesSwitchParams.iteritems():
                if itemParams.spaceName in currSpacePath:
                    return itemKey

            return None

    def __readHangarSpacesSwitchSettings(self):
        hangarsXml = ResMgr.openSection('gui/hangars.xml')
        if hangarsXml and hangarsXml.has_key('hangar_space_switch_items'):
            switchItems = hangarsXml['hangar_space_switch_items']
            for item in switchItems.values():
                name = item.readString('name')
                spaceName = item.readString('space')
                waitingMessage = item.readString('waitingMessage') or None
                waitingBackground = item.readString('waitingBackground') or None
                self.__hangarSpacesSwitchParams[name] = _HangarSpaceSwitchParams(spaceName, waitingMessage, waitingBackground)

        return

    def __switchToHangarSpaceEvent(self, event):
        switchItemName = event.ctx.get('switchItemName')
        if switchItemName:
            self.__switchToHangarSpace(switchItemName)

    def __switchToHangarSpace(self, switchItemName):
        if switchItemName not in self.__hangarSpacesSwitchParams:
            return False
        spaceName, waitingMessage, backgroundImage = self.__hangarSpacesSwitchParams[switchItemName]
        return self._hangarSpaceReloader.changeHangarSpace(spaceName, waitingMessage, backgroundImage)
