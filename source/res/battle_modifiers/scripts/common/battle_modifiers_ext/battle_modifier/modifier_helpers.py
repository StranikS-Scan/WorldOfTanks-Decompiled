# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_helpers.py
from typing import Any, Optional, Callable, Union, Tuple, Dict
from ResMgr import DataSection
from battle_modifiers_ext.constants_ext import UseType
from soft_exception import SoftException

def makeUseTypeMethods(method, copy=False):
    if isinstance(method, dict):
        if copy:
            return method.copy()
        return method
    return dict(((useType, method) for useType in UseType.ALL_WITH_UNDEFINED))


def createLevelTag(level):
    return 'level_' + str(level)


def parseLevelTag(levelTag):
    parts = levelTag.split('_', 1)
    if not (len(parts) == 2 and parts[0] == 'level'):
        return
    else:
        try:
            level = int(parts[1])
        except ValueError:
            level = None

        return level


class Serializable(object):

    def __init__(self, source, *args):
        if isinstance(source, DataSection):
            self._initFromConfig(source, *args)
        elif source is not None:
            self._initFromDescr(source)
        super(Serializable, self).__init__()
        return

    def descr(self):
        raise SoftException('{} can not be serialized'.format(self.__class__.__name__))

    def _initFromDescr(self, descr):
        raise SoftException('{} can not be constructed by descriptor'.format(self.__class__.__name__))

    def _initFromConfig(self, source, *args):
        raise SoftException('{} can not be constructed by data section'.format(self.__class__.__name__))
