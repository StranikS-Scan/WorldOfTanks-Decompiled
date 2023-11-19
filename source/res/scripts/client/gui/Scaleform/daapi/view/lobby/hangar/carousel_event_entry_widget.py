# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousel_event_entry_widget.py
import itertools
import typing
from gui.Scaleform.daapi.view.meta.CarouselEventEntryMeta import CarouselEventEntryMeta
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared.system_factory import collectCarouselEventEntryPoints
if typing.TYPE_CHECKING:
    from typing import Dict, Type
    from skeletons.gui.hangar import ICarouselEventEntry
_VIEWS = {}

class CarouselEventEntryHolder(CarouselEventEntryMeta, IPrbListener):

    def __init__(self):
        super(CarouselEventEntryHolder, self).__init__()
        self.__activeViewID = R.invalid()

    def updateState(self):
        activeViewID = _getActiveCarouselEventEntryID()
        if self.__activeViewID != activeViewID:
            self.__activeViewID = activeViewID
            self._destroyInjected()
            if activeViewID != R.invalid():
                self._createInjectView(self.__activeViewID)

    def _onPopulate(self):
        self.updateState()

    def _makeInjectView(self, viewID=None):
        view = _VIEWS.get(viewID) or collectCarouselEventEntryPoints().get(viewID)
        return view()


def isAnyEntryVisible():
    return _getActiveCarouselEventEntryID() != R.invalid()


def _getActiveCarouselEventEntryID():
    entries = collectCarouselEventEntryPoints()
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is not None:
        state = dispatcher.getFunctionalState()
        for viewID, view in itertools.chain(_VIEWS.iteritems(), entries.iteritems()):
            if view.getIsActive(state):
                return viewID

    return R.invalid()
