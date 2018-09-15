# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_break.py
import BigWorld
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, HtmlMessageDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.daapi.view.meta.NYScreenBreakMeta import NYScreenBreakMeta
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.new_year_types import g_cache
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearUIManager
from items.new_year_types import MAX_TOY_RANK, TOY_TYPES, NATIONAL_SETTINGS

def formatSortString(total, sortedTotal):
    sortedTotalStr = text_styles.error('0') if sortedTotal == 0 else text_styles.stats(str(sortedTotal))
    toysAmountStr = '{} / {}'.format(sortedTotalStr, str(total))
    return toysAmountStr


class NY_Break(NYHelperView, NYScreenBreakMeta):
    newYearUIManager = dependency.descriptor(INewYearUIManager)
    BREAK_CONFIRMATION_VALUE = 240

    def __init__(self, ctx=None):
        super(NY_Break, self).__init__(ctx)
        self.__selectedToys = dict()
        self.__gain = 0
        self.__inDispose = False

    @staticmethod
    def _getDummy():
        return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': text_styles.main(_ms(NY.BREAKSCREEN_NOTOYS_LABEL)),
         'alignCenter': False,
         'btnVisible': False,
         'btnLabel': '',
         'btnTooltip': '',
         'btnEvent': '',
         'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK}

    @staticmethod
    def _getDummyFilter():
        return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': text_styles.main(_ms(NY.BREAKSCREEN_NOTOYSINFILTER_LABEL)),
         'alignCenter': False,
         'btnVisible': True,
         'btnLabel': NY.BREAKSCREEN_CANCELFILTERBTN_LABEL,
         'btnTooltip': '',
         'btnEvent': '',
         'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK}

    def _populate(self):
        super(NY_Break, self)._populate()
        NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_BREAK)
        NYSoundEvents.setState(NYSoundEvents.STATE_ON_BREAK)
        self.resetFilters()
        self.__selectedToys.clear()
        self.__gain = 0
        self.__inDispose = False
        self.__inBreakDlg = False
        toys, total, sortedTotal = self.__updateShownToysAndSelection()
        initData = {'cancelBtnLabel': NY.BREAKSCREEN_CANCELBTN_LABEL,
         'backBtnDescrLabel': NY.BREAKSCREEN_BACKBTN_TO_HANGAR,
         'breakToyFragmentTitle': NY.BREAKSCREEN_BREAKTOYFRAGMENT_TITLE,
         'lackToyFragmentTitle': NY.BREAKSCREEN_LACKTOYFRAGMENT_TITLE,
         'balanceToyFragmentTitle': NY.BREAKSCREEN_BALANCETOYFRAGMENT_TITLE,
         'enoughToyFragmentTitle': NY.BREAKSCREEN_ENOUGHTOYFRAGMENT_TITLE,
         'dummyVO': self._getDummy(),
         'dummyFilterVO': self._getDummyFilter(),
         'decorationsAmountText': formatSortString(total, sortedTotal),
         'title': NY.BREAKSCREEN_TITLE}
        self.as_setInitDataS(initData)
        self.as_setToysS(toys)
        self.as_setBalanceToyFragmentS(BigWorld.wg_getIntegralFormat(self._newYearController.getToyFragments()))
        self.__updateSelectedToyPrice()
        self.__updateBreakButton()
        self._newYearController.onToyFragmentsChanged += self.__onToyFragmentsChanged
        self._newYearController.onToysBreak += self.__showOnToysBreakAnimation
        self._newYearController.onToysBreakFailed += self.__onToysBreakFailed
        self._newYearController.onInventoryUpdated += self.__updateToys
        self.newYearUIManager.onCraftPopoverFilterChanged += self.__updateToys

    def onBack(self):
        self.__switchGuard() and self._switchBack(previewAlias=VIEW_ALIAS.LOBBY_NY_BREAK)

    def onBackClick(self):
        self.__switchGuard() and self._switchToCraft(previewAlias=VIEW_ALIAS.LOBBY_NY_BREAK)

    def onCraftClick(self):
        self.onBackClick()

    def onClose(self):
        self.__switchGuard() and self._switchToNYMain(previewAlias=VIEW_ALIAS.LOBBY_NY_BREAK)

    def onBreak(self):
        self.__onBreak()

    @process
    def __onBreak(self):
        if self.__inDispose:
            return
        if self.__gain >= self.BREAK_CONFIRMATION_VALUE:
            self.__inBreakDlg = True
            ctx = {'fragments_amount': BigWorld.wg_getIntegralFormat(self.__gain)}
            is_ok = yield DialogsInterface.showDialog(meta=I18nConfirmDialogMeta('confirmToysBreak', ctx, ctx, meta=HtmlMessageDialogMeta('html_templates:newYear/dialogs', 'confirmToysBreak', ctx, sourceKey='text'), focusedID=DIALOG_BUTTON_ID.SUBMIT))
            self.__inBreakDlg = False
            if is_ok:
                self.__doBreak()
        else:
            self.__doBreak()

    def __doBreak(self):
        toysForNYC = []
        toysIndexes = []
        for toyId, indexes in self.__selectedToys.iteritems():
            toysForNYC.append([toyId, len(indexes)])
            toysIndexes.extend(indexes)

        if self._newYearController.breakToys(toysForNYC, toysIndexes):
            self.as_onToyBreakStartS()
            self.__selectedToys.clear()

    def __showOnToysBreakAnimation(self, indexes, fromSlot):
        if indexes and not fromSlot:
            self.as_setBreakToysIndexS(indexes)

    def __onToysBreakFailed(self):
        self.as_onToysBreakFailedS()

    def resetFilters(self):
        filterData = dict(levels=None, types=None, nations=None)
        self.newYearUIManager.setCraftPopoverFilter(filterData)
        return

    def _dispose(self):
        self.__selectedToys.clear()
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_BREAK)
        self._newYearController.onToyFragmentsChanged -= self.__onToyFragmentsChanged
        self._newYearController.onToysBreak -= self.__showOnToysBreakAnimation
        self._newYearController.onToysBreakFailed -= self.__onToysBreakFailed
        self._newYearController.onInventoryUpdated -= self.__updateToys
        self.newYearUIManager.onCraftPopoverFilterChanged -= self.__updateToys
        super(NY_Break, self)._dispose()

    def onToySelectChange(self, toyId, index, isSelected):
        if isSelected:
            if toyId in self.__selectedToys:
                self.__selectedToys[toyId].append(index)
            else:
                self.__selectedToys[toyId] = [index]
        elif toyId in self.__selectedToys:
            self.__selectedToys[toyId].remove(index)
        self.__updateGain()
        self.__updateBreakButton()

    def __onToyFragmentsChanged(self, fragmentsCount):
        self.as_setBalanceToyFragmentS(BigWorld.wg_getIntegralFormat(fragmentsCount))
        self.__updateSelectedToyPrice()

    def __updateToys(self):
        toys, total, sortedTotal = self.__updateShownToysAndSelection()
        self.as_setToysAmountStrS(formatSortString(total, sortedTotal), not self.__isFilterDisabled())
        self.as_setToysS(toys)
        self.__updateGain()
        self.__updateBreakButton()

    def __getSortedToys(self):
        toysList = list()
        for _, toys in self._newYearController.getInventory().items():
            for toy in toys.values():
                toysList.append(toy)

        toysList.sort(key=lambda t: [-t.item.rank, t.item.type, self._newYearController.getSettingIndexInNationsOrder(t.item.setting)])
        return toysList

    def __updateShownToysAndSelection(self):
        self.__updateSelectedToys()
        toysData = []
        toysTotal = 0
        for toyItemInfo in self.__getSortedToys():
            toysTotal += toyItemInfo.count
            if self.__checkToy(toyItemInfo.item):
                toyId = toyItemInfo.item.id
                for i in range(0, toyItemInfo.count):
                    isSelected = True if toyId in self.__selectedToys and i < len(self.__selectedToys[toyId]) else False
                    toysData.append({'icon': toyItemInfo.item.icon,
                     'id': toyId,
                     'level': toyItemInfo.item.rank,
                     'select': isSelected,
                     'toggle': True,
                     'isCanUpdateNew': False,
                     'canShowContextMenu': False,
                     'isNew': toyItemInfo.newCount > i,
                     'settings': toyItemInfo.item.setting})

        self.__selectedToys.clear()
        for index, toyData in enumerate(toysData):
            if toyData['select']:
                if toyData['id'] in self.__selectedToys:
                    self.__selectedToys[toyData['id']].append(index)
                else:
                    self.__selectedToys[toyData['id']] = [index]

        sortedTotal = len(toysData)
        return (toysData, toysTotal, sortedTotal)

    def __checkToy(self, toy):
        filterData = self.newYearUIManager.getCraftPopoverFilter()
        if filterData is None:
            return True
        else:
            levelSettings = filterData.get('levels', None)
            if levelSettings:
                if toy.rank not in levelSettings:
                    return False
            typeSettings = filterData.get('types', None)
            if typeSettings:
                if toy.type not in typeSettings:
                    return False
            nationSettings = filterData.get('nations', None)
            if nationSettings:
                if toy.setting not in nationSettings:
                    return False
            return True

    def __isFilterDisabled(self):
        filterData = self.newYearUIManager.getCraftPopoverFilter()
        if not filterData:
            return True
        else:
            levelSettings = filterData.get('levels', None)
            if levelSettings and len(levelSettings) < MAX_TOY_RANK:
                return False
            typeSettings = filterData.get('types', None)
            if typeSettings and len(typeSettings) < len(TOY_TYPES):
                return False
            nationSettings = filterData.get('nations', None)
            return False if nationSettings and len(nationSettings) < len(NATIONAL_SETTINGS) else True

    def __updateGain(self):
        self.__gain = 0
        for toyId, toyIndexes in self.__selectedToys.items():
            self.__gain += self._newYearController.getFragmentsForToy(toyId) * len(toyIndexes)

        self.as_setBreakToyFragmentS(BigWorld.wg_getIntegralFormat(self.__gain))

    def __updateSelectedToys(self):
        updatedToys = dict()
        for toyId in self.__selectedToys:
            toyDescr = g_cache.toys.get(toyId, None)
            if toyDescr is not None and self.__checkToy(toyDescr):
                updatedToys[toyId] = self.__selectedToys[toyId]

        self.__selectedToys = updatedToys
        return

    def __updateSelectedToyPrice(self):
        selectedToy = self.newYearUIManager.getSelectedCraftToy()
        toyType = selectedToy.get('type', None) if selectedToy else None
        toyLevel = selectedToy.get('level', None) if selectedToy else None
        toyNation = selectedToy.get('nation', None) if selectedToy else None
        toyPrice = self._newYearController.getPriceForCraft(toyType, toyNation, toyLevel)
        lack = toyPrice - self._newYearController.getToyFragments()
        toyPriceStr = BigWorld.wg_getIntegralFormat(lack) if lack > 0 else ''
        self.as_setLackToyFragmentS(toyPriceStr)
        if toyType:
            self.as_setLackToyFragmentTypeS(toyType)
        else:
            self.as_setLackToyFragmentTypeS('random')
        return

    def __updateBreakButton(self):
        toysAmount = sum((len(toy) for toy in self.__selectedToys.values()))
        self.as_setBreakButtonLabelS(_ms(NY.BREAKSCREEN_BREAKBTN_LABELCOUNT, count=toysAmount) if toysAmount else NY.BREAKSCREEN_BREAKBTN_LABEL)

    def __switchGuard(self):
        if self.__inBreakDlg:
            return False
        self.__inDispose = True
        return True
