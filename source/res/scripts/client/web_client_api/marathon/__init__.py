# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/marathon/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController
from web_client_api import w2c, w2capi, Field, W2CSchema

class _MarathonProgressSchema(W2CSchema):
    prefix = Field(required=True, type=basestring)


@w2capi(name='user_data', key='action')
class MarathonWebApi(W2CSchema):
    marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    @w2c(_MarathonProgressSchema, 'get_step')
    def handleGetStep(self, command):
        marathon = self.marathonsCtrl.getMarathon(command.prefix)
        currentStep, allSteps = marathon.getMarathonProgress()
        return {'current_step': currentStep,
         'all_steps': allSteps}
