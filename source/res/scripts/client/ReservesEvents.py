# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReservesEvents.py
import Event

class ReservesEvents(object):

    def __init__(self):
        self.onShowPanel = Event.Event()
        self.onSelectedReserve = Event.Event()
        self.onUpdate = Event.Event()
        self.onShownPanel = Event.Event()
        self.hidePanel = Event.Event()
        self.showPanel = Event.Event()
        self.onChangedReservesModifier = Event.Event()


randomReservesEvents = ReservesEvents()
