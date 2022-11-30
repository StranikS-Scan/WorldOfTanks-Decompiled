# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/newyear_cgf_components/lobby_components.py
import CGF
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes

class CelebrityDecorationsComponent(CGFComponent):
    editorTitle = 'Celebrity Decorations'
    category = 'New Year'
    garland = ComponentProperty(type=CGFMetaTypes.LINK, editorName='garland', value=CGF.GameObject)
    snowman = ComponentProperty(type=CGFMetaTypes.LINK, editorName='snowman', value=CGF.GameObject)
    bridgeTrain = ComponentProperty(type=CGFMetaTypes.LINK, editorName='bridgeTrain', value=CGF.GameObject)
    bridgeSnow = ComponentProperty(type=CGFMetaTypes.LINK, editorName='bridgeSnow', value=CGF.GameObject)
    bridgeGarland = ComponentProperty(type=CGFMetaTypes.LINK, editorName='bridgeGarland', value=CGF.GameObject)
    rinkSnow = ComponentProperty(type=CGFMetaTypes.LINK, editorName='rinkSnow', value=CGF.GameObject)
    rinkSkatersDeferred = ComponentProperty(type=CGFMetaTypes.LINK, editorName='rinkSkatersDeferred', value=CGF.GameObject)
    rinkSkatersForward = ComponentProperty(type=CGFMetaTypes.LINK, editorName='rinkSkatersForward', value=CGF.GameObject)
    sparklers = ComponentProperty(type=CGFMetaTypes.LINK, editorName='sparklers', value=CGF.GameObject)


class CelebrityAnimationsComponent(CGFComponent):
    editorTitle = 'Celebrity Animations'
    category = 'New Year'
    dumbbell = ComponentProperty(type=CGFMetaTypes.LINK, editorName='dumbbell', value=CGF.GameObject)
    dumbbellsStand = ComponentProperty(type=CGFMetaTypes.LINK, editorName='dumbbellsStand', value=CGF.GameObject)
    glasses = ComponentProperty(type=CGFMetaTypes.LINK, editorName='glasses', value=CGF.GameObject)
    bazooka = ComponentProperty(type=CGFMetaTypes.LINK, editorName='bazooka', value=CGF.GameObject)
    photo = ComponentProperty(type=CGFMetaTypes.LINK, editorName='photo', value=CGF.GameObject)
    passport = ComponentProperty(type=CGFMetaTypes.LINK, editorName='passport', value=CGF.GameObject)
    zombie = ComponentProperty(type=CGFMetaTypes.LINK, editorName='zombie', value=CGF.GameObject)
    mouse = ComponentProperty(type=CGFMetaTypes.LINK, editorName='mouse', value=CGF.GameObject)
    bowl = ComponentProperty(type=CGFMetaTypes.LINK, editorName='bowl', value=CGF.GameObject)
    food = ComponentProperty(type=CGFMetaTypes.LINK, editorName='food', value=CGF.GameObject)
    lamp = ComponentProperty(type=CGFMetaTypes.LINK, editorName='lamp', value=CGF.GameObject)


class MegaDecorationsComponent(CGFComponent):
    editorTitle = 'Mega Decorations'
    category = 'New Year'
    airship = ComponentProperty(type=CGFMetaTypes.LINK, editorName='airship', value=CGF.GameObject)
    castle = ComponentProperty(type=CGFMetaTypes.LINK, editorName='castle', value=CGF.GameObject)
    inactive_ferris_wheel = ComponentProperty(type=CGFMetaTypes.LINK, editorName='inactive_ferris_wheel', value=CGF.GameObject)
    active_ferris_wheel = ComponentProperty(type=CGFMetaTypes.LINK, editorName='active_ferris_wheel', value=CGF.GameObject)


class ResourcesPlaceComponent(CGFComponent):
    editorTitle = 'Resources Place'
    category = 'New Year'
