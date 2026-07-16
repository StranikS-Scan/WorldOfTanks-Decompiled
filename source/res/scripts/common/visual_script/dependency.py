# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/dependency.py
from __future__ import absolute_import
import sys
import typing
from importlib import import_module
from constants import IS_VS_EDITOR
from py2to3.patched_future import with_metaclass
if typing.TYPE_CHECKING:
    from types import ModuleType
if IS_VS_EDITOR:

    class MockObjectMeta(type):

        def __getitem__(cls, item):
            return MockObject

        def __getattr__(cls, item):
            return MockObject

        def __iter__(cls):
            while False:
                yield

            return


    class MockObject(with_metaclass(MockObjectMeta, object)):

        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return MockObject()

        def __getitem__(self, item):
            return MockObject()

        def __getattr__(self, item):
            return MockObject()

        def __iter__(self):
            while False:
                yield

            return

        def __str__(self):
            pass


    MOCK_IMPORT_ERRORS = []

    def tryImportGen(modules):
        for module in modules:
            try:
                yield import_module(module)
            except Exception as er:
                MOCK_IMPORT_ERRORS.append('On import module <%s> was raised ImportError with msg - %s' % (module, str(er)))
                yield MockObject


def dependencyImporter(*modules):
    if IS_VS_EDITOR:
        return list(tryImportGen(modules))
    return [ import_module(module) for module in modules ]


def dependencyMocker(*modules):
    if IS_VS_EDITOR:
        for module in modules:
            if isinstance(module, tuple):
                path, mock = module
            else:
                path, mock = module, MockObject()
            sys.modules[path] = mock


__all__ = ('dependencyImporter', 'dependencyMocker')
