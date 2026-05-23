# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/server_settings.py
from __future__ import absolute_import
import logging
from collections import namedtuple
from future.utils import viewitems
from shared_utils import makeTupleByDict
_logger = logging.getLogger(__name__)

class BundlesConfig(object):
    __slots__ = ('__bundles',)

    def __init__(self, config):
        self.__bundles = {bundleID:BundleConfig(**bundle) for bundleID, bundle in viewitems(config)}

    def getBundleIDs(self):
        return self.__bundles.keys()

    def getBundles(self):
        return self.__bundles.values()

    def getBundle(self, bundleID):
        if bundleID in self.__bundles:
            return self.__bundles[bundleID]
        _logger.error('Trying to get non-existing bundle by ID: %s', bundleID)
        return BundleConfig.defaults()


class BundleConfig(namedtuple('_BundleConfig', ('enabled', 'id', 'type', 'start', 'finish', 'steps', 'cells', 'bonus'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, id=0, type='', start=0, finish=0, steps={}, cells={}, bonus={})
        defaults.update(kwargs)
        cls.__packStepConfigs(defaults)
        cls.__packCellConfigs(defaults)
        return super(BundleConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(**dict(enabled=False, id=0, type='', start=0, finish=0, steps={}, cells={}, bonus={}))

    @classmethod
    def __packStepConfigs(cls, data):
        data['steps'] = {stepNumber:makeTupleByDict(StepConfig, step) for stepNumber, step in viewitems(data['steps'])}

    @classmethod
    def __packCellConfigs(cls, data):
        data['cells'] = {cellName:makeTupleByDict(CellConfig, cell) for cellName, cell in viewitems(data['cells'])}


class StepConfig(namedtuple('_StepConfig', ('number', 'price', 'fixedBonus'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(number=False, price={}, fixedBonus={})
        defaults.update(kwargs)
        return super(StepConfig, cls).__new__(cls, **defaults)


class CellConfig(namedtuple('_CellConfig', ('name', 'template', 'coordinates', 'tags'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(name='', template='', coordinates={}, tags=[])
        defaults.update(kwargs)
        cls.__packCoordinatesConfig(defaults)
        return super(CellConfig, cls).__new__(cls, **defaults)

    @classmethod
    def __packCoordinatesConfig(cls, data):
        data['coordinates'] = makeTupleByDict(CoordinatesConfig, data['coordinates'])


class CoordinatesConfig(namedtuple('_CoordinatesConfig', ('start', 'end'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(start=(0, 0), end=(0, 0))
        defaults.update(kwargs)
        return super(CoordinatesConfig, cls).__new__(cls, **defaults)
