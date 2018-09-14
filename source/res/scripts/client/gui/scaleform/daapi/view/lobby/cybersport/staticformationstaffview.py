# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationStaffView.py
import random
import BigWorld
from gui.Scaleform.daapi.view.meta.StaticFormationStaffViewMeta import StaticFormationStaffViewMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from helpers.i18n import makeString as _ms
from helpers import time_utils
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from debug_utils import LOG_DEBUG
from gui.Scaleform.genConsts.FORMATION_MEMBER_TYPE import FORMATION_MEMBER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from adisp import process

class StaticFormationStaffView(StaticFormationStaffViewMeta, AppRef):

    def __init__(self):
        super(StaticFormationStaffView, self).__init__()

    def _populate(self):
        super(StaticFormationStaffView, self)._populate()
        self.as_setStaticHeaderDataS(self.__packStaticHeaderData())
        self.as_updateHeaderDataS(self.__packHeaderData())
        self.as_updateStaffDataS(self.__packStaffData())

    def _dispose(self):
        super(StaticFormationStaffView, self)._dispose()

    def showInviteWindow(self):
        LOG_DEBUG('call StaticFormationStaffView.showInviteWindow')

    def showRecriutmentWindow(self):
        LOG_DEBUG('call StaticFormationStaffView.showRecriutmentWindow')

    def setRecruitmentOpened(self, opened):
        LOG_DEBUG('call StaticFormationStaffView.setRecruitmentOpened ' + str(opened))

    @process
    def promoteMember(self, id, userName):
        LOG_DEBUG('call StaticFormationStaffView.promoteMember id: ' + str(id))
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/promoteConfirmation', messageCtx={'userName': userName}))
        if isOk:
            LOG_DEBUG('TODO promote user id: ' + str(id))

    @process
    def demoteMember(self, id, userName):
        LOG_DEBUG('call StaticFormationStaffView.demoteMember id: ' + str(id))
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/demoteConfirmation', messageCtx={'userName': userName}))
        if isOk:
            LOG_DEBUG('TODO demote user id: ' + str(id))

    @process
    def removeMember(self, id, userName):
        LOG_DEBUG('call StaticFormationStaffView.removeMember id: ' + str(id))
        if self.isOwner(id):
            i18nId = 'staticFormation/staffView/discontinuingFormationConfirmation'
        else:
            i18nId = 'staticFormation/staffView/removeMemberConfirmation'
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(i18nId, messageCtx={'userName': userName}))
        if isOk:
            LOG_DEBUG('TODO remover user id: ' + str(id))

    def isOwner(self, id):
        return id == 0

    def getViewerId(self):
        return 0

    def __packHeaderData(self):
        return {'isRecruitmentAvailable': True,
         'isRecruitmentOpened': True}

    def __packStaticHeaderData(self):
        _getText = self.app.utilsManager.textManager.getText
        return {'title': _getText(TextType.HIGH_TITLE, _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_TITLE_TEXT)),
         'description': _getText(TextType.STANDARD_TEXT, _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_DESCRIPTION_TEXT)),
         'inviteBtnText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_INVITEBTN_TEXT),
         'recruitmentBtnText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTBTN_TEXT),
         'recruitmentOpenedText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTOPENEDCHKBX_TEXT),
         'tableHeaders': self.__packTableHeaders(),
         'inviteBtnTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_INVITEBTN,
         'recruitmentBtnTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_RECRUITMENTBTN}

    def __packStaffData(self):
        members = []
        membersCount = 7
        viewerIsOwner = self.isOwner(self.getViewerId())
        for i in range(membersCount):
            id = i
            if self.isOwner(id):
                memberType = FORMATION_MEMBER_TYPE.OWNER
            else:
                memberType = random.choice([FORMATION_MEMBER_TYPE.SOLDIER, FORMATION_MEMBER_TYPE.OFFICER, FORMATION_MEMBER_TYPE.INVITEE])
            orderNumber = i
            isIdOwner = self.isOwner(id)
            himself = self.getViewerId() == id
            canPromoted = viewerIsOwner
            canDemoted = viewerIsOwner
            canRemoved = not isIdOwner if membersCount > 1 and viewerIsOwner else himself
            canPassOwnership = viewerIsOwner and not isIdOwner and memberType != FORMATION_MEMBER_TYPE.INVITEE
            joinDate = time_utils.getCurrentTimestamp() - random.randint(0, 100) * time_utils.ONE_DAY
            canShowContextMenu = not himself
            name = 'Memberrrrrrrrrrrrrrrrrrr' + ('0' if i < 10 else '') + str(i)
            members.append(self.__packStaffItemData(id, orderNumber, name, memberType, canPromoted, canDemoted, canRemoved, canPassOwnership, canShowContextMenu, himself, joinDate))

        return {'members': members}

    def __packStaffItemData(self, id, orderNumber, name, memberType, canPromoted, canDemoted, canRemoved, canPassOwnership, canShowContextMenu, himself, joinDate):
        data = {'memberId': id,
         'canRemoved': canRemoved,
         'canPassOwnership': canPassOwnership,
         'canShowContextMenu': canShowContextMenu,
         'removeMemberBtnIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS,
         'removeMemberBtnTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_REMOVEMEMBERBTN}
        formatDate = BigWorld.wg_getShortDateFormat
        self.__packPlrValue(data, 'appointment', memberType, self.__packAppointment(memberType, canPromoted, canDemoted))
        self.__packStrPlrValue(data, 'orderNumber', orderNumber, str(orderNumber) + '.', TextType.STANDARD_TEXT)
        self.__packNumberPlrValue(data, 'rating', random.randint(1, 10000))
        self.__packNumberPlrValue(data, 'battlesCount', random.randint(1, 5000))
        self.__packNumberPlrValue(data, 'damageCoef', random.randint(1, 5000))
        self.__packNumberPlrValue(data, 'avrDamage', random.randint(1, 5000))
        self.__packNumberPlrValue(data, 'avrAssistDamage', random.randint(1, 5000))
        self.__packNumberPlrValue(data, 'avrExperience', random.randint(1, 5000))
        self.__packNumberPlrValue(data, 'taunt', random.randint(1, 5000))
        self.__packStrPlrValue(data, 'joinDate', joinDate, formatDate(joinDate), TextType.STANDARD_TEXT)
        self.__packPlrValue(data, 'userData', name, self.__packPlayerName(name, himself))
        return data

    def __packPlayerName(self, name, himself):
        return {'userName': name,
         'clanAbbrev': 'CLLL',
         'region': '',
         'igrType': 0,
         'tags': [],
         'colors': [13347959, 15327935]}

    def __packPlrValue(self, objData, fieldName, sortValue, value):
        objData[fieldName + 'SortValue'] = sortValue
        objData[fieldName] = value

    def __packStrPlrValue(self, objData, fieldName, sortValue, value, style):
        objData[fieldName + 'SortValue'] = sortValue
        objData[fieldName] = self.app.utilsManager.textManager.getText(style, value)

    def __packNumberPlrValue(self, objData, fieldName, value, style = TextType.MAIN_TEXT):
        self.__packStrPlrValue(objData, fieldName, value, str(value), style)

    def __packAppointment(self, memberType, canPromoted, canDemoted):
        return {'memberType': memberType,
         'canPromoted': canPromoted,
         'canDemoted': canDemoted,
         'promoteBtnIcon': RES_ICONS.MAPS_ICONS_BUTTONS_LEVEL_UP,
         'officerIcon': RES_ICONS.MAPS_ICONS_LIBRARY_COMMANDERICON,
         'demoteBtnIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS,
         'ownerIcon': RES_ICONS.MAPS_ICONS_LIBRARY_OWNERICON,
         'officerIconTooltip': TOOLTIPS.STATICFORMATION_OFFICERICON,
         'ownerIconTooltip': TOOLTIPS.STATICFORMATION_OWNERICON,
         'demoteBtnTooltip': TOOLTIPS.STATICFORMATION_DEMOTEBTN,
         'promoteBtnTooltip': TOOLTIPS.STATICFORMATION_PROMOTEBTN}

    def __packTableHeaders(self):
        headers = []
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERCOUNT_TEXT), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERCOUNT, 'orderNumber'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAPPOINTMENT_TEXT), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAPPOINTMENT, 'appointment', 1))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERNAME_TEXT), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERNAME, 'userData'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERRATING_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_RATING)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERRATING, 'rating', 2))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERBATTLESCOUNT_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_RATIO)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERBATTLESCOUNT, 'battlesCount'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERDAMAGECOEF_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_FIGHTS)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERDAMAGECOEF, 'damageCoef'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAVRDAMAGE_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_AVGDAMAGE)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRDAMAGE, 'avrDamage'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAVRASSISTDAMAGE_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_FIGHTS)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRASSISTDAMAGE, 'avrAssistDamage'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAVREXPIRIENCE_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_FIGHTS)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVREXPIRIENCE, 'avrExperience'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERTAUNT_TEXT, icon=self.__getHeaderIcon(RES_ICONS.MAPS_ICONS_STATISTIC_FIGHTS)), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERTAUNT, 'taunt'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERJOINDATE_TEXT), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERJOINDATE, 'joinDate'))
        headers.append(self.__packTableHeaderItem(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERREMOVEMEMBER_TEXT), TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERREMOVEMEMBER))
        return headers

    def __getHeaderIcon(self, icon):
        return self.app.utilsManager.getHtmlIconText(ImageUrlProperties(icon, 16, 16, -4))

    def __packTableHeaderItem(self, label, tooltip = '', fieldName = '', sortOrder = 0):
        _getText = self.app.utilsManager.textManager.getText
        return {'label': _getText(TextType.STANDARD_TEXT, label),
         'toolTip': tooltip,
         'sortOrder': sortOrder,
         'iconId': fieldName + 'SortValue' if len(fieldName) > 0 else fieldName}
