# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/rewards/__init__.py
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.shared.gui_items.dossier import getAchievementFactory
from helpers import i18n
from web_client_api import W2CSchema, Field, w2capi, w2c

class _RequestMedalsSchema(W2CSchema):
    medal_ids = Field(required=True, type=list, default=[])


@w2capi(name='rewards', key='action')
class RewardsWebApi(W2CSchema):

    @w2c(_RequestMedalsSchema, 'get_medals')
    def requestRewardInfo(self, cmd):
        responseData = []
        for recordId in cmd.medal_ids:
            record = DB_ID_TO_RECORD.get(int(recordId), ('', ''))
            _, rewardId = record
            factory = getAchievementFactory(record).create()
            responseData.append({'medal_id': recordId,
             'image': ''.join(('gui/maps/icons/achievement/', rewardId, '.png')),
             'title': ''.join(('#achievements:', rewardId)),
             'name': factory.getUserName(),
             'description': factory.getUserWebDescription(),
             'condition': factory.getUserCondition()})

        return responseData
