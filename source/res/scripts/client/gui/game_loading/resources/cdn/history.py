# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/history.py
import os
import typing
from gui.game_loading import loggers
from gui.game_loading.common import loadDictFromJsonFile, saveDictToJsonFile, deleteFile
from gui.game_loading.resources.cdn.config import createSequenceModel, dumpSequenceModel
from web.cache.web_cache import generateKey
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.types import SequenceType, SlideType
    from gui.game_loading.resources.cdn.models import ConfigSequenceModel
_logger = loggers.getSequencesViewHistoryLogger()
_g_viewHistory = None

def getOrCreateViewHistory(dirPath):
    global _g_viewHistory
    if _g_viewHistory is None:
        historyFilePath = os.path.normpath(os.path.join(dirPath, generateKey('history.json')))
        _g_viewHistory = ViewHistory(historyFilePath)
        _g_viewHistory.load()
        _logger.debug('View history created from: %s.', historyFilePath)
    return _g_viewHistory


def saveViewHistory():
    if _g_viewHistory is not None:
        _g_viewHistory.save()
        _logger.debug('View history saved.')
    return


class ViewHistory(object):
    __slots__ = ('_filePath', '_history', '_changed', '_selectedSequence')

    def __init__(self, filePath):
        self._filePath = filePath
        self._history = {}
        self._selectedSequence = None
        self._changed = False
        return

    def load(self):
        history = loadDictFromJsonFile(self._filePath)
        if history is not None:
            self._history = history
            self._selectedSequence = None
            if self._rawSelectedSequence is not None:
                self._selectedSequence = createSequenceModel(self._rawSelectedSequence)
            self._changed = False
        return

    def save(self):
        if self._changed:
            saveDictToJsonFile(self._filePath, self._history)
            self._changed = False
        else:
            _logger.debug('History not changed. Saving skipped.')

    def delete(self):
        if deleteFile(self._filePath):
            self._history = {}
            self._selectedSequence = None
            self._changed = False
            _logger.debug('History deleted.')
        return

    @property
    def selectedSequence(self):
        return self._selectedSequence

    def selectSequence(self, sequence):
        rawSequence = dumpSequenceModel(sequence)
        if not rawSequence:
            _logger.warning('Can not select sequence: %s.', sequence.name)
            return
        if rawSequence == self._rawSelectedSequence:
            _logger.debug('Sequence: %s not changed.', sequence.name)
            return
        self._history['selected'] = rawSequence
        self._selectedSequence = sequence
        self._changed = True
        _logger.debug('Selected sequence: %s.', sequence.name)

    def deleteSelectedSequence(self):
        if self._selectedSequence is not None or self._rawSelectedSequence is not None:
            self._history.pop('selected', None)
            self._selectedSequence = None
            self._changed = True
            _logger.debug('Selected sequence deleted.')
        return

    def getSequenceViewsCount(self, sequence):
        return self._history.get('watched', {}).get(sequence.name, {}).get('views', 0)

    def getSequenceSlideViewsCount(self, sequence, slide):
        return self._history.get('watched', {}).get(sequence.name, {}).get('slides', {}).get(slide.historyKey, 0)

    def addSequenceSlideViewsCount(self, sequence, slide, count=1):
        sequenceStorage = self._history.setdefault('watched', {}).setdefault(sequence.name, {})
        slidesStorage = sequenceStorage.setdefault('slides', {})
        slidesStorage[slide.historyKey] = slidesStorage.get(slide.historyKey, 0) + count
        slidesViewsCount = sorted((self.getSequenceSlideViewsCount(sequence, slide) for slide in sequence.slides))
        sequenceStorage['views'] = slidesViewsCount[0] if slidesViewsCount else 0
        self._changed = True
        _logger.debug('Sequence %s slide %s view added.', sequence.name, slide)

    def removeSequenceFromHistory(self, sequence):
        if self._selectedSequence and self._selectedSequence.name == sequence.name:
            self.deleteSelectedSequence()
        self._history.get('watched', {}).pop(sequence.name, None)
        self._changed = True
        return

    @property
    def _rawSelectedSequence(self):
        return self._history.get('selected')

    def __repr__(self):
        return '<SequencesViewHistory(path={}, sequence={}, changed={})>'.format(self._filePath, self._selectedSequence, self._changed)
