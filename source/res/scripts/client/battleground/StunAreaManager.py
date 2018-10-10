# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/StunAreaManager.py
from collections import namedtuple
import BigWorld
import Math
import ResMgr
from avatar_components.CombatEquipmentManager import CombatEquipmentManager
from debug_utils import LOG_WARNING
from helpers import dependency
from helpers import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import AOI
_EquipmentAdapter = namedtuple('_EquipmentAdapter', ['areaWidth',
 'areaLength',
 'areaVisual',
 'areaColor',
 'areaMarker'])
_DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_STUN_AREA_VISUAL_SECTION = 'stunAreaVisual'
_DIR_UP = Math.Vector3(0.0, 1.0, 0.0)
STUN_AREA_STATIC_MARKER = 'stunAreaStaticMarker'
_STUN_AREA_DEFAULTS = {'radius': 15.0,
 'areasNum': 3,
 'color': '0xff000000',
 'lifetime': 30.0,
 'visual': 'content/Interface/CheckPoint/CheckPoint_white.visual',
 'lineColor': '0x0ff00000',
 'lineWidth': 3.0,
 'lineHeight': 3.0}

class StunAreaManager(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StunAreaManager, self).__init__()
        self.__callbacksSet = CallbackDelayer.CallbacksSetByID()
        self.__stunAreas = {}
        self.__isGUIVisible = True
        self.__stunAreaParams = self.__getStunAreaParamsConfig()
        self.__resources = {}

    def loadPrerequisites(self):
        prereqs = [self.__stunAreaParams['visual']]
        BigWorld.loadResourceListBG(prereqs, self.__onPrereqsLoaded)

    def clear(self):
        for areas in self.__stunAreas.itervalues():
            for area in areas:
                if area is not None:
                    area.destroy()

        self.__stunAreas = {}
        self.__callbacksSet.clear()
        return

    def manageStunArea(self, position, senderID):
        areaID = senderID
        if areaID in self.__stunAreas:
            self.__callbacksSet.stopCallback(areaID)
            self.__removeArea(areaID)
        distanceFromPlayer = (position - BigWorld.player().position).length
        showArea = distanceFromPlayer <= AOI.VEHICLE_CIRCULAR_AOI_RADIUS
        if showArea:
            areas = []
            for i in xrange(0, self.__stunAreaParams['areasNum']):
                area = self.__createStunArea(position, areaIndex=i)
                if area is not None:
                    area.setGUIVisible(self.__isGUIVisible)
                    areas.append(area)

            self.__stunAreas[areaID] = areas
            if areas:
                areas[0].addLine(position, self.__stunAreaParams['lineColor'], self.__stunAreaParams['lineWidth'], self.__stunAreaParams['lineHeight'])
        else:
            self.__stunAreas[areaID] = []
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            position.y += self.__stunAreaParams['lineHeight'] * 1.1
            ctrl.onStaticMarkerAdded(areaID, position, STUN_AREA_STATIC_MARKER, showArea)
        self.__callbacksSet.delayCallback(areaID, self.__stunAreaParams['lifetime'], self.__removeArea)
        return

    def setGUIVisible(self, visible):
        self.__isGUIVisible = visible
        for areas in self.__stunAreas.itervalues():
            for area in areas:
                area.setGUIVisible(visible)

    @staticmethod
    def __getStunAreaParamsConfig():
        configSection = ResMgr.openSection(_DYNAMIC_OBJECTS_CONFIG_FILE)
        if configSection and configSection.has_key(_STUN_AREA_VISUAL_SECTION):
            configSection = configSection[_STUN_AREA_VISUAL_SECTION]
            return {'radius': configSection.readFloat('radius', _STUN_AREA_DEFAULTS['radius']),
             'areasNum': configSection.readInt('areasNum', _STUN_AREA_DEFAULTS['areasNum']),
             'color': int(configSection.readString('color', _STUN_AREA_DEFAULTS['color']), 0),
             'lifetime': configSection.readFloat('lifetime', _STUN_AREA_DEFAULTS['lifetime']),
             'visual': configSection.readString('visual', _STUN_AREA_DEFAULTS['visual']),
             'lineColor': int(configSection.readString('lineColor', _STUN_AREA_DEFAULTS['lineColor']), 0),
             'lineWidth': configSection.readFloat('lineWidth', _STUN_AREA_DEFAULTS['lineWidth']),
             'lineHeight': configSection.readFloat('lineHeight', _STUN_AREA_DEFAULTS['lineHeight'])}
        return _STUN_AREA_DEFAULTS

    def __onPrereqsLoaded(self, resourceRefs):
        if self.__stunAreaParams['visual'] not in resourceRefs.failedIDs:
            self.__resources = resourceRefs
        else:
            LOG_WARNING('Resource is not found', self.__stunAreaParams['visual'])

    def __createStunArea(self, position, areaIndex):
        markerRadius = self.__stunAreaParams['radius']
        offset = markerRadius / self.__stunAreaParams['areasNum']
        areaDiameter = 2.0 * (markerRadius - areaIndex * offset)
        adaptedAreaDesc = _EquipmentAdapter(areaDiameter, areaDiameter, self.__stunAreaParams['visual'], self.__stunAreaParams['color'], None)
        area = CombatEquipmentManager.createEquipmentSelectedArea(position, _DIR_UP, adaptedAreaDesc)
        return area

    def __removeArea(self, areaID):
        if areaID in self.__stunAreas:
            areas = self.__stunAreas.pop(areaID, [])
            for area in areas:
                if area is not None:
                    area.destroy()

            ctrl = self.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onStaticMarkerRemoved(areaID)
        else:
            LOG_WARNING("Stun area with ID {} doesn't exist!".format(areaID))
        return


g_stunAreaManager = StunAreaManager()
