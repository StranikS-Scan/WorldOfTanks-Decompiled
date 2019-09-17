# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_advent_calendar_marker_view.py
import BigWorld
import GUI
import Math
from ClientSelectableAdventCalendarHangarObject import ClientSelectableAdventCalendarHangarObject
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.time_utils import getTillTimeString, getServerUTCTime
from skeletons.gui.game_control import ICalendarController
from skeletons.gui.shared.utils import IHangarSpace
_Y_TRANSLATION_OFFSET = 3.4

class LobbyAdventCalendarMarkerView(LobbyVehicleMarkerViewMeta):
    __calendarController = dependency.descriptor(ICalendarController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbyAdventCalendarMarkerView, self).__init__(ctx)
        self.__id = LobbyAdventCalendarMarkerView.__name__
        self.__actionInfo = None
        self.__matrix = None
        self.__marker = None
        self.__timer = None
        self.__isEnabled = False
        return

    def _populate(self):
        super(LobbyAdventCalendarMarkerView, self)._populate()
        self.__hangarSpace.onSpaceDestroy += self.__onDestroy
        self.addListener(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_LEAVE, self.__onDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.AdventCalendarEvent.DEFERRED_ITEMS_ACTION_STATE_CHANGED, self.__onChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_ENTER, self.__onChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.__onChanged()

    def _dispose(self):
        self.__onDestroy()
        self.removeListener(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_ENTER, self.__onChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.AdventCalendarEvent.DEFERRED_ITEMS_ACTION_STATE_CHANGED, self.__onChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.AdventCalendarEvent.ADVENT_CALENDAR_OBJECT_LEAVE, self.__onDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpace.onSpaceDestroy -= self.__onDestroy
        super(LobbyAdventCalendarMarkerView, self)._dispose()

    def __onMarkerDisable(self, event):
        self.__isEnabled = not event.ctx['isDisable']
        self.__updateMarkerVisibility()

    def __onChanged(self, *_):
        self.__matrix = self.__getEntityMarkerMatrix()
        self.__startUpdate()

    def __onDestroy(self, *_):
        if self.__timer is not None:
            BigWorld.cancelCallback(self.__timer)
            self.__timer = None
        if self.__marker is not None:
            self.as_removeEventMarkerS(self.__id)
            self.__marker = None
        return

    def __startUpdate(self):
        self.__onDestroy()
        if self.__matrix is not None:
            self.__actionInfo = self.__calendarController.getDeferredItemsActionInfo()
            flashMarker = self.as_createEventMarkerS(self.__id, self.__getCounterText(), self.__getTimerText())
            self.__marker = GUI.WGHangarVehicleMarker()
            self.__marker.setMarker(flashMarker, self.__matrix)
            self.__update()
        return

    def __update(self):
        if self.__isVisible():
            self.as_updateEventMarkerTextS(self.__id, self.__getTimerText())
            self.__timer = BigWorld.callback(1, self.__update)
        else:
            self.__onDestroy()

    def __isVisible(self):
        return self.__actionInfo is not None and self.__actionInfo.isEnabled and self.__actionInfo.itemsCount > 0 and self.__getTimeLeft() > 0

    def __updateMarkerVisibility(self):
        if self.__marker is not None:
            self.__marker.markerSetActive(self.__isEnabled)
        return

    def __getCounterText(self):
        return str(self.__actionInfo.itemsCount)

    def __getTimerText(self):
        return getTillTimeString(self.__getTimeLeft(), MENU.ADVENTCALENDAR_TIMELEFT)

    def __getTimeLeft(self):
        timeLeft = self.__actionInfo.endTimestamp - getServerUTCTime()
        return timeLeft if timeLeft > 0 else 0

    @classmethod
    def __getEntityMarkerMatrix(cls):
        for entity in BigWorld.entities.values():
            if entity and isinstance(entity, ClientSelectableAdventCalendarHangarObject):
                return cls.__getMarkerMatrix(entity)

        return None

    @staticmethod
    def __getMarkerMatrix(obj):
        matrix = Math.Matrix(obj.matrix)
        translation = matrix.translation
        translation.y += _Y_TRANSLATION_OFFSET
        matrix.translation = translation
        return matrix
