# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/builders.py
import time
from constants import DOSSIER_TYPE
from dossiers2.common.DossierBuilder import DossierBuilder
from dossiers2.common.utils import getDossierVersion
from layouts import *
from updaters import *
getAccountDossierVersion = lambda dossierCompDescr: getDossierVersion(dossierCompDescr, '<' + VERSION_RECORD_FORMAT, ACCOUNT_DOSSIER_VERSION)
getVehicleDossierVersion = lambda dossierCompDescr: getDossierVersion(dossierCompDescr, '<' + VERSION_RECORD_FORMAT, VEHICLE_DOSSIER_VERSION)
getTankmanDossierVersion = lambda dossierCompDescr: getDossierVersion(dossierCompDescr, '<' + VERSION_RECORD_FORMAT, TANKMAN_DOSSIER_VERSION)
getFortifiedRegionsDossierVersion = lambda dossierCompDescr: getDossierVersion(dossierCompDescr, '<' + VERSION_RECORD_FORMAT, FORT_DOSSIER_VERSION)

def _initializeNewDossier(dossierType, dossier):
    if dossierType == DOSSIER_TYPE.ACCOUNT:
        dossier['total']['creationTime'] = int(time.time())
    elif dossierType == DOSSIER_TYPE.VEHICLE:
        dossier['total']['creationTime'] = int(time.time())
    elif dossierType == DOSSIER_TYPE.FORTIFIED_REGIONS:
        dossier['total']['creationTime'] = int(time.time())
    elif dossierType == DOSSIER_TYPE.TANKMAN:
        pass


getAccountDossierDescr = DossierBuilder(accountDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, ACCOUNT_DOSSIER_VERSION, AccountDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.ACCOUNT, d)).build
getVehicleDossierDescr = DossierBuilder(vehicleDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, VEHICLE_DOSSIER_VERSION, VehicleDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.VEHICLE, d)).build
getTankmanDossierDescr = DossierBuilder(tmanDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, TANKMAN_DOSSIER_VERSION, TankmanDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.TANKMAN, d)).build
getClanDossierDescr = DossierBuilder(clanDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, CLAN_DOSSIER_VERSION, ClanDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.CLAN, d)).build
getFortifiedRegionsDossierDescr = DossierBuilder(fortDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, FORT_DOSSIER_VERSION, FortDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.FORTIFIED_REGIONS, d)).build
getRated7x7DossierDescr = DossierBuilder(rated7x7DossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, RATED7X7_DOSSIER_VERSION, Rated7x7DossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.RATED7X7, d)).build
getClubDossierDescr = DossierBuilder(clubDossierLayout, VERSION_RECORD_FORMAT, BLOCK_SIZE_RECORD_FORMAT, CLUB_DOSSIER_VERSION, ClubDossierVersionUpdater, lambda d: _initializeNewDossier(DOSSIER_TYPE.CLUB, d)).build
