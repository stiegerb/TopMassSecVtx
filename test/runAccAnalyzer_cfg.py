import FWCore.ParameterSet.Config as cms

process = cms.Process("DataAna")

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "START53_V23::All"

process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryIdeal_cff")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5000
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True),
                                        SkipEvent = cms.untracked.vstring('ProductNotFound')
                                        ) 

#the source and output
from UserCode.TopMassSecVtx.MarkusSherpaSamples_cfi import getMarkusSherpaSamplesFor
process.source = cms.Source("PoolSource",
                            fileNames = getMarkusSherpaSamplesFor('Lund'),
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
                            )


process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")

process.TFileService = cms.Service("TFileService", fileName = cms.string("AcceptanceAnalysis.root"))

process.accAnalyzer = cms.EDFilter("GeneratorLevelAcceptanceAnalyzer")

process.p = cms.Path( process.accAnalyzer )

