# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/customization_slot_tags_validator.py
from items.components import c11n_constants

def customizationSlotTagsValidator(tag):
    availableTags = c11n_constants.ProjectionDecalDirectionTags.ALL + c11n_constants.ProjectionDecalFormTags.ALL + c11n_constants.ProjectionDecalPreferredTags.ALL + (c11n_constants.HIDDEN_FOR_USER_TAG,)
    return True if tag in availableTags else tag.endswith(c11n_constants.MATCHING_TAGS_SUFFIX)
