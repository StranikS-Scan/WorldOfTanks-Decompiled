# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/queries.py
from math import ceil
from helpers import i18n, dependency, time_utils
from tutorial.control import ContentQuery
from tutorial.logger import LOG_ERROR
from gui.Scaleform.genConsts.BOOTCAMP_MESSAGE_ALIASES import BOOTCAMP_MESSAGE_ALIASES
from skeletons.gui.game_control import IBootcampController
from nations import NAMES as NATION_NAMES
import BigWorld
_PRESET_RENDERERS = {'FINISH': BOOTCAMP_MESSAGE_ALIASES.RENDERER_FIN_UI,
 'ORANGE': BOOTCAMP_MESSAGE_ALIASES.RENDERER_ORANGE_UI,
 'BLUE': BOOTCAMP_MESSAGE_ALIASES.RENDERER_BLUE,
 'GOLD': BOOTCAMP_MESSAGE_ALIASES.RENDERER_GOLD,
 'INTRO': BOOTCAMP_MESSAGE_ALIASES.RENDERER_INTRO}
_BOTTOM_RENDERERS = {'rewards': BOOTCAMP_MESSAGE_ALIASES.BOTTOM_REWARDS_VIEW_UI,
 'buttons': BOOTCAMP_MESSAGE_ALIASES.BOTTOM_BUTTONS_VIEW_UI}
_BOTTOM_DATA_FIELDS = ('label', 'icon', 'description', 'iconTooltip', 'labelTooltip')

class MessageDialogContentQuery(ContentQuery):
    bootcampController = dependency.descriptor(IBootcampController)

    def invoke(self, content, varID):
        content['messages'], content['voiceovers'] = map(list, zip(*(self.__makeMessageData(msgContent) for msgContent in content['sequence'])))

    def __makeMessageData(self, msgContent):
        nationsDataDict = msgContent.get('nations_data', None)
        if nationsDataDict is not None:
            nation = self.bootcampController.nation
            data = nationsDataDict[NATION_NAMES[nation]]
        else:
            data = msgContent['data']
        showBottomData = not data['only_first_bootcamp_bottom'] or self.bootcampController.needAwarding()
        msgData = {'messagePreset': _PRESET_RENDERERS[data['preset']],
         'label': i18n.makeString(data['label']),
         'iconPath': data['icon'],
         'message': i18n.makeString(data['text']) if showBottomData else '',
         'background': data['background']}
        voiceover = data['voiceover']
        if showBottomData:
            bottomRendererID = data['bottom_renderer']
            if bottomRendererID:
                bottomRenderer = _BOTTOM_RENDERERS.get(bottomRendererID)
                if bottomRenderer is not None:
                    msgData['bottomRenderer'] = bottomRenderer
                    msgData['bottomData'] = []
                    for bottom in data['bottom']:
                        processedBottom = dict(bottom)
                        self.__preprocessBottomData(processedBottom)
                        msgData['bottomData'].append(processedBottom)

                else:
                    LOG_ERROR('invalid bottom renderer ID', bottomRendererID)
        return (msgData, voiceover)

    def __preprocessBottomData(self, data):
        self.__formatLabel(data)
        data['label'] = i18n.makeString(data['label'])
        data['description'] = i18n.makeString(data['description'])
        keysToRemove = [ key for key in data if key not in _BOTTOM_DATA_FIELDS ]
        for key in keysToRemove:
            del data[key]

    def __formatLabel(self, data):
        labelFormat = data.get('label_format')
        if labelFormat is None:
            return
        else:
            ctx = self.bootcampController.getContext()
            if 'bonuses' not in ctx:
                return
            lessonBonuses = ctx['bonuses']['battle'][self.bootcampController.getLessonNum() - 1]
            if labelFormat == 'getCredits':
                nationId = ctx['nation']
                nationsData = lessonBonuses.get('nations', None)
                if nationsData is not None:
                    formattedValue = BigWorld.wg_getIntegralFormat(nationsData[NATION_NAMES[nationId]]['credits']['win'][0])
                    data['label'] = data['label'].format(formattedValue)
            elif labelFormat == 'getExperience':
                nationId = ctx['nation']
                nationsData = lessonBonuses.get('nations', None)
                if nationsData is not None:
                    formattedValue = BigWorld.wg_getIntegralFormat(nationsData[NATION_NAMES[nationId]]['xp']['win'][0])
                    data['label'] = data['label'].format(formattedValue)
            elif labelFormat == 'getGold':
                data['label'] = data['label'].format(lessonBonuses['gold'])
            elif labelFormat == 'getPremiumHours':
                hours = lessonBonuses['premium']
                timeInSeconds = hours * time_utils.ONE_HOUR
                if timeInSeconds > time_utils.ONE_DAY:
                    time = ceil(timeInSeconds / time_utils.ONE_DAY)
                    timeMetric = i18n.makeString('#menu:header/account/premium/days')
                else:
                    time = ceil(timeInSeconds / time_utils.ONE_HOUR)
                    timeMetric = i18n.makeString('#menu:header/account/premium/hours')
                data['label'] = data['label'].format(str(int(time)) + ' ' + timeMetric)
            elif labelFormat == 'getRepairKits':
                data['label'] = data['label'].format(lessonBonuses['equipment']['largeRepairkit']['count'])
            elif labelFormat == 'getFirstAid':
                data['label'] = data['label'].format(lessonBonuses['equipment']['largeMedkit']['count'])
            elif labelFormat == 'getFireExtinguisher':
                data['label'] = data['label'].format(lessonBonuses['equipment']['handExtinguishers']['count'])
            return
