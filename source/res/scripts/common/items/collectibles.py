# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/collectibles.py
from constants import IS_CLIENT, IS_WEB
from debug_utils import LOG_CURRENT_EXCEPTION
from realm_utils import ResMgr
from wotdecorators import singleton
from items.readers.collectibles_readers import _readCollections
from items.components.ny_constants import YEARS
_CONFIG_FILE = 'scripts/item_defs/collectibles/collectibles.xml'

@singleton
class g_cache(object):

    def __init__(self):
        self.__cfg = {}

    def __getattr__(self, collectionName):
        try:
            return self.__cfg[collectionName]
        except KeyError:
            raise AttributeError

    def __getitem__(self, collectionName):
        try:
            return self.__cfg[collectionName]
        except KeyError:
            raise KeyError

    def init(self, nofail=True):
        try:
            try:
                section = ResMgr.openSection(_CONFIG_FILE)
                self.__cfg = cfg = {k:CollectionDescriptor(**v) for k, v in _readCollections(section['collections']).iteritems()}
            except Exception:
                self.ffini()
                if nofail:
                    raise
                LOG_CURRENT_EXCEPTION()

        finally:
            ResMgr.purge(_CONFIG_FILE)

    def ffini(self):
        self.__cfg.clear()

    def __iter__(self):
        return (citem for coll in self.__cfg.itervalues() for citem in coll.itervalues())

    def __nonzero__(self):
        return bool(self.__cfg)


class CollectionDescriptor(object):
    __slots__ = ('__cfg',)

    def __init__(self, **kwargs):
        cfg = self.__cfg = dict(kwargs)
        cfg['toys'] = {tid:ToyDescriptor(**d) for tid, d in kwargs.get('toys', {}).iteritems()}

    def __int__(self):
        pass

    def __getattr__(self, name):
        try:
            return self.__cfg[name]
        except KeyError:
            raise AttributeError

    def __iter__(self):
        return self.toys.itervalues()


@singleton
class EmptyCollection(CollectionDescriptor):
    __slots__ = ()

    def __init__(self):
        CollectionDescriptor.__init__(self, **{'toys': {}})


class ToyDescriptor(object):
    __slots__ = ('__cfg',)

    def __init__(self, **kwargs):
        self.__cfg = {k:v for k, v in kwargs.iteritems() if k in ('id', 'rank', 'type', 'setting', 'collection', 'dropSource') or IS_CLIENT or IS_WEB}

    def __getattr__(self, name):
        if name in self.__cfg:
            return self.__cfg[name]
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__, name))

    def __int__(self):
        pass

    def hasPrefab(self):
        return 'prefab' in self.__cfg


def init(verbose=False, nofail=True):
    if not g_cache:
        g_cache.init(nofail)
