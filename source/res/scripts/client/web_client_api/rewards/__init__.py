# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/rewards/__init__.py
from helpers import i18n
from web_client_api import W2CSchema, Field, w2capi, w2c

class _RequestMedalsSchema(W2CSchema):
    medal_ids = Field(required=True, type=list, default=[])


@w2capi(name='rewards', key='action')
class RewardsWebApi(W2CSchema):

    @w2c(_RequestMedalsSchema, 'get_medals')
    def requestRewardInfo(self, cmd):
        return [ {'medal_id': rewardId,
         'image': ''.join(('gui/maps/icons/achievement/', rewardId, '.png')),
         'title': ''.join(('#achievements:', rewardId)),
         'name': i18n.makeString(''.join(('#achievements:', rewardId))),
         'description': i18n.makeString(''.join(('#achievements:', rewardId, '_descr'))),
         'condition': i18n.makeString(''.join(('#achievements:', rewardId, '_condition')))} for rewardId in cmd.medal_ids ]
