# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/dialogs.py
import adisp
import async
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import showPreformattedDialog
from shared_utils import first
from web.web_client_api import WebCommandException, w2c, W2CSchema, Field

def _dialogButtonsValidator(buttonsList, _=None):
    for button in buttonsList:
        if first(button.keys()) not in DialogButtons.ALL:
            raise WebCommandException('unsupported button label "{}"'.format(first(button.keys())))

    return True


class _DialogSchema(W2CSchema):
    preset = Field(required=True, type=basestring)
    title = Field(required=False, type=basestring, default='')
    message = Field(required=False, type=basestring, default='')
    buttons = Field(required=True, type=list, validator=_dialogButtonsValidator)
    focusedButton = Field(required=False, type=basestring, default=None)
    btnDownSounds = Field(required=False, type=dict, default=None)


class DialogsWebApiMixin(object):

    @w2c(_DialogSchema, 'confirm_dialog_overlay')
    def showDialog(self, cmd):

        @adisp.async
        @async.async
        def proxy(callback):
            res = yield async.await(showPreformattedDialog(cmd.preset, cmd.title, cmd.message, cmd.buttons, cmd.focusedButton, cmd.btnDownSounds))
            callback(res)

        result = yield proxy()
        yield {'buttonID': result}
