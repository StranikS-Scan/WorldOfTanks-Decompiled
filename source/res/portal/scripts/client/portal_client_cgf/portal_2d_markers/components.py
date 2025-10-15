# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/portal_2d_markers/components.py
import CGF
import logging
from portal_constants import PORTAL_GUI_MARKERS_2D, PORTAL_GUI_MARKERS_MINIMAP
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
_logger = logging.getLogger(__name__)

@registerComponent
class PortalAreaMarker(object):
    category = 'Portal'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Portal Area Marker'
    stateID = ComponentProperty(type=CGFMetaTypes.INT, editorName='state ID', value=-1)
    cullDistance = ComponentProperty(type=CGFMetaTypes.INT, editorName='Distance in which marker will be visible', value=500)
    hasProgressBar = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Has progress bar', value=False)
    hasTimerBoard = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Has timer board', value=False)
    marker2DEntryID = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker2DEntryID', value='No marker', annotations={'comboBox': {'Portal HP marker': PORTAL_GUI_MARKERS_2D.BOSS_HP_MARKER,
                  'Portal marker': PORTAL_GUI_MARKERS_2D.PORTAL_MARKER,
                  'Trap marker': PORTAL_GUI_MARKERS_2D.TRAP_MARKER,
                  'No marker': PORTAL_GUI_MARKERS_2D.NO_MARKER}})
    markerMinimapEntryID = ComponentProperty(type=CGFMetaTypes.STRING, editorName='markerMinimapEntryID', value='No marker', annotations={'comboBox': {'Portal marker': PORTAL_GUI_MARKERS_MINIMAP.PORTAL_MINIMAP_ENTRY,
                  'Trap marker': PORTAL_GUI_MARKERS_MINIMAP.TRAP_MINIMAP_ENTRY,
                  'Minefield marker': PORTAL_GUI_MARKERS_MINIMAP.MINEFIELD_MINIMAP_ENTRY,
                  'Frontier Observer Active': PORTAL_GUI_MARKERS_MINIMAP.FRONTIER_OBSERVER_ACTIVE,
                  'Frontier Observer Inactive': PORTAL_GUI_MARKERS_MINIMAP.FRONTIER_OBSERVER_INACTIVE,
                  'No marker': PORTAL_GUI_MARKERS_MINIMAP.NO_MARKER}})

    def __init__(self):
        self.id = None
        return
