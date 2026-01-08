# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/WindowsStoredDataLoader.py
from __future__ import absolute_import
import base64
from future.moves import pickle
from future.utils import lmap
import Settings
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

class WindowsStoredDataLoader(object):

    def __init__(self, rev, maxRecordLen, defMask):
        super(WindowsStoredDataLoader, self).__init__()
        self.__rev = rev
        self.__maxRecordLen = maxRecordLen
        self.__defMask = defMask

    def load(self):
        if Settings.g_instance is None:
            LOG_ERROR('Settings is not defined, can not load data')
            return (self.__defMask, [])
        else:
            section = Settings.g_instance.userPrefs[Settings.KEY_WINDOWS_STORED_DATA]
            if section is None:
                return (self.__defMask, [])
            mask = section.readInt('mask', self.__defMask)
            rev = section.readInt('rev', self.__rev)
            records = []
            if rev == self.__rev:
                dataSec = section['records']

                def decode(value):
                    try:
                        return pickle.loads(base64.b64decode(value))
                    except TypeError:
                        LOG_CURRENT_EXCEPTION()
                        return None

                    return None

                if dataSec is not None:
                    for _, subSec in dataSec.items():
                        record = decode(subSec.asString)
                        if record:
                            records.append(record)

            return (mask, records)

    def flush(self, mask, records):
        if Settings.g_instance is None:
            LOG_ERROR('Settings is not defined, can not flush data')
            return
        else:
            userPrefs = Settings.g_instance.userPrefs
            section = userPrefs[Settings.KEY_WINDOWS_STORED_DATA]
            if section is None:
                section = userPrefs.createSection(Settings.KEY_WINDOWS_STORED_DATA)
            section.writeInt('mask', mask)
            section.writeInt('rev', self.__rev)
            section.deleteSection('records')
            if records:
                dataSec = section.createSection('records')
                records = records[:self.__maxRecordLen]

                def encode(value):
                    return base64.b64encode(pickle.dumps(value))

                dataSec.writeStrings('record', lmap(encode, records))
            Settings.g_instance.save()
            return
