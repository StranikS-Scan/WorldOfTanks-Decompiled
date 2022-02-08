# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/managers_registrator.py
import sys
import CGF
from cgf_script.component_meta_class import CGFComponent
from soft_exception import SoftException

class Reactions(object):
    ON_PROCESS_QUERY = 0
    ON_ADDED_QUERY = 1
    ON_REMOVED_QUERY = 2
    ON_TICK = 3


def tickGroup(groupName):

    def warapper(func):
        return CGF.Reaction(Reactions.ON_TICK, func, groupName)

    return warapper


def onProcessQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_PROCESS_QUERY, func, kwargs.get('tickGroup', 'Simulation'), args)

    return wrapper


def onAddedQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_ADDED_QUERY, func, kwargs.get('tickGroup', 'Init'), args)

    return wrapper


def onRemovedQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_REMOVED_QUERY, func, kwargs.get('tickGroup', 'Init'), args)

    return wrapper


class ManagerRegistrator(object):
    __slots__ = ('__wrapper',)

    def __init__(self, wrapper):
        self.__wrapper = wrapper

    @property
    def wrapper(self):
        return self.__wrapper


class Rule(CGFComponent):

    def __init__(self):
        super(Rule, self).__init__()
        for value in self.__class__.__dict__.itervalues():
            if isinstance(value, ManagerRegistrator):
                value.wrapper(self)


def registerManager(manager, presentInEditor=False):

    def wrapper(func):
        CGF.registerManager(manager, False, presentInEditor)

        def wrapper_self(self):
            CGF.createManager(manager, func(self), self.spaceID)
            return None

        return ManagerRegistrator(wrapper_self)

    return wrapper


_rule_template = "import sys\nclass {typename}Rule(rule):\n    category = '{category}'\n    modulePath = sys.modules[managerType.__module__].__file__\n    def __init__(self):\n        super({typename}Rule, self).__init__()\n    @registrator(managerType)\n    def registerReactor(self):\n        return None\n"

def generateRule(cls, category):
    rule_class_definition = _rule_template.format(typename=cls.__name__, category=category)
    namespace = dict(rule=Rule, registrator=registerManager, managerType=cls)
    try:
        exec rule_class_definition in namespace
    except SyntaxError as e:
        raise SoftException(e.message + ':\n' + rule_class_definition)


def autoregister(presentInAllWorlds=False, category='', presentInEditor=False):

    def manager_registrator(cls):
        CGF.registerManager(cls, presentInAllWorlds, presentInEditor)
        modulePath = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
        CGF.registerModulePath(cls, modulePath)
        if presentInAllWorlds is False:
            generateRule(cls, category)
        return cls

    return manager_registrator
