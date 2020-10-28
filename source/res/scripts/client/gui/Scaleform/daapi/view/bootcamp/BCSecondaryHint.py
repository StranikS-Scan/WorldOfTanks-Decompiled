# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCSecondaryHint.py
from gui.Scaleform.daapi.view.meta.BCSecondaryHintMeta import BCSecondaryHintMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import BootcampEvent

class BCSecondaryHint(BCSecondaryHintMeta):

    def _populate(self):
        super(BCSecondaryHint, self)._populate()
        self.addListener(BootcampEvent.SHOW_SECONDARY_HINT, self.__onSecondaryHintShow, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(BootcampEvent.HIDE_SECONDARY_HINT, self.__onSecondaryHintHide, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(BootcampEvent.SHOW_SECONDARY_HINT, self.__onSecondaryHintShow, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(BootcampEvent.HIDE_SECONDARY_HINT, self.__onSecondaryHintHide, EVENT_BUS_SCOPE.BATTLE)
        super(BCSecondaryHint, self)._dispose()

    def __onSecondaryHintShow(self, event):
        self.as_showHintS(event.eventArg)

    def __onSecondaryHintHide(self, _):
        self.as_hideHintS()
