# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/DemonstratorWindow.py
import ArenaType
from gui.Scaleform.daapi.view.meta.DemonstratorWindowMeta import DemonstratorWindowMeta
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class DemonstratorWindow(DemonstratorWindowMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _populate(self):
        super(DemonstratorWindow, self)._populate()
        maps = dict(ctf=[], assault=[], domination=[], nations=[])
        serverSettings = self.lobbyContext.getServerSettings()
        availableRandomMaps = serverSettings.getRandomMapsForDemonstrator()
        for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
            if arenaType.explicitRequestOnly:
                continue
            if arenaType.gameplayName not in maps:
                continue
            gameplayID, geometryID = ArenaType.parseTypeID(arenaTypeID)
            geometry = (geometryID, gameplayID)
            if any((geometry in divisionMaps for divisionMaps in availableRandomMaps.itervalues())):
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
            dispatcher.doAction(PrbAction(None, mapID=mapID))
            self.onWindowClose()
        return

    def onWindowClose(self):
        self.destroy()
