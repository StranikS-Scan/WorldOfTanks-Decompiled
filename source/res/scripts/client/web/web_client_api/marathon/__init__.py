# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/marathon/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController
from web.web_client_api import w2c, w2capi, W2CSchema, Field

class _OpenVideoContentSchema(W2CSchema):
    prefix = Field(required=True, type=basestring)
    url = Field(required=False, type=basestring)


@w2capi(name='marathon', key='action')
class MarathonWebApi(W2CSchema):
    __marathonCtrl = dependency.descriptor(IMarathonEventsController)

    @w2c(_OpenVideoContentSchema, name='show_video')
    def handleOpenVideoContent(self, cmd):
        self.__marathonCtrl.handleOpenVideoContent(cmd.prefix, cmd.url)
