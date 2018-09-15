# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_cm_handlers.py
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.NY import NY
from helpers import dependency
from skeletons.new_year import INewYearController
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, HtmlMessageDialogMeta, DIALOG_BUTTON_ID
from items.new_year_types import g_cache
INVALID_TOY_ID = -1

class TOY(object):
    PLACE = 'toyPlace'
    REMOVE = 'toyRemove'
    BREAK = 'toyBreak'


class AbstractNyToyContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):
    newYearController = dependency.descriptor(INewYearController)

    def __init__(self, cmProxy, ctx=None, handlers=None):
        if not handlers:
            handlers = {}
        handlers[TOY.BREAK] = 'breakToy'
        super(AbstractNyToyContextMenuHandler, self).__init__(cmProxy, ctx, handlers)

    def breakToy(self):
        self.__breakToy()

    @process
    def __breakToy(self):
        toy = g_cache.toys.get(self._toyId, None)
        if not toy:
            return
        else:
            if toy.rank == 5:
                ctx = {}
                is_ok = yield DialogsInterface.showDialog(meta=I18nConfirmDialogMeta('confirmHighLevelToyBreak', ctx, ctx, meta=HtmlMessageDialogMeta('html_templates:newYear/dialogs', 'confirmHighLevelToyBreak', ctx, sourceKey='text'), focusedID=DIALOG_BUTTON_ID.SUBMIT))
                if is_ok:
                    self._doBreakToy()
            else:
                self._doBreakToy()
            return

    def _doBreakToy(self):
        self.newYearController.breakToys(((self._toyId, 1),), [self._index])

    def _generateOptions(self, ctx=None):
        options = list()
        options.append(self._makeItem(TOY.BREAK, NY.CONTEXTMENU_BREAKTOY))
        return options

    def _initFlashValues(self, ctx):
        self._toyId = int(ctx.id) if ctx.id else 0
        self._index = int(ctx.index)
        self._slotID = int(ctx.slotID)


class NyCurrentToyContextMenuHandler(AbstractNyToyContextMenuHandler):

    def __init__(self, cmProxy, ctx=None):
        super(NyCurrentToyContextMenuHandler, self).__init__(cmProxy, ctx, {TOY.REMOVE: 'removeToy'})

    def removeToy(self):
        self.newYearController.placeToy(INVALID_TOY_ID, self._slotID)

    def _doBreakToy(self):
        self.removeToy()
        self.newYearController.breakToys(((self._toyId, 1),), [self._index])

    def _generateOptions(self, ctx=None):
        options = super(NyCurrentToyContextMenuHandler, self)._generateOptions()
        options.insert(0, self._makeItem(TOY.REMOVE, NY.CONTEXTMENU_REMOVETOY))
        return options


class NyToyContextMenuHandler(AbstractNyToyContextMenuHandler):

    def __init__(self, cmProxy, ctx=None):
        super(NyToyContextMenuHandler, self).__init__(cmProxy, ctx, {TOY.PLACE: 'placeToy'})

    def placeToy(self):
        self.newYearController.placeToy(int(self._toyId), self._slotID)

    def _generateOptions(self, ctx=None):
        options = super(NyToyContextMenuHandler, self)._generateOptions()
        options.insert(0, self._makeItem(TOY.PLACE, NY.CONTEXTMENU_PLACETOY))
        return options


class NyToySlotContextMenuHandler(NyCurrentToyContextMenuHandler, EventSystemEntity):

    def _doBreakToy(self):
        self.removeToy()
        self.newYearController.breakToys(((self._toyId, 1),), [self._index], True)
