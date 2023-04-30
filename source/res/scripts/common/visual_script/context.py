# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/context.py
from inspect import getargspec, ismethod, getmembers, getmro
from functools import wraps
from types import FunctionType
from typing import Tuple, Callable, List, Sequence
from soft_exception import SoftException
from misc import ASPECT
from constants import IS_DEVELOPMENT
if IS_DEVELOPMENT:
    from debug_plan_loader import debugPlanLoader

class UnsupportedMemberException(SoftException):

    def __init__(self, func_name, aspect):
        self.func_name = func_name
        self.aspect = aspect
        super(UnsupportedMemberException, self).__init__(self.__str__())

    def __str__(self):
        return 'UnsupportedMember: %s not available for aspect = %s' % (self.func_name, self.aspect)


class MetaData(object):
    FUNC_CALL = 0
    EVENT_OUT = 1
    PROPERTY_GET = 2
    PROPERTY_SET = 3
    PROPERTY_PARAM_GET = 4
    UNDEFINED_SLOT_TYPE = 'Undefined'

    def __init__(self, field, name, args, **kwargs):
        self.field = field
        self.name = name
        self.args = args
        self.abstract = kwargs.get('abstract', False)
        self.display_name = kwargs.get('display_name', name)
        self.display_group = kwargs.get('display_group', 'default')
        self.description = kwargs.get('description', '')
        self.aspects = kwargs.get('aspects', ASPECT.ALL)

    def __repr__(self):
        return 'MetaData(field=%s, name=%s, args=%s, abstract=%s, display_name=%s, display_group=%s, description=%s, aspects=%s)' % (self.field,
         self.name,
         self.args,
         self.abstract,
         self.display_name,
         self.display_group,
         self.description,
         self.aspects)

    @staticmethod
    def make_res_record(res_type):
        return ('', MetaData.UNDEFINED_SLOT_TYPE) if res_type is None else ('', res_type)


def vse_get_property(*args, **kwargs):

    def wrapper(f):
        meta = MetaData(MetaData.PROPERTY_GET, f.__name__, args[0], **kwargs)

        @wraps(f)
        def w(self, *args_, **kwargs_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            return f(self, *args_, **kwargs_)

        w.vse_meta = meta
        return w

    return wrapper


def vse_get_param_property(res, args, **kwargs):

    def wrapper(f):
        signature = [MetaData.make_res_record(res)] + zip(getargspec(f).args[1:], args)
        meta = MetaData(MetaData.PROPERTY_PARAM_GET, f.__name__, signature, **kwargs)

        @wraps(f)
        def w(self, *args_, **kwargs_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            return f(self, *args_, **kwargs_)

        w.vse_meta = meta
        return w

    return wrapper


def vse_set_property(*args, **kwargs):

    def wrapper(f):
        meta = MetaData(MetaData.PROPERTY_SET, f.__name__, args[0], **kwargs)

        @wraps(f)
        def w(self, *args_, **kwargs_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            return f(self, *args_, **kwargs_)

        w.vse_meta = meta
        return w

    return wrapper


def vse_func_call(res, args, **kwargs):

    def wrapper(f):
        signature = [MetaData.make_res_record(res)] + zip(getargspec(f).args[1:], args)
        meta = MetaData(MetaData.FUNC_CALL, f.__name__, signature, **kwargs)

        @wraps(f)
        def w(self, *args_, **kwargs_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            return f(self, *args_, **kwargs_)

        w.vse_meta = meta
        return w

    return wrapper


def vse_event_out(*args, **kwargs):

    def wrapper(f):
        meta = MetaData(MetaData.EVENT_OUT, f.__name__, zip(getargspec(f).args[1:], args), **kwargs)

        @wraps(f)
        def w(self, *args_, **kwargs_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            getattr(self._vse_dispatchers, meta.name).call(args_)
            return f(self, *args_, **kwargs_)

        w.vse_meta = meta
        return w

    return wrapper


def vse_forward_event(name, argsSpecs, **kwargs):
    meta = MetaData(MetaData.EVENT_OUT, name, argsSpecs, **kwargs)

    def dummyMethod(self, *args_):
        if self._vse_aspect not in meta.aspects:
            raise UnsupportedMemberException(meta.name, self._vse_aspect)
        getattr(self._vse_dispatchers, meta.name).call(args_)

    dummyMethod.__name__ = name
    dummyMethod.__doc__ = name
    dummyMethod.vse_meta = meta
    return dummyMethod


def vse_context_effect_forward_event(name, argsSpecs, **kwargs):

    def wrapper(effect):
        meta = MetaData(MetaData.EVENT_OUT, name, argsSpecs, **kwargs)

        def dummyMethod(self, *args_):
            if self._vse_aspect not in meta.aspects:
                raise UnsupportedMemberException(meta.name, self._vse_aspect)
            getattr(self._vse_dispatchers, meta.name).call(args_)

        def callWithEffect(self, *args):
            effect(self, *args)
            dummyMethod(self, *args)

        callWithEffect.__name__ = name
        callWithEffect.__doc__ = name
        callWithEffect.vse_meta = meta
        return callWithEffect

    return wrapper


class DispatchersHolder(object):
    pass


class VScriptContext(object):

    def __init__(self, aspect):
        self.__active_vse_aspect = aspect
        cls = self.__class__
        self._vse_dispatchers = DispatchersHolder()
        if IS_DEVELOPMENT:
            debugPlanLoader.regContext(self)
        import VSE
        for name, member in getmembers(cls):
            if ismethod(member) and hasattr(member, 'vse_meta') and aspect in member.vse_meta.aspects:
                if member.vse_meta.field is MetaData.EVENT_OUT:
                    args = (type_ for _, type_ in member.vse_meta.args)
                    setattr(self._vse_dispatchers, member.vse_meta.name, VSE.Dispatcher(tuple(args)))
                elif member.vse_meta.abstract:
                    raise RuntimeError('%s: required to override "%s" for aspect = %s' % (cls.__name__, name, aspect))

    def __del__(self):
        if IS_DEVELOPMENT:
            debugPlanLoader.unregContext(self)

    def destroy(self):
        if IS_DEVELOPMENT:
            debugPlanLoader.unregContext(self)

    def triggerEvent(self, name, *args):
        method = getattr(self, name, None)
        method(*args)
        return

    @property
    def _vse_aspect(self):
        return self.__active_vse_aspect

    @classmethod
    def _is_sub_class_of(cls, cls_name):
        return any((c.__name__ == cls_name for c in getmro(cls)))
