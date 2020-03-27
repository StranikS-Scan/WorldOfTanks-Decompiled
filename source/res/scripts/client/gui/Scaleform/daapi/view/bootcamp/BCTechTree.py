# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechTree.py
from gui.Scaleform.daapi.view.lobby.techtree.techtree_page import TechTree
from gui.shared import event_dispatcher as shared_events, events
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from nations import NAMES as NATION_NAMES
from bootcamp.Bootcamp import g_bootcamp
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE

class BCTechTree(TechTree):

    def goToNextVehicle(self, vehCD):
        if not g_bootcamp.isResearchFreeLesson():
            nationData = g_bootcamp.getNationData()
            vehicle = self._itemsCache.items.getItemByCD(int(vehCD))
            exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': vehicle.nationName})
            if nationData['vehicle_second'] == vehCD:
                if vehicle.isInInventory:
                    shared_events.showResearchView(vehCD, exitEvent=exitEvent)
                    return
            if nationData['vehicle_first'] == vehCD:
                shared_events.showResearchView(vehCD, exitEvent=exitEvent)
        else:
            shared_events.showResearchView(vehCD)

    def getNationTreeData(self, nationName):
        data = super(BCTechTree, self).getNationTreeData(NATION_NAMES[g_bootcamp.nation])
        dataNodes = data.get('nodes', None)
        if dataNodes is not None:
            dataNodes = [ node for node in dataNodes if not NODE_STATE.isPremium(node['state']) ]
            for node in dataNodes:
                if 'vehCompareTreeNodeData' in node:
                    node['vehCompareTreeNodeData']['modeAvailable'] = False
                nodeState = node['state']
                if not NODE_STATE.inInventory(nodeState):
                    node['state'] = NODE_STATE_FLAGS.LOCKED
                    if NODE_STATE.isAnnouncement(nodeState):
                        node['state'] |= NODE_STATE_FLAGS.ANNOUNCEMENT
                        node['state'] |= NODE_STATE_FLAGS.NOT_CLICKABLE

            data['nodes'] = dataNodes
        return data

    def setupContextHints(self, hintID):
        pass

    def _populateAfter(self):
        self.as_hideNationsBarS(True)
        self.as_setBlueprintsSwitchButtonStateS(enabled=False, selected=False, tooltip='', visible=False)
        self.as_setVehicleCollectorStateS(enabled=False)
