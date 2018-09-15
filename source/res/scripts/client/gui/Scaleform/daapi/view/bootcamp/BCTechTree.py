# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechTree.py
from gui.Scaleform.daapi.view.lobby.techtree.TechTree import TechTree
from gui.shared import event_dispatcher as shared_events
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from nations import NAMES as NATION_NAMES
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE

class BCTechTree(TechTree):
    itemsCache = dependency.descriptor(IItemsCache)

    def goToNextVehicle(self, vehCD):
        if not g_bootcamp.isResearchFreeLesson():
            nationData = g_bootcampGarage.getNationData()
            if nationData['vehicle_second'] == vehCD:
                vehicle = self.itemsCache.items.getItemByCD(int(vehCD))
                if vehicle.isInInventory:
                    shared_events.showResearchView(vehCD)
                    return
            if nationData['vehicle_first'] == vehCD:
                shared_events.showResearchView(vehCD)
        else:
            shared_events.showResearchView(vehCD)

    def getNationTreeData(self, nationName):
        data = super(BCTechTree, self).getNationTreeData(NATION_NAMES[g_bootcamp.nation])
        dataNodes = data.get('nodes', None)
        if dataNodes is not None:
            for node in dataNodes:
                if 'vehCompareTreeNodeData' in node:
                    node['vehCompareTreeNodeData']['modeAvailable'] = False
                nodeState = node['state']
                if not NODE_STATE.inInventory(nodeState) and not NODE_STATE.isPremium(nodeState):
                    node['state'] = NODE_STATE_FLAGS.LOCKED

        data['nodes'][0]['displayInfo']['position'] = [16, 90]
        data['nodes'][0]['displayInfo']['lines'][0]['outPin'] = [144, 108]
        return data

    def setupContextHints(self, hintID):
        pass

    def _populateAfter(self):
        self.as_hideNationsBarS(True)
