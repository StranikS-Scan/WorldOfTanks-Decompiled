# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_mini_games_marker_view.py
import time
import GUI
import Math
from gui.Scaleform.locale.FESTIVAL import FESTIVAL
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import getTillTimeString
from skeletons.festival import IFestivalController
from skeletons.gui.shared.utils import IHangarSpace
_X_TRANSLATION_OFFSET = 4.3
_Y_TRANSLATION_OFFSET = 6
_Z_TRANSLATION_OFFSET = 5

class LobbyMiniGameMarkerView(LobbyVehicleMarkerViewMeta):
    __festController = dependency.descriptor(IFestivalController)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbyMiniGameMarkerView, self).__init__(ctx)
        self.__id = LobbyMiniGameMarkerView.__name__
        self.__isEnabled = True
        self.__marker = None
        return

    def _populate(self):
        super(LobbyMiniGameMarkerView, self)._populate()
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.addListener(events.MiniGamesEvent.MINI_GAMES_OBJECT_ENTER, self.__onObjectEnterWorld, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.MiniGamesEvent.MINI_GAMES_OBJECT_LEAVE, self.__onObjectLeaveWorld, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.__notifier = SimpleNotifier(self.__getCooldownPeriod, self.__updateNotifier)
        self.__festController.onMiniGamesUpdated += self.__update

    def _dispose(self):
        self.removeListener(events.MiniGamesEvent.MINI_GAMES_OBJECT_LEAVE, self.__onObjectLeaveWorld, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.MiniGamesEvent.MINI_GAMES_OBJECT_ENTER, self.__onObjectEnterWorld, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__festController.onMiniGamesUpdated -= self.__update
        self.__destroyMarker()
        self.__notifier.clear()
        super(LobbyMiniGameMarkerView, self)._dispose()

    def __onMarkerDisable(self, event):
        self.__isEnabled = not event.ctx['isDisable']
        self.__updateMarkerVisibility()

    def __onObjectEnterWorld(self, event):
        self.__update()
        self.__marker = GUI.WGHangarVehicleMarker()
        self.__marker.setMarker(self.as_createEventMarkerS(self.__id, '', ''), self.__getMarkerMatrix(event.ctx['entity']))
        self.as_updateEventMarkerTextS(self.__id, self.__getMarkerString())
        self.__updateMarkerVisibility()

    def __onObjectLeaveWorld(self, *_):
        self.__destroyMarker()

    def __onSpaceDestroy(self, *_):
        self.__destroyMarker()

    def __destroyMarker(self):
        self.__notifier.stopNotification()
        self.as_removeEventMarkerS(self.__id)
        self.__marker = None
        return

    def __getMarkerString(self):
        miniGamesCooldown = self.__festController.getMiniGamesCooldown()
        if miniGamesCooldown is not None:
            timeText = getTillTimeString(miniGamesCooldown if miniGamesCooldown > 0 else 0, FESTIVAL.GAMES_COOLDOWN_OLDSTYLE)
            self.as_setEventMarkerLockedS(self.__id, True)
            return timeText
        else:
            leftAttempts = self.__festController.getMiniGamesAttemptsLeft()
            maxAttempts = self.__festController.getMiniGamesAttemptsMax()
            self.as_setEventMarkerLockedS(self.__id, False)
            return backport.text(R.strings.festival.games.widget.active.body()).format(left=leftAttempts, total=maxAttempts) if maxAttempts else ''

    @staticmethod
    def __getMarkerMatrix(obj):
        matrix = Math.Matrix(obj.matrix)
        translation = matrix.translation
        translation.z += _Z_TRANSLATION_OFFSET
        translation.y += _Y_TRANSLATION_OFFSET
        translation.x += _X_TRANSLATION_OFFSET
        matrix.translation = translation
        return matrix

    def __getCooldownPeriod(self):
        leftTime = self.__festController.getMiniGamesCooldown()
        gmTime = time.gmtime(leftTime)
        return gmTime.tm_sec + 1

    def __updateNotifier(self):
        self.as_updateEventMarkerTextS(self.__id, self.__getMarkerString())

    def __updateMarkerVisibility(self):
        if self.__marker is not None:
            self.__marker.markerSetActive(self.__isEnabled and self.__festController.isMiniGamesEnabled())
        return

    def __update(self):
        self.__updateMarkerVisibility()
        miniGamesCooldown = self.__festController.getMiniGamesCooldown()
        if miniGamesCooldown is not None:
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()
        self.as_updateEventMarkerTextS(self.__id, self.__getMarkerString())
        return
