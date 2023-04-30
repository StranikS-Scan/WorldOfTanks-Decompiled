# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/slots.py
import logging
from shared_utils import first
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import ProjectionDecalFormTags, SLOT_DEFAULT_ALLOWED_MODEL, ProjectionDecalMatchingTags
from gui.shared.gui_items.customization import directionByTag
_logger = logging.getLogger(__name__)
SLOT_ASPECT_RATIO = {GUI_ITEM_TYPE.EMBLEM: 1.0,
 GUI_ITEM_TYPE.INSCRIPTION: 0.5}
FORMFACTOR_ASPECT_RATIO = {ProjectionDecalFormTags.SQUARE: 1.0,
 ProjectionDecalFormTags.RECT1X2: 1.0 / 2,
 ProjectionDecalFormTags.RECT1X3: 1.0 / 3,
 ProjectionDecalFormTags.RECT1X4: 1.0 / 4,
 ProjectionDecalFormTags.RECT1X6: 1.0 / 6}

class BaseSlot(object):
    __slots__ = ('_areaId', '_regionIdx', '_descriptor')

    def __init__(self, descriptor, areaId, regionIdx):
        self._areaId = areaId
        self._regionIdx = regionIdx
        self._descriptor = descriptor

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
    def hiddenForUser(self):
        return False

    @property
    def compatibleModels(self):
        return (SLOT_DEFAULT_ALLOWED_MODEL,)


class EmblemSlot(BaseSlot):

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

    @property
    def planeProjection(self):
        return self.descriptor.planeProjection


class BaseCustomizationSlot(BaseSlot):

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

    @property
    def applyTo(self):
        return self.descriptor.applyTo

    @property
    def tags(self):
        return self.descriptor.tags

    @property
    def hiddenForUser(self):
        return self.descriptor.hiddenForUser

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
    def direction(self):
        return directionByTag(self.tags)

    @property
    def canBeMirroredVertically(self):
        return self.descriptor.canBeMirroredVertically

    @property
    def formfactors(self):
        return tuple((tag for tag in self.tags if tag.startswith(ProjectionDecalFormTags.PREFIX)))

    @property
    def matchingTag(self):
        for tag in self.tags:
            if tag in ProjectionDecalMatchingTags.ALL:
                return tag

        return None

    def isFitForFormfactor(self, formfactor):
        return formfactor in self.formfactors

    @property
    def compatibleModels(self):
        return self._descriptor.compatibleModels


def getProgectionDecalAspect(slotDescriptor):
    formfactor = first((tag for tag in slotDescriptor.tags if tag.startswith(ProjectionDecalFormTags.PREFIX)))
    if formfactor not in FORMFACTOR_ASPECT_RATIO:
        _logger.warning('Missing aspect ratio for forfactor: %s', formfactor)
        return 1.0
    return FORMFACTOR_ASPECT_RATIO[formfactor]
