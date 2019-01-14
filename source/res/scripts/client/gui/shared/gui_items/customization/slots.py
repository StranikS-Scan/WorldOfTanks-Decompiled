# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/slots.py
from shared_utils import first
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import ProjectionDecalDirectionTags, ProjectionDecalFormTags, ProjectionDecalPositionTags
ANCHOR_TYPE_TO_SLOT_TYPE_MAP = {'inscription': GUI_ITEM_TYPE.INSCRIPTION,
 'player': GUI_ITEM_TYPE.EMBLEM,
 'paint': GUI_ITEM_TYPE.PAINT,
 'camouflage': GUI_ITEM_TYPE.CAMOUFLAGE,
 'projectionDecal': GUI_ITEM_TYPE.PROJECTION_DECAL,
 'style': GUI_ITEM_TYPE.STYLE,
 'effect': GUI_ITEM_TYPE.MODIFICATION}
SLOT_TYPE_TO_ANCHOR_TYPE_MAP = {v:k for k, v in ANCHOR_TYPE_TO_SLOT_TYPE_MAP.iteritems()}

class EmblemSlot(object):
    __slots__ = ('_areaId', '_regionIdx', '_descriptor')

    def __init__(self, emblemSlotDescriptor, areaId, regionIdx):
        self._areaId = areaId
        self._regionIdx = regionIdx
        self._descriptor = emblemSlotDescriptor

    @property
    def type(self):
        return self.descriptor.type

    @property
    def areaId(self):
        return self._areaId

    @property
    def regionIdx(self):
        return self._regionIdx

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def rayStart(self):
        return self.descriptor.rayStart

    @property
    def rayEnd(self):
        return self.descriptor.rayEnd

    @property
    def rayUp(self):
        return self.descriptor.rayUp

    @property
    def size(self):
        return self.descriptor.size

    @property
    def hideIfDamaged(self):
        return self.descriptor.hideIfDamaged

    @property
    def isMirrored(self):
        return self.descriptor.isMirrored

    @property
    def isUVProportional(self):
        return self.descriptor.isUVProportional

    @property
    def emblemId(self):
        return self.descriptor.emblemId

    @property
    def slotId(self):
        return self.descriptor.slotId

    @property
    def applyToFabric(self):
        return self.descriptor.applyToFabric


class BaseCustomizationSlot(object):
    __slots__ = ('_areaId', '_regionIdx', '_descriptor')

    def __init__(self, customizationSlotDescriptor, areaId, regionIdx):
        self._areaId = areaId
        self._regionIdx = regionIdx
        self._descriptor = customizationSlotDescriptor

    @property
    def type(self):
        return self.descriptor.type

    @property
    def slotId(self):
        return self.descriptor.slotId

    @property
    def anchorPosition(self):
        return self.descriptor.anchorPosition

    @property
    def anchorDirection(self):
        return self.descriptor.anchorDirection

    @property
    def areaId(self):
        return self._areaId

    @property
    def regionIdx(self):
        return self._regionIdx

    @property
    def descriptor(self):
        return self._descriptor


class ProjectionDecalSlot(BaseCustomizationSlot):
    __slots__ = ('_childs',)

    def __init__(self, customizationSlotDescriptior, areaId, regionIdx):
        super(ProjectionDecalSlot, self).__init__(customizationSlotDescriptior, areaId, regionIdx)
        self._childs = {formfactor:[self.slotId] for formfactor in ProjectionDecalFormTags.ALL}

    @property
    def applyTo(self):
        return self.descriptor.applyTo

    @property
    def position(self):
        return self.descriptor.position

    @property
    def rotation(self):
        return self.descriptor.rotation

    @property
    def scale(self):
        return self.descriptor.scale

    @property
    def scaleFactors(self):
        return self.descriptor.scaleFactors

    @property
    def doubleSided(self):
        return self.descriptor.doubleSided

    @property
    def showOn(self):
        return self.descriptor.showOn

    @property
    def tags(self):
        return self.descriptor.tags

    @property
    def direction(self):
        directionTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalDirectionTags.PREFIX))
        return first(directionTags, ProjectionDecalDirectionTags.ANY)

    @property
    def formfactors(self):
        return tuple((tag for tag in self.tags if tag.startswith(ProjectionDecalFormTags.PREFIX))) or (ProjectionDecalFormTags.ANY,)

    @property
    def positionTag(self):
        positionTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalPositionTags.PREFIX))
        return first(positionTags, None)

    @property
    def parentSlotId(self):
        return self.descriptor.parentSlotId

    @property
    def isChild(self):
        return self.parentSlotId is not None

    @property
    def isParent(self):
        return self.parentSlotId is None

    def getChilds(self, formfactor):
        return self._childs[formfactor]

    def addChild(self, anchor):
        if ProjectionDecalFormTags.ANY in anchor.formfactors:
            for formfactor in ProjectionDecalFormTags.ALL:
                self._childs[formfactor].append(anchor.slotId)

        else:
            for formfactor in anchor.formfactors:
                self._childs[formfactor].append(anchor.slotId)
                self._childs[ProjectionDecalFormTags.ANY].append(anchor.slotId)
