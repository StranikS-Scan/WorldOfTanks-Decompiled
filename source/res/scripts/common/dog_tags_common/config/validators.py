# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/config/validators.py
import typing
from dog_tags_common.config.common import ValidateException, TRIUMPH_GRADES, SKILL_GRADES, STARTING_COMPONENT_TYPES, DEDICATION_GRADES
if typing.TYPE_CHECKING:
    from dog_tag_framework import ComponentDefinition, StartingComponents
    from common import ComponentPurpose, ComponentViewType

def validateCommon(component):
    if component.isDefault and component.isHidden:
        raise ValidateException(ValidateException.DEFAULT_HIDDEN, component.componentId)


def validateTriumphMedal(component):
    if component.grades is not None and len(component.grades) != 0:
        raise ValidateException(ValidateException.HAS_GRADES, component.componentId, component.grades)
    return


def validateTriumph(component):
    if component.grades is None or len(component.grades) != TRIUMPH_GRADES:
        raise ValidateException(ValidateException.WRONG_NUMBER_OF_GRADES, component.componentId, TRIUMPH_GRADES)
    if component.isDefault and component.grades[0] > 0:
        raise ValidateException(ValidateException.DEFAULT_WRONG_GRADES, component.componentId, component.grades)
    return


def validateSkill(component):
    if component.grades is None or len(component.grades) != SKILL_GRADES:
        raise ValidateException(ValidateException.WRONG_NUMBER_OF_GRADES, component.componentId, SKILL_GRADES)
    if component.isDefault and component.grades[0] > 0:
        raise ValidateException(ValidateException.DEFAULT_WRONG_GRADES, component.componentId, component.grades)
    return


def validateDedication(component):
    if component.grades is None or len(component.grades) != DEDICATION_GRADES:
        raise ValidateException(ValidateException.WRONG_NUMBER_OF_GRADES, component.componentId, DEDICATION_GRADES)
    if component.isDefault and component.grades[0] > 0:
        raise ValidateException(ValidateException.DEFAULT_WRONG_GRADES, component.componentId, component.grades)
    return


def validateDedicationUnlock(component):
    if bool(component.unlockKey) == component.isDefault:
        raise ValidateException(ValidateException.SHOULD_BE_DEFAULT_OR_HAS_UNLOCK_KEY, component.componentId, component.grades)


def validateBase(component):
    if component.unlockKey is not None and len(component.unlockKey) != 0:
        raise ValidateException(ValidateException.HAS_UNLOCK_KEY, component.componentId, component.unlockKey)
    if component.grades is not None and len(component.grades) != 0:
        raise ValidateException(ValidateException.HAS_GRADES, component.componentId, component.grades)
    return


def validateViewType(component, viewType, purpose):
    if component.viewType is None or component.viewType != viewType:
        raise ValidateException(ValidateException.WRONG_TYPE_VIEW_COMBINATION, component.componentId, purpose, component.viewType)
    return


def validateStartingComponent(component):
    cache = []
    for c in component.components:
        if not c.isDefault:
            raise ValidateException(ValidateException.STARTING_COMPONENT_NON_DEFAULT, c.componentId)
        if c.viewType is None or c.viewType not in STARTING_COMPONENT_TYPES:
            raise ValidateException(ValidateException.STARTING_COMPONENT_INVALID_TYPE, 'None' if c.viewType is None else c.viewType.value.lower())
        cache.append(c.viewType.value)

    if sorted(cache) != sorted([ x.value for x in STARTING_COMPONENT_TYPES ]):
        raise ValidateException(ValidateException.STARTING_COMPONENT_WRONG_DATA, [ x.value for x in STARTING_COMPONENT_TYPES ], cache)
    return
