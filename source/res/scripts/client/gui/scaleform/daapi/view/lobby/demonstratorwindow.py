# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/DemonstratorWindow.py
import ArenaType
from gui.Scaleform.daapi.view.meta.DemonstratorWindowMeta import DemonstratorWindowMeta
from gui.prb_control.context import PrebattleAction
from gui.prb_control.dispatcher import g_prbLoader

class DemonstratorWindow(DemonstratorWindowMeta):

    def _populate(self):
        super(DemonstratorWindow, self)._populate()
        maps = dict(ctf=[], assault=[], domination=[], nations=[])
        for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
            if arenaType.explicitRequestOnly:
                continue
            if arenaType.gameplayName in maps:
                maps[arenaType.gameplayName].append({'id': arenaTypeID,
                 'name': arenaType.name,
                 'type': arenaType.gameplayName})

        sorting = lambda item: item['name']
        self.as_setDataS({'standard': sorted(maps['ctf'], key=sorting),
         'assault': sorted(maps['assault'], key=sorting),
         'encounter': sorted(maps['domination'], key=sorting),
         'nations': sorted(maps['nations'], key=sorting)})

    def onMapSelected(self, mapID):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doAction(PrebattleAction(None, mapID=mapID))
            self.onWindowClose()
        return

    def onWindowClose(self):
        self.destroy()
