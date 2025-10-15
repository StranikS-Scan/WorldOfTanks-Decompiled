# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_constants.py
import constants
from constants_utils import ConstInjector
from enum import IntEnum
from portal.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_crew import CrewId
from portal_common.portal_constants import CampMarkerStatesIDs, TeleportMarkerStatesIDs
PORTAL_BANNER_ENTRY_POINT = 'PortalBannerEntryPoint'
PORTAL_HANGAR_SCENE = 'PORTAL'
PORTAL_HANGAR_SPACE_PATH = 'spaces/h13_mt_portal_2025'

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    PORTAL = 301


class PORTAL_BATTLE_CTRL_ID(IntEnum):
    PORTAL_MARKERS_CTRL = 100
    EFFECTS_CTRL = 101


class PORTAL_GUI_MARKERS_2D(object):
    NO_MARKER = None
    PORTAL_MARKER = 'PortalMarkerUI'
    TRAP_MARKER = 'PortalTrapMarkerUI'
    BASE_MARKER = 'PortalPlayersBaseMarkerUI'
    HOOK_CAMP_MARKER = 'PortalHookCampMarkerUI'
    HORSE_CAMP_MARKER = 'PortalHorseCampMarkerUI'
    PERSPECTIVE_CAMP_MARKER = 'PortalPerspectiveCampMarkerUI'
    SATELITE_CAMP_MARKER = 'PortalSateliteCampMarkerUI'
    HOOK_TP_READY_MARKER = 'PortalHookTpReadyMarkerUI'
    HORSE_TP_READY_MARKER = 'PortalHorseTpReadyMarkerUI'
    PERSPECTIVE_TP_READY_MARKER = 'PortalPerspectiveTpReadyMarkerUI'
    SATELITE_TP_READY_MARKER = 'PortalSateliteTpReadyMarkerUI'
    HOOK_TP_USED_MARKER = 'PortalHookTpMarkerUI'
    HORSE_TP_USED_MARKER = 'PortalHorseTpMarkerUI'
    PERSPECTIVE_TP_USED_MARKER = 'PortalPerspectiveTpMarkerUI'
    SATELITE_TP_USED_MARKER = 'PortalSateliteTpMarkerUI'
    HOOK_TP_COOLDOWN_MARKER = 'PortalHookTpCooldownMarkerUI'
    HORSE_TP_COOLDOWN_MARKER = 'PortalHorseTpCooldownMarkerUI'
    PERSPECTIVE_TP_COOLDOWN_MARKER = 'PortalPerspectiveTpCooldownMarkerUI'
    SATELITE_TP_COOLDOWN_MARKER = 'PortalSateliteTpCooldownMarkerUI'
    BOSS_HP_MARKER = 'PortalVehicleMarker'


class PORTAL_GUI_MARKERS_MINIMAP(object):
    NO_MARKER = None
    BASE_MARKER = 'PortalPlayersBaseMinimapEntryUI'
    PORTAL_MINIMAP_ENTRY = 'PortalMinimapEntryUI'
    TRAP_MINIMAP_ENTRY = 'PortalTrapMinimapEntryUI'
    MINEFIELD_MINIMAP_ENTRY = 'PortalMinefieldMinimapEntryUI'
    BASE_MINIMAP_ENTRY = 'PortalPlayersBaseMinimapEntryUI'
    HOOK_CAMP_MINIMAP_ENTRY = 'PortalHookCampMinimapEntryUI'
    HORSE_CAMP_MINIMAP_ENTRY = 'PortalHorseCampMinimapEntryUI'
    PERSPECTIVE_CAMP_MINIMAP_ENTRY = 'PortalPerspectiveCampMinimapEntryUI'
    SATELITE_CAMP_MINIMAP_ENTRY = 'PortalSateliteCampMinimapEntryUI'
    HOOK_TP_USED_MINIMAP_ENTRY = 'PortalHookTpMinimapEntryUI'
    HORSE_TP_USED_MINIMAP_ENTRY = 'PortalHorseTpMinimapEntryUI'
    PERSPECTIVE_TP_USED_MINIMAP_ENTRY = 'PortalPerspectiveTpMinimapEntryUI'
    SATELITE_TP_USED_MINIMAP_ENTRY = 'PortalSateliteTpMinimapEntryUI'
    HOOK_TP_COOLDOWN_MINIMAP_ENTRY = 'PortalHookTpCooldownMinimapEntryUI'
    HORSE_TP_COOLDOWN_MINIMAP_ENTRY = 'PortalHorseTpCooldownMinimapEntryUI'
    PERSPECTIVE_TP_COOLDOWN_MINIMAP_ENTRY = 'PortalPerspectiveTpCooldownMinimapEntryUI'
    SATELITE_TP_COOLDOWN_MINIMAP_ENTRY = 'PortalSateliteTpCooldownMinimapEntryUI'
    FRONTIER_OBSERVER_INACTIVE = 'PortalFrontierObserverInactiveMinimapEntryUI'
    FRONTIER_OBSERVER_ACTIVE = 'PortalFrontierObserverActiveMinimapEntryUIcopy'


class PORTAL_FRONTIER_MARKERS(object):
    VASILIEVA = {'camp': {'markers2d': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_2D.SATELITE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_2D.SATELITE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAPTURED: None},
              'markersMinimap': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_MINIMAP.SATELITE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.SATELITE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.NO_MARKER}},
     'teleport': {'markers2d': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_2D.SATELITE_TP_READY_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_2D.SATELITE_TP_USED_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_2D.SATELITE_TP_COOLDOWN_MARKER},
                  'markersMinimap': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_MINIMAP.SATELITE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_MINIMAP.SATELITE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_MINIMAP.SATELITE_TP_COOLDOWN_MINIMAP_ENTRY}}}
    KOSHCHEEVA = {'camp': {'markers2d': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_2D.PERSPECTIVE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_2D.PERSPECTIVE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAPTURED: None},
              'markersMinimap': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_MINIMAP.PERSPECTIVE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.PERSPECTIVE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.NO_MARKER}},
     'teleport': {'markers2d': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_2D.PERSPECTIVE_TP_READY_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_2D.PERSPECTIVE_TP_USED_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_2D.PERSPECTIVE_TP_COOLDOWN_MARKER},
                  'markersMinimap': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_MINIMAP.PERSPECTIVE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_MINIMAP.PERSPECTIVE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_MINIMAP.PERSPECTIVE_TP_COOLDOWN_MINIMAP_ENTRY}}}
    YAGINSKAYA = {'camp': {'markers2d': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_2D.HOOK_CAMP_MARKER,
                            CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_2D.HOOK_CAMP_MARKER,
                            CampMarkerStatesIDs.CAPTURED: None},
              'markersMinimap': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_MINIMAP.HOOK_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.HOOK_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.NO_MARKER}},
     'teleport': {'markers2d': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_2D.HOOK_TP_READY_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_2D.HOOK_TP_USED_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_2D.HOOK_TP_COOLDOWN_MARKER},
                  'markersMinimap': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_MINIMAP.HOOK_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_MINIMAP.HOOK_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_MINIMAP.HOOK_TP_COOLDOWN_MINIMAP_ENTRY}}}
    TSAREV = {'camp': {'markers2d': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_2D.HORSE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_2D.HORSE_CAMP_MARKER,
                            CampMarkerStatesIDs.CAPTURED: None},
              'markersMinimap': {CampMarkerStatesIDs.DEFAULT_CAMP: PORTAL_GUI_MARKERS_MINIMAP.HORSE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAN_BE_CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.HORSE_CAMP_MINIMAP_ENTRY,
                                 CampMarkerStatesIDs.CAPTURED: PORTAL_GUI_MARKERS_MINIMAP.NO_MARKER}},
     'teleport': {'markers2d': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_2D.HORSE_TP_READY_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_2D.HORSE_TP_USED_MARKER,
                                TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_2D.HORSE_TP_COOLDOWN_MARKER},
                  'markersMinimap': {TeleportMarkerStatesIDs.DEFAULT_TELEPORT: PORTAL_GUI_MARKERS_MINIMAP.HORSE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_OCCUPIED: PORTAL_GUI_MARKERS_MINIMAP.HORSE_TP_USED_MINIMAP_ENTRY,
                                     TeleportMarkerStatesIDs.TELEPORT_COOLDOWN: PORTAL_GUI_MARKERS_MINIMAP.HORSE_TP_COOLDOWN_MINIMAP_ENTRY}}}


PORTAL_VEHICLE_TOOLTIP_DATA = {5120257: {'damage': 4,
           'mobility': 1,
           'armor': 4,
           'reload': 1,
           'hp': 4,
           'crewID': CrewId.KOSHCHEYEV},
 5120321: {'damage': 2,
           'mobility': 4,
           'armor': 1,
           'reload': 4,
           'hp': 2,
           'crewID': CrewId.VASILIEVA},
 5120337: {'damage': 3,
           'mobility': 2,
           'armor': 3,
           'reload': 3,
           'hp': 3,
           'crewID': CrewId.TSAREV},
 5120401: {'damage': 3,
           'mobility': 3,
           'armor': 2,
           'reload': 3,
           'hp': 3,
           'crewID': CrewId.YAGINSKAYA}}

class PORTAL_VIDEO(object):
    INTRO = 'portal_intro'
    OUTRO = 'portal_outro'
