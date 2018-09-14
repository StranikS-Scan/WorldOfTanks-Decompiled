# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationLadderView.py
from gui.Scaleform.daapi.view.meta.StaticFormationLadderViewMeta import StaticFormationLadderViewMeta
from gui.Scaleform.framework import AppRef
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.framework.managers.TextManager import TextType
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
import random

class StaticFormationLadderView(StaticFormationLadderViewMeta, AppRef):
    __clanEmblem = None

    def __init__(self):
        super(StaticFormationLadderView, self).__init__()

    def _populate(self):
        super(StaticFormationLadderView, self)._populate()
        self.as_updateHeaderDataS(self.__packHeaderData())
        self.as_updateLadderDataS(self.__packLadderData())

    def _dispose(self):
        super(StaticFormationLadderView, self)._dispose()

    def showFormationProfile(self, fromationId):
        LOG_DEBUG('StaticFormationLadderView.showFormationProfile fromationId: ' + str(fromationId))

    def __packHeaderData(self):
        _getText = self.app.utilsManager.textManager.getText
        return {'divisionName': _getText(TextType.HIGH_TITLE, _ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_DIVISIONNAME_TEXT, division='D', league='12')),
         'divisionPositionText': _getText(TextType.STANDARD_TEXT, _ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_DIVISIONPOSITION_TEXT, place='133', points='8989')),
         'formationIconPath': RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LADDER_64_0,
         'tableHeaders': self.__packTableHeaders()}

    def getViewerFormation(self):
        return 10

    def __packLadderData(self):
        formations = []
        formationsCount = 50
        for i in range(formationsCount):
            id = i + 1
            place = i + 1
            points = random.randint(1, 400)
            battlesCount = random.randint(1, 100)
            winPercent = random.randint(1, 100)
            himself = self.getViewerFormation() == id
            name = 'FORMATIONSSSSSSS' + ('0' if id < 10 else '') + str(i)
            motto = name + ' motto'
            formations.append(self.__packLadderItemData(id, place, points, name, motto, battlesCount, winPercent, himself))

        return {'formations': formations}

    def __packLadderItemData(self, id, place, points, name, motto, battlesCount, winPercent, himself):
        data = {'formationId': id,
         'showProfileBtnText': _ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_SHOWFORMATIONPROFILEBTN_TEXT),
         'showProfileBtnTooltip': TOOLTIPS.STATICFORMATIONLADDERVIEW_SHOWFORMATIONPROFILEBTN,
         'formationMotto': self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, motto),
         'emblemIconPath': ''}
        self.__packStrPlrValue(data, 'place', place, str(place) + '.', TextType.STANDARD_TEXT)
        self.__packNumberPlrValue(data, 'points', points, style=TextType.MIDDLE_TITLE)
        self.__packStrPlrValue(data, 'formationName', name, name, TextType.HIGH_TITLE)
        self.__packNumberPlrValue(data, 'battlesCount', battlesCount, TextType.MIDDLE_TITLE)
        self.__packStrPlrValue(data, 'winPercent', winPercent, str(winPercent) + '%', TextType.MIDDLE_TITLE)
        return data

    def __packPlrValue(self, objData, fieldName, sortValue, value):
        objData[fieldName + 'SortValue'] = sortValue
        objData[fieldName] = value

    def __packStrPlrValue(self, objData, fieldName, sortValue, value, style):
        self.__packPlrValue(objData, fieldName, sortValue, self.app.utilsManager.textManager.getText(style, value))

    def __packNumberPlrValue(self, objData, fieldName, value, style = TextType.MAIN_TEXT):
        self.__packStrPlrValue(objData, fieldName, value, str(value), style)

    def __packTableHeaders(self):
        headers = []
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERPLACE_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERPLACE, 'place', 1))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERPOINTS_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERPOINTS, 'points', 2))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERFORMATIONNAME_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERFORMATIONNAME, 'formationName'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERBATTLESCOUNT_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERBATTLESCOUNT, 'battlesCount'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERWINSPERCENT_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERWINPERCENT, 'winPercent'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERSHOWFORMATIONPROFILE_TEXT), TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERSHOWFORMATIONPROFILE))
        return headers

    def __packTableHeaderItem(self, label, tooltip = '', fieldName = '', sortOrder = 0):
        _getText = self.app.utilsManager.textManager.getText
        return {'label': _getText(TextType.STANDARD_TEXT, label),
         'toolTip': tooltip,
         'sortOrder': sortOrder,
         'iconId': fieldName + 'SortValue' if len(fieldName) > 0 else fieldName}
