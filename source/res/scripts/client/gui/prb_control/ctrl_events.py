# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/ctrl_events.py
import Event

class _PrbCtrlEvents(object):
    """
    Class for gui specific events in prebattle/unit.
    """
    __slots__ = ('__eManager', 'onLegacyIntroModeJoined', 'onLegacyIntroModeLeft', 'onUnitIntroModeLeft', 'onLegacyInited', 'onUnitIntroModeJoined', 'onUnitBrowserModeLeft', 'onPreQueueJoined', 'onPreQueueLeft', 'onVehicleClientStateChanged')

    def __init__(self):
        """
        Events initialization
        """
        super(_PrbCtrlEvents, self).__init__()
        self.__eManager = Event.EventManager()
        self.onLegacyIntroModeJoined = Event.Event(self.__eManager)
        self.onLegacyIntroModeLeft = Event.Event(self.__eManager)
        self.onLegacyInited = Event.Event(self.__eManager)
        self.onUnitIntroModeJoined = Event.Event(self.__eManager)
        self.onUnitIntroModeLeft = Event.Event(self.__eManager)
        self.onUnitBrowserModeLeft = Event.Event(self.__eManager)
        self.onPreQueueJoined = Event.Event(self.__eManager)
        self.onPreQueueLeft = Event.Event(self.__eManager)
        self.onVehicleClientStateChanged = Event.Event(self.__eManager)

    def clear(self):
        """
        Events subscriptions clear
        """
        self.__eManager.clear()


g_prbCtrlEvents = _PrbCtrlEvents()
