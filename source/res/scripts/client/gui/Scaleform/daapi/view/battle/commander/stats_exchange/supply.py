# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/stats_exchange/supply.py
from RTSShared import RTSSupply
from gui.Scaleform.daapi.view.battle.commander.spawn_menu import convertTagToGuiSupplyType
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.broker import IExchangeComposer, IExchangeComponent
from gui.battle_control.controllers.commander.vos_collections import SupplySortKey, SupplyInfoCollection
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class SupplySortedIDsComposer(IExchangeComposer):

    def __init__(self, voField='itemIDs', isAlly=True):
        super(SupplySortedIDsComposer, self).__init__()
        self._items = []
        self._voField = voField
        self._isAlly = isAlly

    def clear(self):
        self._items = []

    def compose(self, data):
        if self._items:
            data[self._voField] = self._items
        return data

    def update(self, arenaDP):
        self._items = []
        for cd in SupplyInfoCollection(SupplySortKey, isAlly=self._isAlly).ids(arenaDP):
            if cd not in self._items:
                self._items.append(cd)


class SupplyComposer(IExchangeComposer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, voField='items'):
        super(SupplyComposer, self).__init__()
        self._items = {}
        self._voField = voField

    def clear(self):
        self._items = {}

    def compose(self, data):
        if self._items:
            data[self._voField] = self._items.values()
        return data

    def create(self, vInfo):
        supplyID = RTSSupply.getID(vInfo.vehicleType)
        if supplyID is None or supplyID in self._items:
            return
        else:
            self._items[supplyID] = {'supplyID': supplyID,
             'supplyType': convertTagToGuiSupplyType(vInfo.vehicleType.classTag),
             'supplyName': vInfo.vehicleType.name,
             'alive': 0,
             'all': 0,
             'frags': 0}
            return

    def updateCounters(self, vInfo, isAlive, frags):
        supplyID = RTSSupply.getID(vInfo.vehicleType)
        if supplyID in self._items:
            if isAlive:
                self._items[supplyID]['alive'] += 1
            self._items[supplyID]['all'] += 1
            self._items[supplyID]['frags'] += frags


class SupplyExchangeBlock(IExchangeComponent):

    def __init__(self):
        super(SupplyExchangeBlock, self).__init__()
        self._allySupplyComposer = SupplyComposer('leftSupplyInfos')
        self._enemySupplyComposer = SupplyComposer('rightSupplyInfos')
        self._allyIDsComposer = SupplySortedIDsComposer('leftSupplyIDs', isAlly=True)
        self._enemyIDsComposer = SupplySortedIDsComposer('rightSupplyIDs', isAlly=False)

    def destroy(self):
        self.clear()
        self._allySupplyComposer = None
        self._enemySupplyComposer = None
        self._allyIDsComposer = None
        self._enemyIDsComposer = None
        return

    def clear(self):
        self._allySupplyComposer.clear()
        self._enemySupplyComposer.clear()
        self._allyIDsComposer.clear()
        self._enemyIDsComposer.clear()

    def get(self, forced=False):
        data = {}
        self._allySupplyComposer.compose(data)
        self._enemySupplyComposer.compose(data)
        self._allyIDsComposer.compose(data)
        self._enemyIDsComposer.compose(data)
        return data

    def update(self, arenaDP):
        self._allySupplyComposer.clear()
        self._enemySupplyComposer.clear()
        for composer, isAlly in ((self._allySupplyComposer, True), (self._enemySupplyComposer, False)):
            for vInfo in SupplyInfoCollection(SupplySortKey, isAlly=isAlly).iterator(arenaDP):
                vStats = arenaDP.getVehicleStats(vInfo.vehicleID)
                composer.create(vInfo)
                composer.updateCounters(vInfo, vInfo.isAlive(), vStats.frags)

        self._allyIDsComposer.update(arenaDP)
        self._enemyIDsComposer.update(arenaDP)
