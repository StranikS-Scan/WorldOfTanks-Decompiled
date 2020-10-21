# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/events/halloween.py
from helpers import dependency
from skeletons.gui.game_control import IEventTokenController
from web.web_client_api import w2c, Field, W2CSchema

class _HalloweenSchema(W2CSchema):
    note = Field(required=True, type=basestring)


class Halloween19WebApiMixin(object):
    __eventTokenController = dependency.descriptor(IEventTokenController)

    @w2c(W2CSchema, 'get_read_notes')
    def getReadNotesList(self, command):
        tokens = self.__eventTokenController.getReadNotes()
        return {'notes_list': tokens}

    @w2c(_HalloweenSchema, 'mark_as_read')
    def markNoteRead(self, command):
        self.__eventTokenController.markNoteRead(command.note)
