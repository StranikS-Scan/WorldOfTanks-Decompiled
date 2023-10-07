# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/quick_training_helpers.py
import typing
if typing.TYPE_CHECKING:
    from typing import Dict

class UiData(object):
    __slots__ = ('_freeXP', '_booksData', '_preSelectedBook', '_preSelectedFreeXp')

    def __init__(self):
        self._freeXP = 0
        self._booksData = {}
        self._preSelectedBook = 0
        self._preSelectedFreeXp = 0

    def addBook(self, bookCD):
        self._booksData[bookCD] = 0

    def updateBooks(self, bookCD, count):
        self._booksData.update({bookCD: count})

    def isBookSelected(self):
        return any((count for count in self._booksData.itervalues()))

    def isSomeSelected(self):
        return self.isBookSelected() or self.freeXp

    def clearPreSelected(self):
        self._preSelectedBook = 0
        self._preSelectedFreeXp = 0

    def clear(self):
        self._freeXP = 0
        for bookCD in self._booksData.iterkeys():
            self._booksData[bookCD] = 0

        self.clearPreSelected()

    def getBooksData(self):
        return self._booksData

    @property
    def freeXp(self):
        return self._freeXP

    @freeXp.setter
    def freeXp(self, value):
        self._freeXP = value

    @property
    def preSelectedBook(self):
        return self._preSelectedBook

    @preSelectedBook.setter
    def preSelectedBook(self, value):
        self._preSelectedFreeXp = 0
        self._preSelectedBook = value

    @property
    def preSelectedFreeXp(self):
        return self._preSelectedFreeXp

    @preSelectedFreeXp.setter
    def preSelectedFreeXp(self, value):
        self._preSelectedBook = 0
        self._preSelectedFreeXp = value

    def __repr__(self):
        return 'freeXP: {}, books: {}'.format(self._freeXP, self._booksData)
