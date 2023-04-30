# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/managers_registrator.py
import sys
import CGF
from cgf_script.component_meta_class import registerComponent
from soft_exception import SoftException

class Reactions(object):
    ON_PROCESS_QUERY = 0
    ON_ADDED_QUERY = 1
    ON_REMOVED_QUERY = 2
    ON_TICK = 3


def tickGroup(groupName, updatePeriod=0.0):

    def warapper(func):
        return CGF.Reaction(Reactions.ON_TICK, func, groupName, updatePeriod)

    return warapper


def onProcessQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_PROCESS_QUERY, func, kwargs.get('tickGroup', 'Simulation'), kwargs.get('period', 0.0), args)

    return wrapper


def onAddedQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_ADDED_QUERY, func, kwargs.get('tickGroup', 'Init'), 0.0, args)

    return wrapper


def onRemovedQuery(*args, **kwargs):

    def wrapper(func):
        return CGF.Reaction(Reactions.ON_REMOVED_QUERY, func, kwargs.get('tickGroup', 'Init'), 0.0, args)

    return wrapper


class ManagerRegistrator(object):
    __slots__ = ('__wrapper',)

    def __init__(self, wrapper):
        self.__wrapper = wrapper

    @property
    def wrapper(self):
        return self.__wrapper


class Rule(object):

    def __init__(self):
        for value in self.__class__.__dict__.itervalues():
            if isinstance(value, ManagerRegistrator):
                value.wrapper(self)


registerRule = registerComponent

def registerManager(manager, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor):

    def wrapper(func):
        CGF.registerManager(manager, False, domain)

        def wrapper_self(self):
            CGF.createManager(manager, func(self), self.spaceID)
            return None

        return ManagerRegistrator(wrapper_self)

    return wrapper


_rule_template = "import sys\n@decorator\nclass {typename}Rule(rule):\n    vseVisible = False\n    category = '{category}'\n    modulePath = sys.modules[managerType.__module__].__file__\n    def __init__(self):\n        super({typename}Rule, self).__init__()\n    @registrator(managerType)\n    def registerReactor(self):\n        return None\n"

def generateRule(cls, category):
    rule_class_definition = _rule_template.format(typename=cls.__name__, category=category)
    namespace = dict(rule=Rule, registrator=registerManager, managerType=cls, decorator=registerRule)
    try:
        exec rule_class_definition in namespace
    except SyntaxError as e:
        raise SoftException(e.message + ':\n' + rule_class_definition)


def autoregister(presentInAllWorlds=False, category='', domain=CGF.DomainOption.DomainClient, creationPredicate=None):

    def manager_registrator(cls):
        CGF.registerManager(cls, presentInAllWorlds, domain, creationPredicate)
        modulePath = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
        CGF.registerModulePath(cls, modulePath)
        if presentInAllWorlds is False:
            generateRule(cls, category)
        return cls

    return manager_registrator
