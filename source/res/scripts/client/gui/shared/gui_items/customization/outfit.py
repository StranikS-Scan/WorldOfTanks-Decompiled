# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/outfit.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.containers import OutfitContainer, MultiSlot
from gui.shared.gui_items.gui_item import HasStrCD
from vehicle_systems.tankStructure import TankPartIndexes
from items.components.c11n_constants import ApplyArea, CustomizationType
from items.customizations import parseCompDescr, CustomizationOutfit
from items.vehicles import makeIntCompactDescrByID
from helpers import dependency
from shared_utils import isEmpty
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class Area(TankPartIndexes):
    MISC = 4


def scaffold():
    """ This function creates a scaffold of container structure of an outfit.
    """
    return (OutfitContainer(areaID=Area.CHASSIS, slots=(MultiSlot(slotType=GUI_ITEM_TYPE.PAINT, regions=ApplyArea.CHASSIS_PAINT_REGIONS),)),
     OutfitContainer(areaID=Area.HULL, slots=(MultiSlot(slotType=GUI_ITEM_TYPE.PAINT, regions=ApplyArea.HULL_PAINT_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.CAMOUFLAGE, regions=ApplyArea.HULL_CAMOUFLAGE_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.EMBLEM, regions=ApplyArea.HULL_EMBLEM_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.INSCRIPTION, regions=ApplyArea.HULL_INSCRIPTION_REGIONS))),
     OutfitContainer(areaID=Area.TURRET, slots=(MultiSlot(slotType=GUI_ITEM_TYPE.PAINT, regions=ApplyArea.TURRET_PAINT_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.CAMOUFLAGE, regions=ApplyArea.TURRET_CAMOUFLAGE_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.EMBLEM, regions=ApplyArea.TURRET_EMBLEM_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.INSCRIPTION, regions=ApplyArea.TURRET_INSCRIPTION_REGIONS))),
     OutfitContainer(areaID=Area.GUN, slots=(MultiSlot(slotType=GUI_ITEM_TYPE.PAINT, regions=ApplyArea.GUN_PAINT_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.CAMOUFLAGE, regions=ApplyArea.GUN_CAMOUFLAGE_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.EMBLEM, regions=ApplyArea.GUN_EMBLEM_REGIONS),
      MultiSlot(slotType=GUI_ITEM_TYPE.INSCRIPTION, regions=ApplyArea.GUN_INSCRIPTION_REGIONS))),
     OutfitContainer(areaID=Area.MISC, slots=(MultiSlot(slotType=GUI_ITEM_TYPE.MODIFICATION, regions=(ApplyArea.NONE,)),)))


class Outfit(HasStrCD):
    """ Complete representation of customization items applied on vehicle.
    
    Outfit consists of containers that represent different parts of a vehicle.
    Each container holds customization items inside slots and capable of
    packing/unpacking itself from/to components (components are serializable
    parts of server representation of outfit).
    
    Each container has few "slots" where items can be put at. These slots
    can be accessed by the type of items that they're storing.
    
    For example, this is how a slot for the hull paint can be accessed:
    
         outfit.hull.slotFor(GUI_ITEM_TYPE.PAINT)  # returns MultiSlot of type PAINT
    
    If you want to, say, get/set a paint for some region, you can pass region id
    to the special get/set methods:
    
        outfit.hull.slotFor(GUI_ITEM_TYPE.PAINT).getItem(idx=regionID)  # returns Paint
        outfit.hull.slotFor(GUI_ITEM_TYPE.PAINT).set(paint, idx=regionID)
    
    Areas can also be accessed using dynamic name:
    
        outfit.getContainer(Area.HULL).slotFor(GUI_ITEM_TYPE.PAINT).getItem(idx=regionID)
    
    """
    __slots__ = ('_id', '_containers', '_isEnabled')
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, strCompactDescr=None, isEnabled=False, proxy=None):
        super(Outfit, self).__init__(strCompactDescr)
        self._containers = {}
        if strCompactDescr:
            component = parseCompDescr(strCompactDescr)
        else:
            component = CustomizationOutfit()
        self._id = component.styleId
        self._isEnabled = isEnabled
        for container in scaffold():
            container.unpack(component, proxy)
            self._containers[container.getAreaID()] = container

        self.invalidate()

    def pack(self):
        """ Pack the current outfit into a component.
        """
        component = CustomizationOutfit()
        for container in self._containers.itervalues():
            container.pack(component)

        component.styleId = self._id
        return component

    def copy(self):
        """ Create an identical outfit for the current one.
        """
        return self.itemsFactory.createOutfit(self.pack().makeCompDescr(), isEnabled=self._isEnabled, proxy=self.itemsCache.items)

    def diff(self, other):
        """ Get difference between two outfits.
        """
        result = Outfit()
        for areaID in self._containers.iterkeys():
            acont = self.getContainer(areaID)
            bcont = other.getContainer(areaID)
            result.setContainer(areaID, acont.diff(bcont))

        return result

    def isEqual(self, other):
        """ Returns True if outfits are identical.
        """
        return self.diff(other).isEmpty()

    def getContainer(self, areaID):
        """ Get a container for the given areaID.
        """
        return self._containers.get(areaID)

    def setContainer(self, areaID, container):
        """ Set a new container for the given areaID.
        """
        self._containers[areaID] = container

    def has(self, item):
        """ Check if outfit has the given item.
        """
        return any((item.intCD == i.intCD for i in self.items()))

    @property
    def id(self):
        """ Get an id of the outfit.
        """
        return self._id

    @property
    def hull(self):
        """ Get a hull container.
        """
        return self.getContainer(Area.HULL)

    @property
    def chassis(self):
        """ Get a chassis container.
        """
        return self.getContainer(Area.CHASSIS)

    @property
    def turret(self):
        """ Get a turret container.
        """
        return self.getContainer(Area.TURRET)

    @property
    def gun(self):
        """ Get a gun container.
        """
        return self.getContainer(Area.GUN)

    @property
    def misc(self):
        """ Get a misc container.
        """
        return self.getContainer(Area.MISC)

    def containers(self):
        """ Iterate over containers of the outfit.
        """
        for container in self._containers.itervalues():
            yield container

    def items(self):
        """ Iterate over items of the outfit.
        """
        for container in self._containers.itervalues():
            for slot in container.slots():
                for item in slot.values():
                    yield item

    def slots(self):
        """ Iterate over slots of the outfit.
        """
        for container in self._containers.itervalues():
            for slot in container.slots():
                yield slot

    def isHistorical(self):
        """ Check if all outfit items are historical.
        """
        if self._id:
            intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, self._id)
            style = self.itemsFactory.createCustomization(intCD)
            return style.isHistorical()
        return all((item.isHistorical() for item in self.items()))

    def isEmpty(self):
        """ Check if outfit is empty.
        """
        return isEmpty(self.items())

    def isPredefined(self):
        """ Check if outfit is predefined (i.e. is inside style).
        """
        return self._id != 0

    def isEnabled(self):
        """ Check if outfit is enabled, i.e. rent is not over
        """
        return self._isEnabled

    def clear(self):
        """ Clear containers in outfit.
        """
        for container in self._containers.itervalues():
            container.clear()

    def invalidate(self):
        """ Populate component in the containers with proper data.
        """
        for container in self._containers.itervalues():
            container.invalidate()
