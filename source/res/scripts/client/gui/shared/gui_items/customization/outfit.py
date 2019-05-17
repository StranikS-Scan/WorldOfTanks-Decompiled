# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/outfit.py
from collections import Counter
from soft_exception import SoftException
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.containers import OutfitContainer, MultiSlot, SizableMultiSlot
from gui.shared.gui_items.gui_item import HasStrCD
from vehicle_systems.tankStructure import TankPartIndexes
from items.components.c11n_constants import ApplyArea, CustomizationType, MAX_PROJECTION_DECALS
from items.customizations import parseOutfitDescr, CustomizationOutfit
from items.vehicles import makeIntCompactDescrByID, getItemByCompactDescr
from helpers import dependency
from shared_utils import isEmpty
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class Area(TankPartIndexes):
    MISC = 4
    TANK_PARTS = TankPartIndexes.ALL
    ALL = TankPartIndexes.ALL + (MISC,)


def scaffold():
    return (OutfitContainer(areaID=Area.CHASSIS, slots=(MultiSlot(slotTypes=(GUI_ITEM_TYPE.PAINT,), regions=ApplyArea.CHASSIS_PAINT_REGIONS),)),
     OutfitContainer(areaID=Area.HULL, slots=(MultiSlot(slotTypes=(GUI_ITEM_TYPE.PAINT,), regions=ApplyArea.HULL_PAINT_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.CAMOUFLAGE,), regions=ApplyArea.HULL_CAMOUFLAGE_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.EMBLEM,), regions=ApplyArea.HULL_EMBLEM_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER), regions=ApplyArea.HULL_INSCRIPTION_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSIGNIA,), regions=ApplyArea.HULL_INSIGNIA_REGIONS))),
     OutfitContainer(areaID=Area.TURRET, slots=(MultiSlot(slotTypes=(GUI_ITEM_TYPE.PAINT,), regions=ApplyArea.TURRET_PAINT_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.CAMOUFLAGE,), regions=ApplyArea.TURRET_CAMOUFLAGE_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.EMBLEM,), regions=ApplyArea.TURRET_EMBLEM_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER), regions=ApplyArea.TURRET_INSCRIPTION_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSIGNIA,), regions=ApplyArea.TURRET_INSIGNIA_REGIONS))),
     OutfitContainer(areaID=Area.GUN, slots=(MultiSlot(slotTypes=(GUI_ITEM_TYPE.PAINT,), regions=ApplyArea.GUN_PAINT_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.CAMOUFLAGE,), regions=ApplyArea.GUN_CAMOUFLAGE_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.EMBLEM,), regions=ApplyArea.GUN_EMBLEM_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER), regions=ApplyArea.GUN_INSCRIPTION_REGIONS),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.INSIGNIA,), regions=ApplyArea.GUN_INSIGNIA_REGIONS))),
     OutfitContainer(areaID=Area.MISC, slots=(MultiSlot(slotTypes=(GUI_ITEM_TYPE.MODIFICATION,), regions=(ApplyArea.NONE,)),
      MultiSlot(slotTypes=(GUI_ITEM_TYPE.PROJECTION_DECAL,), regions=tuple(range(MAX_PROJECTION_DECALS))),
      SizableMultiSlot(slotTypes=(GUI_ITEM_TYPE.SEQUENCE,), regions=[]),
      SizableMultiSlot(slotTypes=(GUI_ITEM_TYPE.ATTACHMENT,), regions=[]))))


REGIONS_BY_SLOT_TYPE = {container.getAreaID():{slotType:slot.getRegions() for slot in container.slots() for slotType in slot.getTypes()} for container in scaffold()}

class Outfit(HasStrCD):
    __slots__ = ('_id', '_styleDescr', '_containers', '_isEnabled', '_isInstalled')
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, strCompactDescr=None, component=None, isEnabled=False, isInstalled=False, proxy=None):
        super(Outfit, self).__init__(strCompactDescr)
        self._containers = {}
        self._isEnabled = isEnabled
        self._isInstalled = isInstalled
        if strCompactDescr is not None and component is not None:
            raise SoftException("'strCompactDescr' and 'component' arguments are mutually exclusive!")
        if strCompactDescr:
            component = parseOutfitDescr(strCompactDescr)
        elif component is None:
            component = CustomizationOutfit()
        self._id = component.styleId
        if self._id:
            intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, self._id)
            self._styleDescr = getItemByCompactDescr(intCD)
        else:
            self._styleDescr = None
        for container in scaffold():
            container.unpack(component, proxy)
            self._containers[container.getAreaID()] = container

        self.invalidate()
        return

    def pack(self):
        component = CustomizationOutfit()
        for container in self._containers.itervalues():
            container.pack(component)

        component.styleId = self._id
        return component

    def copy(self):
        return self.itemsFactory.createOutfit(component=self.pack(), isEnabled=self._isEnabled, isInstalled=self._isInstalled, proxy=self.itemsCache.items)

    def diff(self, other):
        result = Outfit()
        for areaID in self._containers.iterkeys():
            acont = self.getContainer(areaID)
            bcont = other.getContainer(areaID)
            result.setContainer(areaID, acont.diff(bcont))

        return result

    def isEqual(self, other):
        return self.diff(other).isEmpty()

    def getContainer(self, areaID):
        return self._containers.get(areaID)

    def setContainer(self, areaID, container):
        self._containers[areaID] = container

    def has(self, item):
        return any((item.intCD == i.intCD for i in self.items()))

    @property
    def id(self):
        return self._id

    @property
    def hull(self):
        return self.getContainer(Area.HULL)

    @property
    def chassis(self):
        return self.getContainer(Area.CHASSIS)

    @property
    def turret(self):
        return self.getContainer(Area.TURRET)

    @property
    def gun(self):
        return self.getContainer(Area.GUN)

    @property
    def misc(self):
        return self.getContainer(Area.MISC)

    @property
    def modelsSet(self):
        return self._styleDescr.modelsSet if self._styleDescr else ''

    @property
    def attachments(self):
        return self.misc.slotFor(GUI_ITEM_TYPE.ATTACHMENT)

    @property
    def itemsCounter(self):
        return Counter((i.intCD for i in self.items()))

    def containers(self):
        for container in self._containers.itervalues():
            yield container

    def items(self):
        for container in self._containers.itervalues():
            for slot in container.slots():
                for item in slot.values():
                    yield item

    def itemsFull(self):
        for container in self._containers.itervalues():
            for slot in container.slots():
                for _, item, component in slot.items():
                    yield (item, component)

    def slots(self):
        for container in self._containers.itervalues():
            for slot in container.slots():
                yield slot

    def isHistorical(self):
        return self._styleDescr.historical if self._styleDescr else all((item.isHistorical() for item in self.items()))

    def isEmpty(self):
        return isEmpty(self.items())

    def isPredefined(self):
        return self._id != 0

    def isEnabled(self):
        return self._isEnabled

    def isInstalled(self):
        return self._isInstalled

    def isActive(self):
        return self._isEnabled and self._isInstalled

    def clear(self):
        for container in self._containers.itervalues():
            container.clear()

    def invalidate(self):
        for container in self._containers.itervalues():
            container.invalidate()
