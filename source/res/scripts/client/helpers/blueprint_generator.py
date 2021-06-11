# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/blueprint_generator.py
import logging
import typing
from collections import namedtuple
import BigWorld
import Math
import ResMgr
from items import vehicles, parseIntCompactDescr, ITEM_TYPES
from vehicle_systems import model_assembler as ma
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.tankStructure import ModelsSetParams
_logger = logging.getLogger(__name__)
_BLUEPRINT_BG_TEXTURE = 'gui/maps/blueprint_bg.png'
_BLUEPRINT_TEXTURE_PATH = 'img://customTexture:blueprint'
_BLUEPRINT_LAYOUTS_PATH = 'gui/blueprint_layouts.xml'
_BpProjections = namedtuple('BpProjections', ('front', 'left', 'top', 'isometric'))
_BpLayout = namedtuple('BpLayout', ('projections', 'lodIdx'))
_BLUEPRINT_DEFAULT_LAYOUT = _BpLayout(_BpProjections(front=Math.Vector4(220, 140, 0.25, 0.94), left=Math.Vector4(560, 140, 0.25, 0.94), top=Math.Vector4(220, 350, 0.25, 0.94), isometric=Math.Vector4(644, 433, 0.5, 0.94)), lodIdx=3)

class BlueprintGenerator(object):

    def __init__(self):
        self.__cachedCompound = {}
        self.__pendingCompound = set()
        self.__layouts = None
        self.__inProgress = None
        return

    def init(self):
        self.__layouts = self.__readConfig()
        BigWorld.enableBlueprintBuilding(True)

    def fini(self):
        self.__cachedCompound.clear()
        self.__pendingCompound.clear()
        self.__layouts = None
        self.__inProgress = None
        BigWorld.enableBlueprintBuilding(False)
        return

    def generate(self, vehicleCD=None, vehicleName=None, clear=False):
        vehicleDescriptor = self.__getVehicleDescr(vehicleCD, vehicleName)
        if vehicleDescriptor is None:
            return
        else:
            if self.__inProgress != vehicleDescriptor.name:
                if clear:
                    BigWorld.clearBlueprint()
                self.__inProgress = vehicleDescriptor.name
                self.__loadVehicleCompound(vehicleDescriptor)
            return self.__getTexturePath()

    def cancel(self, vehicleCD=None, vehicleName=None):
        if self.__inProgress is None:
            return
        else:
            if vehicleName is None:
                vehicleDescriptor = self.__getVehicleDescr(vehicleCD, vehicleName)
                vehicleName = vehicleDescriptor.name if vehicleDescriptor is not None else None
            if vehicleName is not None and self.__inProgress == vehicleName:
                self.__inProgress = None
            return

    @classmethod
    def __getTexturePath(cls):
        return _BLUEPRINT_TEXTURE_PATH

    def __loadVehicleCompound(self, vehicleDescr):
        vehicleName = vehicleDescr.name
        layout = self.__layouts.get(vehicleName, self.__layouts['default'])
        if vehicleName in self.__cachedCompound:
            _logger.debug('Loaded vehicle compound of "%s" from cache', vehicleName)
            BigWorld.buildBlueprint(self.__cachedCompound[vehicleName], _BLUEPRINT_BG_TEXTURE, layout.projections)
            self.__inProgress = None
            return
        elif vehicleName in self.__pendingCompound:
            _logger.debug('Vehicle compound of "%s" is loading at the moment.', vehicleName)
            return
        else:
            _logger.debug('Loading vehicle compound of "%s".', vehicleName)
            self.__pendingCompound.add(vehicleName)
            resources = (ma.prepareCompoundAssembler(vehicleDescr, ModelsSetParams('', 'undamaged', []), BigWorld.camera().spaceID, lodIdx=layout.lodIdx, skipMaterials=True),)
            BigWorld.loadResourceListBG(resources, makeCallbackWeak(self.__onResourcesLoaded, vehicleName))
            return

    def __onResourcesLoaded(self, vehicleName, resourceRefs):
        failedIDs = resourceRefs.failedIDs
        if failedIDs and vehicleName in failedIDs:
            _logger.error('Failed to load compound model for "%s"', vehicleName)
            return
        else:
            _logger.debug('Loaded compound model for "%s"', vehicleName)
            compound = resourceRefs[vehicleName]
            self.__cachedCompound[vehicleName] = compound
            self.__pendingCompound.remove(vehicleName)
            if vehicleName != self.__inProgress:
                return
            layout = self.__layouts.get(vehicleName, self.__layouts['default'])
            BigWorld.buildBlueprint(compound, _BLUEPRINT_BG_TEXTURE, layout.projections)
            self.__inProgress = None
            return

    def __readConfig(self):
        layouts = {'default': _BLUEPRINT_DEFAULT_LAYOUT}
        try:
            try:
                layoutsSection = ResMgr.openSection(_BLUEPRINT_LAYOUTS_PATH)
                if layoutsSection is None:
                    return layouts
                for layout in layoutsSection.values():
                    bpLayout = _BpLayout(_BpProjections(front=layout['front'].asVector4, left=layout['left'].asVector4, top=layout['top'].asVector4, isometric=layout['isometric'].asVector4), lodIdx=layout['lodIdx'].asInt)
                    if layout.name == 'default':
                        layouts['default'] = bpLayout
                        continue
                    for vehicleName in layout['vehicles'].asString.split():
                        layouts[vehicleName] = bpLayout

            except:
                _logger.exception("Can't read blueprint layouts config")

        finally:
            ResMgr.purge(_BLUEPRINT_LAYOUTS_PATH)

        return layouts

    def __getVehicleDescr(self, vehicleCD=None, vehicleName=None):
        if vehicleCD is not None:
            itemTypeId, nationId, innationId = parseIntCompactDescr(vehicleCD)
        elif vehicleName is not None:
            nationId, innationId = vehicles.g_list.getIDsByName(vehicleName)
        else:
            _logger.error('Do not specified correct vehicle int cd or vehicle name!')
            return
        return vehicles.VehicleDescr(typeID=(nationId, innationId))


g_blueprintGenerator = BlueprintGenerator()
