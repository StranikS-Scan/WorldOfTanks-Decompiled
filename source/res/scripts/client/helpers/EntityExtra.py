# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EntityExtra.py
from debug_utils import LOG_CURRENT_EXCEPTION

class EntityExtra(object):
    __slots__ = ('name', 'index')

    def __init__(self, name, index, containerName, dataSection):
        self.name = name
        self.index = index
        self._readConfig(dataSection, containerName)

    def prerequisites(self):
        pass

    def startFor(self, entity, args=None):
        if entity.extras.has_key(self.index):
            raise Exception("the extra '%s' is already started" % self.name)
        d = self._newData(entity)
        entity.extras[self.index] = d
        try:
            self._start(d, args)
        except Exception:
            if d['entity'] is not None:
                del entity.extras[self.index]
                try:
                    self._cleanup(d)
                except Exception:
                    LOG_CURRENT_EXCEPTION()

                d['entity'] = None
            raise

        return

    def stopFor(self, entity):
        data = entity.extras.pop(self.index, None)
        if data is None:
            return False
        else:
            try:
                self._cleanup(data)
            except Exception:
                LOG_CURRENT_EXCEPTION()

            data['entity'] = None
            return True

    def stop(self, data):
        if data['entity'] is None:
            return
        else:
            try:
                del data['entity'].extras[self.index]
                self._cleanup(data)
            except Exception:
                LOG_CURRENT_EXCEPTION()

            data['entity'] = None
            return

    def updateFor(self, entity, args):
        data = entity.extras.get(self.index)
        if data is None:
            return False
        else:
            self._update(data, args)
            return True

    def isRunningFor(self, entity):
        return self.index in entity.extras

    def _readConfig(self, dataSection, containerName):
        pass

    def _start(self, data, args):
        self.stop(data)

    def _update(self, data, args):
        pass

    def _cleanup(self, data):
        pass

    def _raiseWrongConfig(self, paramName, containerName):
        raise Exception("missing or wrong parameter <%s> (entity extra '%s' in '%s')" % (paramName, self.name, containerName))

    def _newData(self, entity):
        return {'extra': self,
         'entity': entity}
