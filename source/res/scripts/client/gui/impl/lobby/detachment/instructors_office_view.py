# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/instructors_office_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.auxiliary.instructors_helper import fillInstructorBaseModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.instructors_office_model import InstructorsOfficeModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.shared.event_dispatcher import showDetachmentViewById
from helpers.dependency import descriptor
from items.components.detachment_constants import NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from sound_constants import BARRACKS_SOUND_SPACE

class InstructorsOfficeView(NavigationViewImpl):
    __slots__ = ('__previousView', '__detachmentInvID')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __detachmentCache = descriptor(IDetachmentCache)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = InstructorsOfficeModel()
        super(InstructorsOfficeView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__previousView = ctx['previousView']
        self.__detachmentInvID = ctx.get('detInvID', NO_DETACHMENT_ID)

    @property
    def viewModel(self):
        return super(InstructorsOfficeView, self).getViewModel()

    def _initModel(self, vm):
        super(InstructorsOfficeView, self)._initModel(vm)
        self.__setInstructors(vm)

    def _addListeners(self):
        super(InstructorsOfficeView, self)._addListeners()
        model = self.viewModel
        model.onMoveInstructorClick += self.__onMoveInstructorClick
        model.onHireInstructorClick += self.__onHireInstructorClick

    def _removeListeners(self):
        model = self.viewModel
        model.onMoveInstructorClick -= self.__onMoveInstructorClick
        model.onHireInstructorClick -= self.__onHireInstructorClick
        super(InstructorsOfficeView, self)._removeListeners()

    def __setInstructors(self, tx):
        detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
        instructors = tx.getInstructors()
        instructors.clear()
        for instructorInvID in detachment.getInstructorsIDs(skipNone=True):
            instructor = InstructorBaseModel()
            instructorItem = self.__detachmentCache.getInstructor(instructorInvID)
            fillInstructorBaseModel(instructor, instructorItem, fillPlaceholder=False)
            instructors.addViewModel(instructor)

        tx.setBackground(R.images.gui.maps.icons.detachment.backgrounds.bg_dark_room())
        tx.setHasDog(False)
        tx.setCanHire(False)
        tx.setDogTooltipHeader(R.strings.tooltips.hangar.crew.rudy.dog.ussr.header())
        tx.setDogTooltipDescription(R.strings.tooltips.hangar.crew.rudy.dog.ussr.body())
        instructors.invalidate()

    def __onMoveInstructorClick(self, args=None):
        pass

    def __onHireInstructorClick(self, args=None):
        showDetachmentViewById(NavigationViewModel.INSTRUCTORS_LIST, {'instructorInvID': 0,
         'slotID': 0,
         'detInvID': self.__detachmentInvID}, self._navigationViewSettings)

    def _onLoadPage(self, args=None):
        super(InstructorsOfficeView, self)._onLoadPage({'viewId': self.__previousView,
         'detInvID': self.__detachmentInvID})
