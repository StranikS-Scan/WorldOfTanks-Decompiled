# Embedded file name: scripts/common/dossiers/__init__.py
import dossiers1
import dossiers2
import struct

def getAccountDossierDescr(compDescr = ''):
    if compDescr == '':
        return dossiers1.getAccountDossierDescr()
    version = struct.unpack_from('<H', compDescr)[0]
    if version < 64:
        return dossiers1.getAccountDossierDescr(compDescr)
    d2 = dossiers2.getAccountDossierDescr(compDescr)
    d = dossiers1.getAccountDossierDescr()
    d.expand()
    total = d2.expand('total')
    for record in ['creationTime',
     'lastBattleTime',
     'battleLifeTime',
     'treesCut',
     'mileage']:
        d[record] = total[record]

    a15x15 = d2.expand('a15x15')
    for record in ['xp',
     'battlesCount',
     'wins',
     'winAndSurvived',
     'losses',
     'survivedBattles',
     'frags',
     'frags8p',
     'shots',
     'directHits',
     'spotted',
     'damageDealt',
     'damageReceived',
     'capturePoints',
     'droppedCapturePoints',
     'xpBefore8_8',
     'battlesCountBefore8_8']:
        d[record] = a15x15[record]

    a15x15_2 = d2.expand('a15x15_2')
    for record in ['originalXP',
     'damageAssistedTrack',
     'damageAssistedRadio',
     'directHitsReceived',
     'noDamageDirectHitsReceived',
     'piercingsReceived',
     'explosionHitsReceived',
     'explosionHits',
     'piercings']:
        d[record] = a15x15_2[record]

    max15x15 = d2.expand('max15x15')
    for record in ['maxFrags',
     'maxXP',
     'maxXPVehicle',
     'maxFragsVehicle']:
        d[record] = max15x15[record]

    vehTypeFrags = d2.expand('vehTypeFrags')
    vehTypeFrags_copy = {}
    for vehTypeCompDescr, frags in vehTypeFrags.iteritems():
        vehTypeFrags_copy[vehTypeCompDescr] = frags

    d['vehTypeFrags'] = vehTypeFrags_copy
    achievements = d2.expand('achievements')
    for record in ['fragsBeast',
     'sniperSeries',
     'invincibleSeries',
     'diehardSeries',
     'killingSeries',
     'fragsSinai',
     'piercingSeries',
     'warrior',
     'invader',
     'sniper',
     'defender',
     'steelwall',
     'supporter',
     'scout',
     'evileye',
     'medalWittmann',
     'medalOrlik',
     'medalOskin',
     'medalHalonen',
     'medalBurda',
     'medalBillotte',
     'medalKolobanov',
     'medalFadin',
     'medalRadleyWalters',
     'medalBrunoPietro',
     'medalTarczay',
     'medalPascucci',
     'medalDumitru',
     'medalLehvaslaiho',
     'medalNikolas',
     'medalLafayettePool',
     'heroesOfRassenay',
     'tankExpertStrg',
     'raider',
     'kamikaze',
     'lumberjack',
     'medalBrothersInArms',
     'medalCrucialContribution',
     'medalDeLanglade',
     'medalTamadaYoshio',
     'bombardier',
     'huntsman',
     'alaric',
     'sturdy',
     'ironMan',
     'luckyDevil',
     'fragsPatton',
     'mechanicEngineerStrg']:
        d[record] = achievements[record]

    a15x15Cut = d2.expand('a15x15Cut')
    a15x15Cut_copy = {}
    for vehTypeCompDescr, cut in a15x15Cut.iteritems():
        a15x15Cut_copy[vehTypeCompDescr] = cut

    d['a15x15Cut'] = a15x15Cut_copy
    rareAchievements = d2.expand('rareAchievements')
    rareAchievements_copy = []
    for achievement in rareAchievements:
        rareAchievements_copy.append(achievement)

    d['rareAchievements'] = rareAchievements_copy
    return dossiers1.getAccountDossierDescr(d.makeCompDescr())


def getVehicleDossierDescr(compDescr = ''):
    if compDescr == '':
        return dossiers1.getVehicleDossierDescr()
    version = struct.unpack_from('<H', compDescr)[0]
    if version < 64:
        return dossiers1.getVehicleDossierDescr(compDescr)
    d2 = dossiers2.getVehicleDossierDescr(compDescr)
    d = dossiers1.getVehicleDossierDescr()
    d.expand()
    total = d2.expand('total')
    for record in ['creationTime',
     'lastBattleTime',
     'battleLifeTime',
     'treesCut',
     'mileage']:
        d[record] = total[record]

    a15x15 = d2.expand('a15x15')
    for record in ['xp',
     'battlesCount',
     'wins',
     'winAndSurvived',
     'losses',
     'survivedBattles',
     'frags',
     'frags8p',
     'shots',
     'directHits',
     'spotted',
     'damageDealt',
     'damageReceived',
     'capturePoints',
     'droppedCapturePoints',
     'xpBefore8_8',
     'battlesCountBefore8_8']:
        d[record] = a15x15[record]

    a15x15_2 = d2.expand('a15x15_2')
    for record in ['originalXP',
     'damageAssistedTrack',
     'damageAssistedRadio',
     'directHitsReceived',
     'noDamageDirectHitsReceived',
     'piercingsReceived',
     'explosionHitsReceived',
     'explosionHits',
     'piercings']:
        d[record] = a15x15_2[record]

    max15x15 = d2.expand('max15x15')
    for record in ['maxFrags', 'maxXP']:
        d[record] = max15x15[record]

    vehTypeFrags = d2.expand('vehTypeFrags')
    vehTypeFrags_copy = {}
    for vehTypeCompDescr, frags in vehTypeFrags.iteritems():
        vehTypeFrags_copy[vehTypeCompDescr] = frags

    d['vehTypeFrags'] = vehTypeFrags_copy
    achievements = d2.expand('achievements')
    for record in ['fragsBeast',
     'sniperSeries',
     'invincibleSeries',
     'diehardSeries',
     'killingSeries',
     'fragsSinai',
     'piercingSeries',
     'warrior',
     'invader',
     'sniper',
     'defender',
     'steelwall',
     'supporter',
     'scout',
     'evileye',
     'medalWittmann',
     'medalOrlik',
     'medalOskin',
     'medalHalonen',
     'medalBurda',
     'medalBillotte',
     'medalKolobanov',
     'medalFadin',
     'medalRadleyWalters',
     'medalBrunoPietro',
     'medalTarczay',
     'medalPascucci',
     'medalDumitru',
     'medalLehvaslaiho',
     'medalNikolas',
     'medalLafayettePool',
     'heroesOfRassenay',
     'tankExpertStrg',
     'raider',
     'kamikaze',
     'lumberjack',
     'medalBrothersInArms',
     'medalCrucialContribution',
     'medalDeLanglade',
     'medalTamadaYoshio',
     'bombardier',
     'huntsman',
     'alaric',
     'sturdy',
     'ironMan',
     'luckyDevil',
     'fragsPatton',
     'markOfMastery']:
        d[record] = achievements[record]

    return dossiers1.getVehicleDossierDescr(d.makeCompDescr())


def getTankmanDossierDescr(compDescr = ''):
    if compDescr == '':
        return dossiers1.getTankmanDossierDescr()
    version = struct.unpack_from('<H', compDescr)[0]
    if version < 64:
        return dossiers1.getTankmanDossierDescr(compDescr)
    d2 = dossiers2.getTankmanDossierDescr(compDescr)
    d = dossiers1.getTankmanDossierDescr()
    d.expand()
    total = d2.expand('a15x15')
    for record in ['battlesCount']:
        d[record] = total[record]

    achievements = d2.expand('achievements')
    for record in ['warrior',
     'invader',
     'sniper',
     'defender',
     'steelwall',
     'supporter',
     'scout',
     'evileye',
     'medalWittmann',
     'medalOrlik',
     'medalOskin',
     'medalHalonen',
     'medalBurda',
     'medalBillotte',
     'medalKolobanov',
     'medalFadin',
     'medalRadleyWalters',
     'medalBrunoPietro',
     'medalTarczay',
     'medalPascucci',
     'medalDumitru',
     'medalLehvaslaiho',
     'medalNikolas',
     'medalLafayettePool',
     'heroesOfRassenay',
     'medalDeLanglade',
     'medalTamadaYoshio']:
        d[record] = achievements[record]

    return d


def getFortifiedRegionsDossierDescr(compDescr = ''):
    return dossiers2.getFortifiedRegionsDossierDescr(compDescr)
