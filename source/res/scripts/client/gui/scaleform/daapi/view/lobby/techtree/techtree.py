# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/TechTree.py
import Keys
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree.ResearchView import ResearchView
from gui.Scaleform.daapi.view.meta.TechTreeMeta import TechTreeMeta
from gui.Scaleform.daapi.view.lobby.techtree import dumpers, SelectedNation, USE_XML_DUMPING
from gui.Scaleform.daapi.view.lobby.techtree.data import NationTreeData
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared import events, EVENT_BUS_SCOPE
import nations

class TechTree(ResearchView, TechTreeMeta):

    def __init__(self, ctx = None):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            dumper = dumpers.NationXMLDumper()
        else:
            dumper = dumpers.NationObjDumper()
        super(TechTree, self).__init__(NationTreeData(dumper))
        self._resolveLoadCtx(ctx=ctx)

    def __del__(self):
        LOG_DEBUG('TechTree deleted')

    def redraw(self):
        self.as_refreshNationTreeDataS(SelectedNation.getName())

    def requestNationTreeData(self):
        if USE_XML_DUMPING and IS_DEVELOPMENT:
            self.as_useXMLDumpingS()
        self.as_setAvailableNationsS(g_techTreeDP.getAvailableNations())
        self.as_setSelectedNationS(SelectedNation.getName())
        return True

    def getNationTreeData(self, nationName):
        if nationName not in nations.INDICES:
            LOG_ERROR('Nation not found', nationName)
            return {}
        nationIdx = nations.INDICES[nationName]
        SelectedNation.select(nationIdx)
        self._data.load(nationIdx)
        return self._data.dump()

    def request4Unlock(self, unlockCD, vehCD, unlockIdx, xpCost):
        self.unlockItem(int(unlockCD), int(vehCD), int(unlockIdx), int(xpCost))

    def request4Buy(self, itemCD):
        self.buyVehicle(int(itemCD))

    def request4Sell(self, itemCD):
        self.sellVehicle(int(itemCD))

    def request4SelectInHangar(self, itemCD):
        self.selectVehicleInHangar(itemCD)
        self.onCloseTechTree()

    def request4ShowVehicleStatistics(self, itemCD):
        self.showVehicleStatistics(itemCD)

    def requestVehicleInfo(self, pickleDump):
        self.showVehicleInfo(pickleDump)

    def goToNextVehicle(self, vehCD):
        Event = events.LoadEvent
        exitEvent = Event(Event.LOAD_TECHTREE, ctx={'nation': SelectedNation.getName()})
        loadEvent = Event(Event.LOAD_RESEARCH, ctx={'rootCD': vehCD,
         'exit': exitEvent})
        self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def onCloseTechTree(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.as_refreshNationTreeDataS(SelectedNation.getName())

    def invalidateVTypeXP(self, xps):
        super(TechTree, self).invalidateVTypeXP(xps)
        result = self._data.invalidateXpCosts()
        if len(result):
            self.as_setUnlockPropsS(result)

    def invalidateWalletStatus(self, status):
        self.invalidateFreeXP()
        self.invalidateGold()

    def _resolveLoadCtx(self, ctx = None):
        nation = ctx['nation'] if ctx is not None and 'nation' in ctx else None
        if nation is not None and nation in nations.INDICES:
            nationIdx = nations.INDICES[nation]
            SelectedNation.select(nationIdx)
        else:
            SelectedNation.byDefault()
        return

    def _populate(self):
        super(TechTree, self)._populate()
        if IS_DEVELOPMENT:
            from gui import InputHandler
            InputHandler.g_instance.onKeyUp += self.__handleReloadData

    def _dispose(self):
        if IS_DEVELOPMENT:
            from gui import InputHandler
            InputHandler.g_instance.onKeyUp -= self.__handleReloadData
        super(TechTree, self)._dispose()

    def __handleReloadData(self, event):
        if event.key is Keys.KEY_R:
            g_techTreeDP.load(isReload=True)
            self.as_refreshNationTreeDataS(SelectedNation.getName())
