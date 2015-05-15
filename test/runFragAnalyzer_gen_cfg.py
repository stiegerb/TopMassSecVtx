import FWCore.ParameterSet.Config as cms

process = cms.Process('GEN')

import sys
UEtune=sys.argv[2]

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic8TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(500000)
)
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.load('UserCode.TopMassSecVtx.fragAnalyzer_cfi')
from UserCode.TopMassSecVtx.ttMadgraphConfig_cff import configureTTGenerator
print 'Running for %s'%UEtune
pythiaUESettingsBlock=configureTTGenerator(process,UEtune)
process.TFileService = cms.Service("TFileService", fileName = cms.string("FragmentationDist_%s.root"%UEtune))

process.options = cms.untracked.PSet(

)

process.source = cms.Source("EmptySource")

process.generator = cms.EDFilter("Pythia6GeneratorFilter",
                                 ExternalDecays = cms.PSet(Tauola = cms.untracked.PSet(UseTauolaPolarization = cms.bool(True),
                                                                                       InputCards = cms.PSet(mdtau = cms.int32(0),
                                                                                                             pjak2 = cms.int32(0),
                                                                                                             pjak1 = cms.int32(0)
                                                                                                             )
                                                                                       ),
                                                           parameterSets = cms.vstring('Tauola')
                                                           ),
                                 UseExternalGenerators = cms.untracked.bool(True),
                                 pythiaPylistVerbosity = cms.untracked.int32(1),
                                 pythiaHepMCVerbosity = cms.untracked.bool(True),
                                 comEnergy = cms.double(8000.0),
                                 maxEventsToPrint = cms.untracked.int32(0),
                                 crossSection = cms.untracked.double(131.7),
                                 PythiaParameters = cms.PSet( pythiaUESettings=pythiaUESettingsBlock.pythiaUESettings,
                                                              processParameters = cms.vstring('MSEL=0         ! User defined processes', 
                                                                                              'MSUB(81)  = 1     ! qqbar to QQbar',
                                                                                              'MSUB(82)  = 1     ! gg to QQbar',
                                                                                              'MSTP(7)   = 6     ! flavor = top',
                                                                                              'PMAS(5,1)=4.8   ! b quark mass', 
                                                                                              'PMAS(6,1)=172.5 ! t quark mass', 
                                                                                              'MSTJ(1)=1       ! Fragmentation/hadronization on or off', 
                                                                                              'MSTP(61)=1      ! Parton showering on or off'),
                                                           parameterSets = cms.vstring('pythiaUESettings', 
                                                                                       'processParameters')
                                                              )
                                 )


# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.28 $'),
    annotation = cms.untracked.string('tt nevts:1'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'START53_V23::All', '')

# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen*process.fragAnalyzer)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step)
for path in process.paths:
    getattr(process,path)._seq = process.generator * getattr(process,path)._seq 
