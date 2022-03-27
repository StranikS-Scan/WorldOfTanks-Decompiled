# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/rts/rts_help_view.py
import logging
import Keys
from aih_constants import CTRL_MODE_NAME
from frameworks.wulf import WindowFlags, ViewSettings
from gui.battle_control import avatar_getter
from gui.battle_control.avatar_getter import isCommanderCtrlMode, setForcedGuiControlMode
from gui.battle_control.controllers.commander.common import MappedKeys
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.rts.help_actions_item_model import HelpActionsItemModel
from gui.impl.gen.view_models.views.battle.rts.help_actions_section_model import HelpActionsSectionModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_article_item_model import HelpControlsArticleItemModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_article_model import HelpControlsArticleModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_section_model import HelpControlsSectionModel
from gui.impl.gen.view_models.views.battle.rts.help_view_model import HelpViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl import backport
from gui.shared.utils.key_mapping import getKeyAsString
_logger = logging.getLogger(__name__)

class RtsHelpView(ViewImpl):
    GROUP_START = '1'
    GROUP_END = '7'

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.battle.rts.HelpView(), model=HelpViewModel())
        super(RtsHelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._handleClose

    def _finalize(self):
        self.viewModel.onClose -= self._handleClose

    def _updateViewModel(self):
        self.__updatePage1()
        self.__updatePage2()

    def _handleClose(self):
        if not self.getParentWindow().isHidden():
            self.getParentWindow().hide()

    def __updatePage1(self):
        with self.viewModel.transaction() as model:
            strRtsBattles = R.strings.rts_battles
            img = R.images.gui.maps.icons.rtsBattles
            sectionsArray = model.getControls()
            cameraControls = HelpControlsSectionModel()
            cameraControls.setIcon(img.help.camera())
            cameraControls.setHeader(strRtsBattles.help.cameraControls.header())
            ccArticles = cameraControls.getArticles()
            ccModel = HelpControlsArticleModel()
            mmb = backport.text(R.strings.readable_key_names.KEY_MOUSE2())
            lmb = backport.text(R.strings.readable_key_names.KEY_MOUSE0())
            rmb = backport.text(R.strings.readable_key_names.KEY_MOUSE1())
            ctrl = backport.text(R.strings.controls.keyboard.key_ctrl_wo_referral())
            shift = backport.text(R.strings.readable_key_names.KEY_SHIFT())
            self.__addControlsToSection(ccModel, strRtsBattles.help.cameraControls.move(), '' + getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CAM_FORWARD))[0] + ', ' + getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CAM_LEFT))[0] + ', ' + getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CAM_BACK))[0] + ', ' + getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CAM_RIGHT))[0])
            self.__addControlsToSection(ccModel, strRtsBattles.help.cameraControls.rotate(), backport.text(strRtsBattles.help.camera.rotateKey(), key=mmb))
            self.__addControlsToSection(ccModel, strRtsBattles.help.camera.zoom(), backport.text(strRtsBattles.help.camera.zoomKey(), key=getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CAM_ZOOM))[0]))
            self.__addControlsToSection(ccModel, strRtsBattles.help.camera.view(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_GOTO_CONTACT))[0])
            vehiclesSelection = HelpControlsSectionModel()
            vehiclesSelection.setIcon(img.help.selection())
            vehiclesSelection.setHeader(strRtsBattles.help.selection.header())
            vsArticles = vehiclesSelection.getArticles()
            vsModel = HelpControlsArticleModel()
            self.__addControlsToSection(vsModel, strRtsBattles.help.selection.selectOnScene(), backport.text(strRtsBattles.help.selection.selectOnSceneKey(), key=lmb))
            self.__addControlsToSection(vsModel, strRtsBattles.help.selection.createGroup(), backport.text(strRtsBattles.help.selection.createGroupKey(), start=self.GROUP_START, to=self.GROUP_END, key=ctrl))
            self.__addControlsToSection(vsModel, strRtsBattles.help.selection.selectSeveral(), backport.text(strRtsBattles.help.selection.selectSeveralKey(), ctrl=ctrl, shift=shift, key=lmb))
            self.__addControlsToSection(vsModel, strRtsBattles.help.selection.selectAll(), backport.text(strRtsBattles.help.selection.selectAllKey(), ctrl=ctrl, key=getKeyAsString(Keys.KEY_A)[0]))
            self.__addControlsToSection(vsModel, strRtsBattles.help.selection.selectOnPanel(), backport.text(strRtsBattles.help.selection.selectOnPanelKey(), start=self.GROUP_START, to=self.GROUP_END))
            ordersAndCommands = HelpControlsSectionModel()
            ordersAndCommands.setIcon(img.help.orders())
            ordersAndCommands.setHeader(strRtsBattles.help.orders.header())
            ocArticles = ordersAndCommands.getArticles()
            mModel = HelpControlsArticleModel()
            mModel.setHeader(strRtsBattles.help.orders.movement.header())
            self.__addControlsToSection(mModel, strRtsBattles.help.orders.movement.move(), rmb)
            self.__addControlsToSection(mModel, strRtsBattles.help.orders.movement.rush(), backport.text(strRtsBattles.help.orders.movement.rushKey(), rmb=rmb, key=getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_FORCE_ORDER_MODE))[0]))
            self.__addControlsToSection(mModel, strRtsBattles.help.orders.movement.fallBack(), backport.text(strRtsBattles.help.orders.movement.fallBackKey(), rmb=rmb, key=getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_REV_MOVE))[0]))
            aeModel = HelpControlsArticleModel()
            aeModel.setHeader(strRtsBattles.help.orders.attack.header())
            self.__addControlsToSection(aeModel, strRtsBattles.help.orders.attack.attack(), rmb)
            self.__addControlsToSection(aeModel, strRtsBattles.help.orders.attack.charge(), backport.text(strRtsBattles.help.orders.attack.chargeKey(), rmb=rmb, key=getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_FORCE_ORDER_MODE))[0]))
            miModel = HelpControlsArticleModel()
            miModel.setHeader(strRtsBattles.help.orders.misc.header())
            self.__addControlsToSection(miModel, strRtsBattles.help.orders.misc.queueOrders(), backport.text(strRtsBattles.help.orders.misc.queueOrdersKey(), shift=shift, key=rmb))
            self.__addControlsToSection(miModel, strRtsBattles.help.orders.misc.stopAndCancel(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_HALT))[0])
            self.__addControlsToSection(miModel, strRtsBattles.help.orders.misc.controlModeSwitch(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_CONTROL_VEHICLE))[0])
            self.__addControlsToSection(miModel, strRtsBattles.help.orders.misc.lineOfFire(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_SHOW_TRAJECTORY))[0])
            vsModel.getHelpItems().invalidate()
            ccModel.getHelpItems().invalidate()
            ccArticles.addViewModel(ccModel)
            ccArticles.invalidate()
            vsArticles.addViewModel(vsModel)
            vsArticles.invalidate()
            ocArticles.addViewModel(mModel)
            ocArticles.addViewModel(aeModel)
            ocArticles.addViewModel(miModel)
            ocArticles.invalidate()
            sectionsArray.addViewModel(cameraControls)
            sectionsArray.addViewModel(vehiclesSelection)
            sectionsArray.addViewModel(ordersAndCommands)
            sectionsArray.invalidate()

    def __updatePage2(self):
        with self.viewModel.transaction() as model:
            strRtsBattles = R.strings.rts_battles
            img = R.images.gui.maps.icons.rtsBattles
            rmb = backport.text(R.strings.readable_key_names.KEY_MOUSE1())
            actionsSectionsArray = model.getActions()
            orderTypes = HelpActionsSectionModel()
            orderTypes.setHeader(strRtsBattles.help.orderTypes.header())
            self.__addActionsToSection(orderTypes, img.help.movement(), strRtsBattles.help.orderTypes.movement.brief(), rmb, strRtsBattles.help.orderTypes.movement.description())
            self.__addActionsToSection(orderTypes, img.help.rush(), strRtsBattles.help.orderTypes.rush.brief(), backport.text(strRtsBattles.help.orderTypes.rush.key(), rmb=rmb, key=getKeyAsString(Keys.KEY_C)[0]), strRtsBattles.help.orderTypes.rush.description())
            self.__addActionsToSection(orderTypes, img.help.attack(), strRtsBattles.help.orderTypes.attack.brief(), rmb, strRtsBattles.help.orderTypes.attack.description())
            self.__addActionsToSection(orderTypes, img.help.charge(), strRtsBattles.help.orderTypes.charge.brief(), backport.text(strRtsBattles.help.orderTypes.rush.key(), rmb=rmb, key=getKeyAsString(Keys.KEY_C)[0]), strRtsBattles.help.orderTypes.charge.description())
            self.__addActionsToSection(orderTypes, img.help.fall_back(), strRtsBattles.help.orderTypes.fallBack.brief(), backport.text(strRtsBattles.help.orderTypes.fallBack.key(), rmb=rmb, key=getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_REV_MOVE))[0]), strRtsBattles.help.orderTypes.fallBack.description())
            modes = HelpActionsSectionModel()
            modes.setHeader(strRtsBattles.help.behavior.header())
            self.__addActionsToSection(modes, img.help.adaptive(), strRtsBattles.help.behavior.adaptive.brief(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_SMART_MANNER))[0], strRtsBattles.help.behavior.adaptive.description())
            self.__addActionsToSection(modes, img.help.hold(), strRtsBattles.help.behavior.hold.brief(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_HOLD_MANNER))[0], strRtsBattles.help.behavior.hold.description())
            self.__addActionsToSection(modes, img.help.recon(), strRtsBattles.help.behavior.recon.brief(), getKeyAsString(MappedKeys.getKey(MappedKeys.KEY_SCOUT_MANNER))[0], strRtsBattles.help.behavior.recon.description())
            modes.getArticles().invalidate()
            orderTypes.getArticles().invalidate()
            actionsSectionsArray.addViewModel(orderTypes)
            actionsSectionsArray.addViewModel(modes)
            actionsSectionsArray.invalidate()

    def __addActionsToSection(self, sectionModel, icon, action, keyHint, desc):
        articles = sectionModel.getArticles()
        item = HelpActionsItemModel()
        item.setIcon(icon)
        item.setAction(action)
        item.setKeyHint(keyHint)
        item.setDescription(desc)
        articles.addViewModel(item)

    def __addControlsToSection(self, sectionModel, action, keyHint):
        helperItems = sectionModel.getHelpItems()
        item = HelpControlsArticleItemModel()
        item.setAction(action)
        item.setKeyHint(keyHint)
        helperItems.addViewModel(item)


class HelpWindow(WindowImpl):

    def __init__(self):
        super(HelpWindow, self).__init__(wndFlags=WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN, content=RtsHelpView())

    def load(self):
        if self.handleCameraChange not in avatar_getter.getInputHandler().onCameraChanged:
            avatar_getter.getInputHandler().onCameraChanged += self.handleCameraChange
        if not isCommanderCtrlMode():
            self.__showCursorDisableAiming()
        super(HelpWindow, self).load()

    def show(self):
        if not isCommanderCtrlMode():
            self.__showCursorDisableAiming()
        super(HelpWindow, self).show()

    def hide(self):
        if not isCommanderCtrlMode() and not self.isHidden():
            setForcedGuiControlMode(False)
        super(HelpWindow, self).hide()

    def handleCameraChange(self, mode, _):
        if not self.isHidden() and mode == CTRL_MODE_NAME.ARCADE:
            self.__showCursorDisableAiming()

    def _finalize(self):
        if avatar_getter.getInputHandler():
            avatar_getter.getInputHandler().onCameraChanged -= self.handleCameraChange

    def __showCursorDisableAiming(self):
        setForcedGuiControlMode(True, enableAiming=False, cursorVisible=True)
