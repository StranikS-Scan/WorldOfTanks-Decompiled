# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/base.py
from constants import BigWorld
from gui.Scaleform.daapi.view.battle.shared.indicator_items.indicators_storage import g_indicatorsStorage
from gui.shared import EVENT_BUS_SCOPE, events
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.CommonIndicatorMeta import CommonIndicatorMeta
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID, VEHICLE_VIEW_STATE
from helpers import dependency
from helpers.events_handler import EventsHandler

class BaseIndicator(CommonIndicatorMeta, EventsHandler):
    __slots__ = ('__isAllowedByContext', '__isEnabled')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BaseIndicator, self).__init__()
        self.__isAllowedByContext = False
        self.__isEnabled = False

    @property
    def attachedVehicle(self):
        avatar = BigWorld.player()
        return avatar.vehicle if avatar and avatar.vehicle else None

    def setState(self, state):
        raise NotImplementedError

    def isValidVehicle(self, vehicle):
        raise NotImplementedError

    @staticmethod
    def componentName():
        raise NotImplementedError

    def _populate(self):
        super(BaseIndicator, self)._populate()
        g_indicatorsStorage.add(self.componentName(), self)
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.__onVehicleControlling(self.attachedVehicle)
        self._subscribe()
        self.__updateVisibility()

    def _dispose(self):
        self._unsubscribe()
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        g_indicatorsStorage.pop(self.componentName())
        super(BaseIndicator, self)._dispose()

    def _getEvents(self):
        result = ()
        result += self.__getCrosshairEvents()
        result += self.__getComp7Events()
        result += self.__getVehicleStateEvents()
        return result

    def _setVisible(self, state):
        self.__isEnabled = state
        self.__updateVisibility()

    def __getCrosshairEvents(self):
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        return () if crosshairCtrl is None else ((crosshairCtrl.onCrosshairPositionChanged, self._updateScale), (crosshairCtrl.onCrosshairScaleChanged, self._updateScale), (crosshairCtrl.onCrosshairViewChanged, self.__onCrosshairViewChanged))

    def __getComp7Events(self):
        prbCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        return () if prbCtrl is None else ((prbCtrl.onBattleStarted, self.__onComp7BattleStarted),)

    def __getVehicleStateEvents(self):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        return () if vStateCtrl is None else ((vStateCtrl.onVehicleStateUpdated, self.__onVehicleStateUpdated), (vStateCtrl.onVehicleControlling, self.__onVehicleControlling))

    def __onComp7BattleStarted(self):
        self.__isAllowedByContext = self.__isComp7IndicatorAllowed()
        self.__updateVisibility()

    def __onVehicleControlling(self, vehicle):
        if vehicle is None:
            return
        else:
            self._setVisible(self.isValidVehicle(vehicle))
            return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__updateDestroyed(value)
            return
        if state == VEHICLE_VIEW_STATE.CREW_DEACTIVATED:
            self.__updateDestroyed(value)
            return

    def __updateDestroyed(self, _):
        self.as_setVisibleS(False)

    def _updateScale(self, *_):
        self.as_updateLayoutS(*self.__sessionProvider.shared.crosshair.getScaledPosition())
        self.__updateVisibility()

    def __onCrosshairViewChanged(self, viewID):
        if viewID == CROSSHAIR_VIEW_ID.UNDEFINED:
            self.as_setVisibleS(False)
        else:
            self.__updateVisibility()

    def __updateVisibility(self):
        self.as_setVisibleS(self.__isEnabled and self.__isAllowedByContext)

    def __handleBattleLoading(self, event):
        self.__isAllowedByContext = not event.ctx['isShown'] and self.__isComp7IndicatorAllowed()
        self.__updateVisibility()

    def __isComp7IndicatorAllowed(self):
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        return prebattleCtrl is None or prebattleCtrl.isVehicleStateIndicatorAllowed()
