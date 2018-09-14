# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationSummaryView.py
import BigWorld
from gui.Scaleform.daapi.view.meta.StaticFormationSummaryViewMeta import StaticFormationSummaryViewMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextType
from helpers import i18n, time_utils
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.ARENAS import ARENAS
import random

class StaticFormationSummaryView(StaticFormationSummaryViewMeta, AppRef):

    def __init__(self):
        super(StaticFormationSummaryView, self).__init__()

    def _populate(self):
        super(StaticFormationSummaryView, self)._populate()
        self.__setData()

    def _dispose(self):
        super(StaticFormationSummaryView, self)._dispose()

    def __setData(self):
        _getText = self.app.utilsManager.textManager.getText
        _ms = i18n.makeString
        place, league, division, ladderPts = self.__makeLadderData()
        league = _getText(TextType.STATUS_WARNING_TEXT, str(league))
        division = _getText(TextType.STATUS_WARNING_TEXT, division)
        ladderPts = _getText(TextType.STATUS_WARNING_TEXT, ladderPts)
        placeText = _getText(TextType.PROMO_SUB_TITLE, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_PLACE, place=place))
        leagueDivisionText = _getText(TextType.MIDDLE_TITLE, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_LEAGUEDIVISION, league=league, division=division))
        ladderPtsText = _getText(TextType.MAIN_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_LADDERPTS, points=ladderPts))
        bestTanksText = _getText(TextType.STATS_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_BESTTANKS))
        bestMapsText = _getText(TextType.STATS_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_BESTMAPS))
        notEnoughTanksText = notEnoughMapsText = _getText(TextType.STANDARD_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOTENOUGHTANKSMAPS))
        registeredDate = time_utils.getCurrentTimestamp() - random.randint(0, 20) * time_utils.ONE_DAY
        lastBattleDate = time_utils.getCurrentTimestamp() - random.randint(0, 20) * time_utils.ONE_DAY
        registeredDate = _getText(TextType.MAIN_TEXT, BigWorld.wg_getShortDateFormat(registeredDate))
        lastBattleDate = _getText(TextType.MAIN_TEXT, BigWorld.wg_getShortDateFormat(lastBattleDate))
        registeredText = _getText(TextType.STANDARD_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_REGISTERED, date=registeredDate))
        lastBattleText = _getText(TextType.STANDARD_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LASTBATTLE, date=lastBattleDate))
        ladderIconSource = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LADDER_256_1A
        noAwardsText = _getText(TextType.STATS_TEXT, _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOAWARDS))
        ribbonSource = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_RIBBON
        battlesNumData, winsPercentData, winsByCaptureData, techDefeatsData = self.__makeStats()
        bestTanks, bestMaps = self.__makeBestTanksMaps()
        bestTanksGroupWidth = 152
        bestMapsGroupWidth = 211
        notEnoughTanksTFVisible = False if len(bestTanks) else True
        notEnoughMapsTFVisible = False if len(bestMaps) else True
        result = {'placeText': placeText,
         'leagueDivisionText': leagueDivisionText,
         'ladderPtsText': ladderPtsText,
         'bestTanksText': bestTanksText,
         'bestMapsText': bestMapsText,
         'notEnoughTanksText': notEnoughTanksText,
         'notEnoughMapsText': notEnoughMapsText,
         'registeredText': registeredText,
         'lastBattleText': lastBattleText,
         'ladderIconSource': ladderIconSource,
         'noAwardsText': noAwardsText,
         'ribbonSource': ribbonSource,
         'battlesNumData': battlesNumData,
         'winsPercentData': winsPercentData,
         'winsByCaptureData': winsByCaptureData,
         'techDefeatsData': techDefeatsData,
         'bestTanks': bestTanks,
         'bestMaps': bestMaps,
         'achievements': self.__makeAchievements(),
         'bestTanksGroupWidth': bestTanksGroupWidth,
         'bestMapsGroupWidth': bestMapsGroupWidth,
         'notEnoughTanksTFVisible': notEnoughTanksTFVisible,
         'notEnoughMapsTFVisible': notEnoughMapsTFVisible}
        self.as_setDataS(result)

    def __makeLadderData(self):
        place = random.randint(1, 50)
        league = random.randint(1, 6)
        division = random.choice(['A',
         'B',
         'C',
         'D'])
        ladderPts = random.randint(1, 2000)
        return (place,
         league,
         division,
         ladderPts)

    def __makeStats(self):
        _ms = i18n.makeString
        battlesNumData = {'value': BigWorld.wg_getNiceNumberFormat(random.randint(0, 10000)),
         'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES),
         'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32,
         'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES}
        winsPercentData = {'value': BigWorld.wg_getNiceNumberFormat(random.uniform(0, 100)) + '%',
         'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT),
         'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32,
         'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT}
        winsByCaptureData = {'value': BigWorld.wg_getNiceNumberFormat(random.uniform(0, 100)) + '%',
         'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_WINSBYCAPTURE),
         'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINSBYCAPTURE40X32,
         'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSBYCAPTURE}
        techDefeatsData = {'value': BigWorld.wg_getNiceNumberFormat(random.randint(0, 2000)),
         'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_TECHDEFEATS),
         'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_TECHDEFEAT40X32,
         'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_TECHDEFEATS}
        return (battlesNumData,
         winsPercentData,
         winsByCaptureData,
         techDefeatsData)

    def __makeBestTanksMaps(self):
        _getText = self.app.utilsManager.textManager.getText
        _ms = i18n.makeString
        bestTanks = []
        bestMaps = []
        tanksLen = random.randint(0, 5)
        mapsLen = random.randint(0, 5)
        for i in xrange(tanksLen):
            label = str(i + 1) + '.'
            value = random.choice(['AMX 13 90',
             'AMX 50 100',
             'T1',
             'IS-3',
             'T-32'])
            iconSource = random.choice([RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_CHINA_CH09_M5,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_FRANCE_BAT_CHATILLON155_55,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_GERMANY_HUMMEL,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_JAPAN_NC27,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_UK_GB31_CONQUEROR_GUN,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_FRANCE_AMX_105AM,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_GERMANY_PZVI_TIGER_P,
             RES_ICONS.MAPS_ICONS_VEHICLE_CONTOUR_USA_T25_AT])
            bestTanks.append({'label': _getText(TextType.STANDARD_TEXT, label),
             'value': _getText(TextType.STATS_TEXT, value),
             'iconSource': iconSource})

        for i in xrange(mapsLen):
            label = str(i + 1) + '.'
            mapName = random.choice([ARENAS.C_43_NORTH_AMERICA_NAME,
             ARENAS.C_34_REDSHIRE_NAME,
             ARENAS.C_14_SIEGFRIED_LINE_NAME,
             ARENAS.C_08_RUINBERG_NAME,
             ARENAS.C_11_MUROVANKA_NAME,
             ARENAS.C_13_ERLENBERG_NAME,
             ARENAS.C_63_TUNDRA_NAME,
             ARENAS.C_02_MALINOVKA_NAME,
             ARENAS.C_05_PROHOROVKA_NAME,
             ARENAS.C_07_LAKEVILLE_NAME])
            mapName = _getText(TextType.MAIN_TEXT, _ms(mapName))
            value = random.randint(0, 100)
            bestMaps.append({'label': _getText(TextType.STANDARD_TEXT, label + ' ' + mapName),
             'value': _getText(TextType.STATS_TEXT, str(value) + '%')})

        return (bestTanks, bestMaps)

    def __makeAchievements(self):
        haveAchievements = random.choice([True, False])
        result = []
        if haveAchievements:
            result = [{'description': '\xd0\x97\xd0\xb0 \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x83\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81\xd0\xb0 \xc2\xab\xd0\x93\xd0\xb5\xd1\x80\xd0\xbe\xd0\xb9 \xd0\x91\xd0\xb8\xd1\x82\xd0\xb2\xd1\x8b\xc2\xbb.',
              'unic': True,
              'customData': [],
              'rank': 4,
              'inactive': False,
              'icon': '../maps/icons/achievement/medalKay4.png',
              'localizedValue': '4',
              'rare': False,
              'specialIcon': None,
              'rareIconId': None,
              'title': '\xd0\x9c\xd0\xb5\xd0\xb4\xd0\xb0\xd0\xbb\xd1\x8c \xd0\x9a\xd0\xb5\xd1\x8f  IV \xd1\x81\xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xd0\xbd\xd0\xb8',
              'isEpic': False,
              'type': 'medalKay',
              'block': 'achievements'}, {'description': '\xd0\x9f\xd0\xbe\xd0\xbb\xd1\x83\xd1\x87\xd0\xb8\xd1\x82\xd1\x8c \xd0\xbd\xd0\xb0\xd0\xb8\xd0\xb1\xd0\xbe\xd0\xbb\xd1\x8c\xd1\x88\xd0\xb5\xd0\xb5 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe \xd0\xb5\xd0\xb4\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x86 \xd0\xb7\xd0\xb0\xd0\xb1\xd0\xbb\xd0\xbe\xd0\xba\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xb1\xd1\x80\xd0\xbe\xd0\xbd\xd1\x91\xd0\xb9 \xd1\x83\xd1\x80\xd0\xbe\xd0\xbd\xd0\xb0.',
              'unic': True,
              'customData': [],
              'rank': 1,
              'inactive': False,
              'icon': '../maps/icons/achievement/steelwall.png',
              'localizedValue': '1',
              'rare': False,
              'specialIcon': None,
              'rareIconId': None,
              'title': '\xc2\xab\xd0\xa1\xd1\x82\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb0\xd1\x8f c\xd1\x82\xd0\xb5\xd0\xbd\xd0\xb0\xc2\xbb',
              'isEpic': False,
              'type': 'steelwall',
              'block': 'achievements'}, {'description': '\xd0\x9f\xd0\xbe\xd0\xbb\xd1\x83\xd1\x87\xd0\xb8\xd1\x82\xd1\x8c \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x80\xd1\x8f\xd0\xb4 \xd0\xbd\xd0\xb5 \xd0\xbc\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xb5 10 \xd1\x80\xd0\xb8\xd0\xba\xd0\xbe\xd1\x88\xd0\xb5\xd1\x82\xd0\xbe\xd0\xb2 \xd0\xb8 \xd0\xbd\xd0\xb5\xd0\xbf\xd1\x80\xd0\xbe\xd0\xb1\xd0\xb8\xd1\x82\xd0\xb8\xd0\xb9 \xd0\xbe\xd1\x82 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x82\xd0\xb8\xd0\xb2\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb0.',
              'unic': True,
              'customData': [],
              'rank': 1,
              'inactive': False,
              'icon': '../maps/icons/achievement/ironMan.png',
              'localizedValue': '1',
              'rare': False,
              'specialIcon': None,
              'rareIconId': None,
              'title': '\xc2\xab\xd0\x9d\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb7\xd0\xbc\xd1\x83\xd1\x82\xd0\xb8\xd0\xbc\xd1\x8b\xd0\xb9\xc2\xbb',
              'isEpic': False,
              'type': 'ironMan',
              'block': 'achievements'}]
        return result
