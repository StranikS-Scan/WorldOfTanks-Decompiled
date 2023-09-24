# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/marathon/marathon_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.MarathonEntryPointMeta import MarathonEntryPointMeta
from gui.impl.lobby.marathon.marathon_entry_point import MarathonEntryPoint

class MarathonEntryPointWrapper(MarathonEntryPointMeta):

    def _makeInjectView(self):
        self.__view = MarathonEntryPoint(flags=ViewFlags.VIEW)
        return self.__view
