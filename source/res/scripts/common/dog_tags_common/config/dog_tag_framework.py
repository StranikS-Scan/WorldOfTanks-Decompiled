# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/config/dog_tag_framework.py
import inspect
import sys
from functools import partial
import typing
from common import ParameterType, Visibility, ParseException, ComponentPurpose, ComponentViewType, ComponentNumberType
from validators import validateTriumphMedal, validateTriumph, validateSkill, validateDedication, validateDedicationUnlock, validateBase, validateRankedSkill, validateViewType, validateCommon, validateStartingComponent
if typing.TYPE_CHECKING:
    from typing import List

class XMLObjBuilder(object):

    def __init__(self, componentCls):
        self.__componentCls = componentCls
        self._component = componentCls()

    def reset(self):
        self._component = self.__componentCls()

    def validate(self):
        pass

    def build(self):
        self.validate()
        componentObject = self._component
        self.reset()
        return componentObject


class ComponentBuilder(XMLObjBuilder):
    TAG = 'component'
    PARAMS = {'componentId': (ParameterType.INT, Visibility.ALL),
     'resourceRoot': (ParameterType.STR, Visibility.ALL),
     'viewType': (ParameterType.VIEW_TYPE, Visibility.ALL),
     'purpose': (ParameterType.TYPE, Visibility.ALL),
     'unlockKey': (ParameterType.STR_LIST, Visibility.ALL),
     'progressKey': (ParameterType.STR_LIST, Visibility.ALL),
     'isHidden': (ParameterType.BOOL, Visibility.ALL),
     'isSecret': (ParameterType.BOOL, Visibility.ALL),
     'isDefault': (ParameterType.BOOL, Visibility.ALL),
     'isExternalUnlockOnly': (ParameterType.BOOL, Visibility.ALL),
     'grades': (ParameterType.FLOAT_LIST, Visibility.ALL),
     'isDeprecated': (ParameterType.BOOL, Visibility.ALL),
     'numberType': (ParameterType.NUMBER_TYPE, Visibility.ALL),
     'src': (ParameterType.STR, Visibility.CLIENT),
     'minLevel': (ParameterType.INT, Visibility.ALL),
     'battleTypes': (ParameterType.INT_LIST, Visibility.ALL),
     'glossaryName': (ParameterType.STR, Visibility.ALL)}
    DEFAULTS = {'isSecret': False,
     'isHidden': False,
     'isDefault': False,
     'isDeprecated': False,
     'isExternalUnlockOnly': False,
     'numberType': ComponentNumberType.NUMBER,
     'glossaryName': ''}
    VALIDATORS = {ComponentPurpose.TRIUMPH_MEDAL: [validateCommon, partial(validateViewType, viewType=ComponentViewType.BACKGROUND, purpose=ComponentPurpose.TRIUMPH_MEDAL), validateTriumphMedal],
     ComponentPurpose.TRIUMPH: [validateCommon, partial(validateViewType, viewType=ComponentViewType.ENGRAVING, purpose=ComponentPurpose.TRIUMPH), validateTriumph],
     ComponentPurpose.SKILL: [validateCommon, partial(validateViewType, viewType=ComponentViewType.ENGRAVING, purpose=ComponentPurpose.SKILL), validateSkill],
     ComponentPurpose.DEDICATION: [validateCommon,
                                   partial(validateViewType, viewType=ComponentViewType.ENGRAVING, purpose=ComponentPurpose.DEDICATION),
                                   validateDedication,
                                   validateDedicationUnlock],
     ComponentPurpose.RANKED_SKILL: [validateCommon, partial(validateViewType, viewType=ComponentViewType.ENGRAVING, purpose=ComponentPurpose.RANKED_SKILL), validateRankedSkill],
     ComponentPurpose.BASE: [validateCommon, partial(validateViewType, viewType=ComponentViewType.BACKGROUND, purpose=ComponentPurpose.BASE), validateBase]}

    def __init__(self):
        super(ComponentBuilder, self).__init__(ComponentDefinition)

    def componentId(self, value):
        self._component.componentId = value

    def resourceRoot(self, value):
        self._component.resourceRoot = value

    def viewType(self, value):
        self._component.viewType = value

    def purpose(self, value):
        self._component.purpose = value

    def unlockKey(self, value):
        self._component.unlockKey = value

    def progressKey(self, value):
        self._component.progressKey = value

    def isHidden(self, value):
        self._component.isHidden = value

    def isSecret(self, value):
        self._component.isSecret = value

    def isDefault(self, value):
        self._component.isDefault = value

    def isExternalUnlockOnly(self, value):
        self._component.isExternalUnlockOnly = value

    def grades(self, value):
        self._component.grades = value

    def isDeprecated(self, value):
        self._component.isDeprecated = value

    def numberType(self, value):
        self._component.numberType = value

    def src(self, value):
        self._component.src = value

    def minLevel(self, value):
        self._component.minLevel = value

    def battleTypes(self, value):
        self._component.battleTypes = value

    def glossaryName(self, value):
        self._component.glossaryName = value

    def validate(self):
        for validator in self.VALIDATORS.get(self._component.purpose, []):
            validator(self._component)


class StartingComponentsBuilder(XMLObjBuilder):
    TAG = 'startingComponents'
    PARAMS = {'components': (ParameterType.INT_LIST, Visibility.ALL)}
    VALIDATORS = [validateStartingComponent]

    def __init__(self, componentDefs=None):
        super(StartingComponentsBuilder, self).__init__(StartingComponents)
        self.__componentDefs = componentDefs
        self._compsID = []

    def components(self, value):
        self._compsID = value

    def validate(self):
        for validator in self.VALIDATORS:
            validator(self._component)

    def build(self):
        if len(self._compsID) != len(set(self._compsID)):
            raise ParseException(ParseException.STARTING_COMPONENT_DUPLICITY)
        for c in self._compsID:
            found = False
            for cd in self.__componentDefs:
                if cd.componentId == c:
                    found = True
                    self._component.components.append(cd)

            if not found:
                raise ParseException(ParseException.STARTING_COMPONENT_INVALID_ID, c)

        return super(StartingComponentsBuilder, self).build()


class ComponentDefinition(object):

    def __init__(self):
        self.componentId = 0
        self.resourceRoot = ''
        self.viewType = None
        self.purpose = None
        self.unlockKey = None
        self.progressKey = None
        self.isHidden = False
        self.isSecret = False
        self.isDefault = False
        self.isExternalUnlockOnly = False
        self.grades = None
        self.isDeprecated = False
        self.src = None
        self.numberType = ComponentNumberType.NUMBER
        self.minLevel = None
        self.battleTypes = None
        self.glossaryName = ''
        return

    def __str__(self):
        return "[id: {componentId}, {purpose}, {viewType}, unlock keys: {unlockKey}, progress keys: {progressKey}, hidden: {isHidden}, default: {isDefault}, deprecated: {isDeprecated}, grades: {grades}, secret: {isSecret}, only external unlock: {isExternalUnlockOnly}, src: '{src}']".format(componentId=self.componentId, purpose='None' if self.purpose is None else self.purpose.value, viewType='None' if self.viewType is None else self.viewType.value, unlockKey=self.unlockKey, progressKey=self.progressKey, isHidden=self.isHidden, isDefault=self.isDefault, isDeprecated=self.isDeprecated, grades=self.grades, isSecret=self.isSecret, isExternalUnlockOnly=self.isExternalUnlockOnly, src=self.src)

    def __repr__(self):
        return self.__str__()


class StartingComponents(object):

    def __init__(self):
        self.components = []

    def __str__(self):
        return self.components.__str__()

    def __repr__(self):
        return self.__str__()


def buildParserInfo():
    res = {}
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for name, cls in clsmembers:
        tag = getattr(cls, 'TAG', None)
        if tag:
            if tag in res:
                raise ParseException(ParseException.TAG_DUPLICITY, tag)
            paramNames = set(cls.PARAMS.iterkeys())
            paramsInfo = {}
            for paramName, paramType in cls.PARAMS.iteritems():
                if paramName in paramsInfo:
                    raise ParseException(ParseException.PARAM_DUPLICITY, paramName)
                paramsInfo[paramName] = paramType

            defaults = getattr(cls, 'DEFAULTS', {})
            res[tag] = (name,
             cls,
             paramNames,
             paramsInfo,
             defaults)

    return res


parserInfo = buildParserInfo()
