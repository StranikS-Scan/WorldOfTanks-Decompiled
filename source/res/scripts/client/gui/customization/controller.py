# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/controller.py
from collections import namedtuple
from Event import Event
from gui import GUI_SETTINGS
from CurrentVehicle import g_currentVehicle
from gui.shared.ItemsCache import g_itemsCache
from gui.server_events.EventsCache import g_eventsCache
from gui.game_control import g_instance as g_gameControlInstance
from items.vehicles import g_cache as g_vehiclesCache
from items.qualifiers import g_cache as g_qualifiersCache
from gui import g_tankActiveCamouflage
from gui.customization.carousel import Carousel
from gui.customization.quests import Quests
from gui.customization.inventory import Inventory
from gui.customization.data_aggregator import DataAggregator, IgrDataAggregator
from gui.customization.tank_model import TankModel
from gui.customization.slots import Slots
from gui.customization.filter import Filter
from gui.customization.cart import Cart
from gui.customization.bonus_panel import BonusPanel
_ExternalDependencies = namedtuple('ExternalDependencies', 'g_currentVehicle g_questsCache g_itemsCache g_gameControlInstance ' + 'g_vehiclesCache g_tankActiveCamouflage, g_qualifiersCache')

class _Events(object):

    def __init__(self):
        self.onQuestsUpdated = Event()
        self.onInventoryUpdated = Event()
        self.onTankModelAttributesUpdated = Event()
        self.onInstalledElementsUpdated = Event()
        self.onDisplayedElementsAndGroupsUpdated = Event()
        self.onCarouselUpdated = Event()
        self.onFilterUpdated = Event()
        self.onOwnedElementPicked = Event()
        self.onMultiplePurchaseStarted = Event()
        self.onMultiplePurchaseProcessed = Event()
        self.onCarouselElementPicked = Event()
        self.onSlotSelected = Event()
        self.onSlotUpdated = Event()
        self.onSlotsSet = Event()
        self.onInitialSlotsSet = Event()
        self.onTankSlotCleared = Event()
        self.onCartUpdated = Event()
        self.onCartFilled = Event()
        self.onCartEmptied = Event()
        self.onBonusesUpdated = Event()
        self.onCustomizationViewClosed = Event()
        self.onBackToSelectorGroup = Event()


class Controller(object):

    def __init__(self, dependencies):
        self._events = _Events()
        self._dependencies = _ExternalDependencies(*dependencies)
        self._createAttributes()

    def init(self):
        self._quests.init()
        self._inventory.init()
        self._tankModel.init()
        self._carousel.init()
        self._dataAggregator.init()
        self._bonusPanel.init()
        self._cart.init()

    def start(self):
        self._quests.start()
        self._inventory.start()
        self._dataAggregator.start()

    def fini(self):
        self._carousel.fini()
        self._cart.fini()
        self._bonusPanel.fini()
        self._tankModel.fini()
        self._inventory.fini()
        self._quests.fini()
        self._dataAggregator.fini()

    @property
    def dataAggregator(self):
        return self._dataAggregator

    @property
    def carousel(self):
        return self._carousel

    @property
    def cart(self):
        return self._cart

    @property
    def events(self):
        return self._events

    @property
    def tankModel(self):
        return self._tankModel

    @property
    def inventory(self):
        return self._inventory

    @property
    def quests(self):
        return self._quests

    @property
    def bonusPanel(self):
        return self._bonusPanel

    @property
    def slots(self):
        return self._slots

    @property
    def filter(self):
        return self._filter

    def _createAttributes(self):
        if GUI_SETTINGS.igrEnabled:
            self._dataAggregator = IgrDataAggregator(self._events, self._dependencies)
        else:
            self._dataAggregator = DataAggregator(self._events, self._dependencies)
        self._quests = Quests(self._events, self._dependencies)
        self._inventory = Inventory(self._events, self._dependencies)
        self._slots = Slots(self._events)
        self._filter = Filter(self._events)
        self._carousel = Carousel(self._events, self._filter, self._slots, self._dependencies)
        self._tankModel = TankModel(self._events)
        self._cart = Cart(self._events, self._dependencies)
        self._bonusPanel = BonusPanel(self._events)


_externalDependencies = (g_currentVehicle,
 g_eventsCache,
 g_itemsCache,
 g_gameControlInstance,
 g_vehiclesCache,
 g_tankActiveCamouflage,
 g_qualifiersCache)
g_customizationController = Controller(_externalDependencies)
