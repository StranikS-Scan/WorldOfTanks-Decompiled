# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/projection_decal.py
from collections import OrderedDict
from constants import IS_EDITOR
from items.components.c11n_constants import ApplyArea, Options, DEFAULT_SCALE_FACTOR_ID, DEFAULT_SCALE, DEFAULT_ROTATION, DEFAULT_POSITION, DEFAULT_DECAL_TINT_COLOR, ProjectionDecalMatchingTags
from serialization import FieldFlags
from serialization.field import intField, optionsEnumField, xmlOnlyApplyAreaEnumField, xmlOnlyFloatArrayField, xmlOnlyIntField, intArrayField, xmlOnlyTagsField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('ProjectionDecalComponent',)

class ProjectionDecalComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.PROJECTION_DECAL
    fields = OrderedDict((('id', intField()),
     ('options', optionsEnumField(Options.NONE)),
     ('slotId', intField(0)),
     ('scaleFactorId', intField(DEFAULT_SCALE_FACTOR_ID)),
     ('showOn', xmlOnlyApplyAreaEnumField(ApplyArea.NONE, FieldFlags.SAVE_AS_STRING)),
     ('scale', xmlOnlyFloatArrayField()),
     ('rotation', xmlOnlyFloatArrayField()),
     ('position', xmlOnlyFloatArrayField()),
     ('tintColor', intArrayField(flags=FieldFlags.NON_BIN if not IS_EDITOR else FieldFlags.NONE)),
     ('doubleSided', xmlOnlyIntField(0)),
     ('tags', xmlOnlyTagsField(())),
     ('preview', xmlOnlyIntField(0)),
     ('progressionLevel', intField(0))))
    __slots__ = ('id', 'options', 'slotId', 'scaleFactorId', 'showOn', 'scale', 'rotation', 'position', 'tintColor', 'doubleSided', 'tags', 'preview', 'progressionLevel')

    def __init__(self, id=0, options=Options.NONE, slotId=0, scaleFactorId=DEFAULT_SCALE_FACTOR_ID, showOn=ApplyArea.NONE, scale=DEFAULT_SCALE, rotation=DEFAULT_ROTATION, position=DEFAULT_POSITION, tintColor=DEFAULT_DECAL_TINT_COLOR, doubleSided=0, tags=None, preview=False, progressionLevel=0):
        self.id = id
        self.options = options
        self.slotId = slotId
        self.scaleFactorId = scaleFactorId
        self.showOn = showOn
        self.scale = scale
        self.rotation = rotation
        self.position = position
        self.tintColor = tintColor
        self.doubleSided = doubleSided
        self.tags = tags
        self.preview = preview
        self.progressionLevel = progressionLevel
        super(ProjectionDecalComponent, self).__init__()

    def __str__(self):
        return 'ProjectionDecalComponent(id={0}, options={1}, slotId={2}, scaleFactorId={3}, showOn={4}, scale={5}, rotation={6}, position={7}, tintColor={8}, doubleSided={9}, preview={10}, progressionLevel={11})'.format(self.id, self.options, self.slotId, self.scaleFactorId, self.showOn, self.scale, self.rotation, self.position, self.tintColor, self.doubleSided, self.preview, self.progressionLevel)

    def isMirroredHorizontally(self):
        return self.options & Options.MIRRORED_HORIZONTALLY

    def isMirroredVertically(self):
        return self.options & Options.MIRRORED_VERTICALLY

    def isFilled(self):
        return (any(self.position) or bool(self.slotId)) and not self.preview

    @property
    def matchingTag(self):
        if self.tags:
            for tag in self.tags:
                if tag in ProjectionDecalMatchingTags.ALL:
                    return tag

        return None
