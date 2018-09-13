# Embedded file name: scripts/client/helpers/EntityExtra.py
import BigWorld
from debug_utils import *

class EntityExtra(object):

    def __init__(self, name, index, containerName, dataSection):
        self.name = name
        self.index = index
        self._readConfig(dataSection, containerName)

    def prerequisites(self):
        return ()

    def stop(self, data):
        if not data['extra'] is self:
            raise AssertionError
            return data['entity'] is None and None
        else:
            try:
                del data['entity'].extras[self.index]
                self._cleanup(data)
            except Exception:
                LOG_CURRENT_EXCEPTION()

            data['entity'] = None
            return

    def startFor(self, entity, args = None):
        if entity.extras.has_key(self.index):
            raise Exception, "the extra '%s' is already started" % self.name
        d = _newData(self, entity)
        entity.extras[self.index] = d
        try:
            self._start(d, args)
        except:
            if d['entity'] is not None:
                del entity.extras[self.index]
                try:
                    self._cleanup(d)
                except Exception:
                    LOG_CURRENT_EXCEPTION()

                d['entity'] = None
            raise

        return d

    def useNewArgs(self, data, args):
        return False

    def _readConfig(self, dataSection, containerName):
        pass

    def _start(self, data, args):
        self.stop(data)

    def _cleanup(self, data):
        pass

    def _raiseWrongConfig(self, paramName, containerName):
        raise Exception, "missing or wrong parameter <%s> (entity extra '%s' in '%s')" % (paramName, self.name, containerName)


def _newData(extra, entity):
    return {'extra': extra,
     'entity': entity}
