# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/config/dog_tag_parser.py
import typing
import ResMgr
import dog_tag_framework as dtf
from constants import IS_CLIENT, IS_BASEAPP
from dog_tags_common.config.common import ParseException, ParameterType, Visibility, ComponentPurpose, ComponentViewType, DOG_TAGS_FILE, ComponentNumberType
if typing.TYPE_CHECKING:
    from typing import List, Tuple
    from dog_tags_common.config.dog_tag_framework import StartingComponents, ComponentDefinition

def _parseInt(attrValue, path):
    try:
        return int(attrValue)
    except Exception:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseBool(attrValue, path):
    if attrValue.lower() in ('true', 'yes', '1'):
        return True
    if attrValue.lower() in ('false', 'no', '0'):
        return False
    raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseStr(attrValue, path):
    return '%s' % str(attrValue)


def _parseIntList(attrValue, path):
    try:
        return [ int(i) for i in str(attrValue).split() ]
    except Exception:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseFloatList(attrValue, path):
    try:
        return [ float(i) for i in str(attrValue).split() ]
    except Exception:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseStrList(attrValue, path):
    try:
        return str(attrValue).split()
    except Exception:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseViewType(attrValue, path):
    try:
        return ComponentViewType(attrValue)
    except ValueError:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseType(attrValue, path):
    try:
        return ComponentPurpose(attrValue)
    except ValueError:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


def _parseNumberType(attrValue, path):
    try:
        return ComponentNumberType(attrValue)
    except ValueError:
        raise ParseException(ParseException.WRONG_PARAM_VALUE, path)


PARAM_PARSERS = {ParameterType.INT: _parseInt,
 ParameterType.STR: _parseStr,
 ParameterType.BOOL: _parseBool,
 ParameterType.INT_LIST: _parseIntList,
 ParameterType.STR_LIST: _parseStrList,
 ParameterType.VIEW_TYPE: _parseViewType,
 ParameterType.TYPE: _parseType,
 ParameterType.NUMBER_TYPE: _parseNumberType,
 ParameterType.FLOAT_LIST: _parseFloatList}

def _parseSection(sectionName, section, *builderAttrs):
    operationName, cls, operationParamNames, operationParamsInfo, operationDefaults = dtf.parserInfo[sectionName]
    childrens = section.keys()
    operationParams = {}
    for chilName in childrens:
        visibility = operationParamsInfo[chilName][1]
        if visibility == Visibility.ALL or IS_CLIENT and visibility == Visibility.CLIENT or IS_BASEAPP and visibility == Visibility.SERVER:
            paramType = operationParamsInfo[chilName][0]
            operationParams[chilName] = PARAM_PARSERS[paramType](section.readString(chilName), chilName)

    for key, value in operationDefaults.iteritems():
        if key not in operationParams:
            operationParams[key] = value

    missedParams = operationParamNames - set(operationParams.iterkeys())
    for miss in missedParams:
        operationParams[miss] = None

    builder = cls(*builderAttrs)
    for key, value in operationParams.iteritems():
        getattr(builder, key)(value)

    return builder.build()


def readDogTags(xmlPath=DOG_TAGS_FILE):
    xmlFile = ResMgr.openSection(xmlPath)
    components = []
    for sectionName, section in xmlFile.items():
        if sectionName == 'component':
            components.append(_parseSection(sectionName, section))

    startingComponent = _parseSection('startingComponents', xmlFile['startingComponents'], components)
    return (startingComponent, components)
