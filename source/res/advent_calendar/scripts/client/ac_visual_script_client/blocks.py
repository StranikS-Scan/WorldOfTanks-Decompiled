# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/ac_visual_script_client/blocks.py
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script import ASPECT
from visual_script.slot_types import SLOT_TYPE
event_dispatcher, dependency, game_controller = dependencyImporter('advent_calendar.gui.shared.event_dispatcher', 'helpers.dependency', 'advent_calendar.skeletons.game_controller')

class AdventCalendarMeta(Meta):

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
        return [ASPECT.HANGAR]


class OpenAdventCalendar(Block, AdventCalendarMeta):

    def __init__(self, *args, **kwargs):
        super(OpenAdventCalendar, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self, *_):
        event_dispatcher.showAdventCalendarMainWindow()
        self._out.call()


class OnAdventCalendarConfigChanged(Block, AdventCalendarMeta):
    __adventController = dependency.descriptor(game_controller.IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        super(OnAdventCalendarConfigChanged, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        self.__adventController.onConfigChanged += self.__onConfigChanged

    def onFinishScript(self):
        self.__adventController.onConfigChanged -= self.__onConfigChanged

    def __onConfigChanged(self):
        self._out.call()


class IsAdventCalendarAvailable(Block, AdventCalendarMeta):
    __adventController = dependency.descriptor(game_controller.IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        super(IsAdventCalendarAvailable, self).__init__(*args, **kwargs)
        self._isAvailable = self._makeDataOutputSlot('isAvailable', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._isAvailable.setValue(self.__adventController.isAvailable())
