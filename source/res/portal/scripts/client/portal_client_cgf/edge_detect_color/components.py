# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/edge_detect_color/components.py
import CGF
import Math
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty
_DEFAULT_FILL_COLOR = Math.Vector4(0.561, 0.816, 0.863, 1)
_DEFAULT_SOLID_OVERLAY = Math.Vector4(0.561, 0.816, 0.863, 0.5)
_DEFAULT_SOLID_DESTRUCTIBLE = Math.Vector4(0.35, 0.55, 0.58, 0.5)
_DEFAULT_PATTERN_OVERLAY = Math.Vector4(0.22, 0.35, 0.38, 0.25)
_DEFAULT_PATTERN_OVERLAY_FOREGROUND = Math.Vector4(0.561, 0.816, 0.863, 1)
_DEFAULT_PATTERN_DESTRUCTIBLE = Math.Vector4(0.22, 0.35, 0.38, 0.25)
_DEFAULT_PATTERN_DESTRUCTIBLE_FOREGROUND = Math.Vector4(0.561, 0.816, 0.863, 1)
_COLOR_PICKER = {'colorPicker': {'255Range': False,
                 'useAlpha': True}}

@registerComponent
class EdgeDetectFillColorComponent(object):
    category = 'Portal'
    editorTitle = 'Edge Detect Fill Color'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    fillColor = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Fill Color', value=_DEFAULT_FILL_COLOR, annotations=_COLOR_PICKER)
    solidOverlay = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Solid Overlay', value=_DEFAULT_SOLID_OVERLAY, annotations=_COLOR_PICKER)
    solidDestructible = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Solid Destructible', value=_DEFAULT_SOLID_DESTRUCTIBLE, annotations=_COLOR_PICKER)
    patternOverlayForeground = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Pattern Overlay Foreground', value=_DEFAULT_PATTERN_OVERLAY_FOREGROUND, annotations=_COLOR_PICKER)
    patternOverlay = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Pattern Overlay', value=_DEFAULT_PATTERN_OVERLAY, annotations=_COLOR_PICKER)
    patternDestructibleForeground = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Pattern Destructible Foreground', value=_DEFAULT_PATTERN_DESTRUCTIBLE_FOREGROUND, annotations=_COLOR_PICKER)
    patternDestructible = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Teammate Pattern Destructible', value=_DEFAULT_PATTERN_DESTRUCTIBLE, annotations=_COLOR_PICKER)
