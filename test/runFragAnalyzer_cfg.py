2
import FWCore.ParameterSet.Config as cms

process = cms.Process('GEN')

import sys
model=sys.argv[2]

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 5000

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.load('UserCode.TopMassSecVtx.fragAnalyzer_cfi')
process.TFileService = cms.Service("TFileService", fileName = cms.string("FragmentationDist_%s.root"%model))

process.options = cms.untracked.PSet(
)

from UserCode.TopMassSecVtx.MarkusSherpaSamples_cfi import getMarkusSherpaSamplesFor
process.source = cms.Source("PoolSource",
                            fileNames = getMarkusSherpaSamplesFor(model),
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
                            )

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.28 $'),
    annotation = cms.untracked.string('tt nevts:1'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'START53_V23::All', '')

# Path and EndPath definitions
process.analysis = cms.Path(process.fragAnalyzer)
