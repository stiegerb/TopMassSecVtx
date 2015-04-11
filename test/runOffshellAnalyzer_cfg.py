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

width5=cms.untracked.vstring('/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/002FE906-F2AE-E311-BC3A-90E6BA442EF0.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00317D90-F4AF-E311-A48A-E0CB4E5536A8.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0051DFD9-5AB0-E311-9415-002590775016.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0054E898-59AF-E311-9CCC-485B398971FE.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00725579-EDAF-E311-BC6D-E0CB4E1A1191.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00782553-E8AF-E311-91A5-00259074AE82.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0084849E-E6AF-E311-852E-E0CB4E553639.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00AE0EC9-49AF-E311-9AC4-00259073E442.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00D9D189-09AF-E311-9C9C-90E6BA442F0D.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/022529A3-6DAF-E311-9FED-00259073E3FE.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0227866D-3AAF-E311-8067-002590D0B0D2.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02283183-82AF-E311-A7FF-00259073E488.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/023C9F23-E7AF-E311-9D7F-E0CB4E19F95B.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/023F2BF9-0FAF-E311-9624-E0CB4E1A119E.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/024444EB-EAAF-E311-82A6-52540062556D.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02742F44-2CAF-E311-819C-485B39800B62.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02A4C1EB-5DAF-E311-8DDA-00259073E4C8.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02A9325A-60AF-E311-BA0D-00259073E4C8.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02AC3023-19AF-E311-83C3-90E6BA19A232.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02B56061-47AF-E311-A79E-20CF3027A5C0.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02D121E6-16B0-E311-9A8F-90E6BA19A214.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02F18FFE-43AF-E311-B5D7-90E6BA0D09DC.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02FF7C6F-64AF-E311-8941-00259073E464.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/042842B8-52B0-E311-9693-20CF3027A5DC.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/046D8658-FCAF-E311-96F1-E0CB4E1A118F.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04B45F81-5EAF-E311-970B-20CF305616EA.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04C1DAF3-13AF-E311-83A1-90E6BA19A23C.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04C5CF1A-7BAF-E311-B1A7-E0CB4E19F9A6.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04D5FEBA-14AF-E311-9603-90E6BA0D099A.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04E4F91D-07AF-E311-8738-00259073E406.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04EB8E15-45B0-E311-90F8-00259074AE54.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0606E95B-F6AF-E311-80F0-90E6BA0D09EA.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/060E2587-69AF-E311-88B0-90E6BA442F1C.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/061348F6-76B0-E311-A8F4-BCAEC5097203.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06215759-DEAF-E311-A054-00259074AE8A.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/062377B9-1BAF-E311-BF30-0025907B4F32.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06330D50-E8AF-E311-8EAF-20CF305B0585.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06349A02-DFAF-E311-809E-002590D0AFEC.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06445E4E-9BB0-E311-84CA-E0CB4E19F981.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/064760E0-E6AF-E311-9F7A-E0CB4E1A1191.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/064FCD29-6FAF-E311-95AC-20CF3019DEED.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/066A496E-75AF-E311-9F25-E0CB4E55366B.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0670BA8E-3DAF-E311-8851-E0CB4E553676.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06769A75-89AF-E311-B76A-525400413DF2.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0677F2CA-E9AF-E311-8425-525400F9CC35.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/067E6552-E8AF-E311-B0C4-E0CB4E29C4BA.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0694D119-EAAF-E311-9151-20CF305B0508.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06A49FAC-50B0-E311-9810-20CF305616CC.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06B1E2E1-E9AF-E311-BBA8-002590D0AFEE.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06CD1258-28AF-E311-8CC6-0025907B4F3A.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06CE9059-16AF-E311-BA84-90E6BA0D09D2.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06EBB671-1FAF-E311-8ED6-002590D0B046.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0801FCE6-E7AF-E311-B07B-0025907B4F9E.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/080544CD-E7AF-E311-97DC-0025907B4FA4.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/082E7144-70AF-E311-BA05-00261834B57E.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0835011B-7BAF-E311-8843-0025907277BE.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/083D2177-28B0-E311-A2D9-E0CB4E5536F7.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/084AF7FD-F1AE-E311-A89A-90E6BA0D09EC.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0850536A-13B0-E311-ACB5-E0CB4E19F971.root',
                                                              '/store/mc/Summer12_DR53X/TTJets_MSDecays_width_x5_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08744C39-0FAF-E311-B1D4-00259073E33A.root'
                                                              )

widthsm=cms.untracked.vstring(
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0037BFA7-D943-E311-8FA3-00266CF9C018.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/003CFA73-E945-E311-8917-00266CFAE318.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/005B4D11-F543-E311-B865-008CFA010D18.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00817B05-8D45-E311-885C-848F69FD29DF.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00903D2F-3E44-E311-8AAB-00266CF9B274.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/009499C5-CF43-E311-9C8E-7845C4FC3647.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00A00D59-A244-E311-AAA3-00266CFAE810.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00A610BE-4D44-E311-BAAD-848F69FD4667.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00CB37BF-2745-E311-BF45-008CFA008D0C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00E2062C-9E44-E311-9EA5-00266CF253C4.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/00FA0BB4-4845-E311-A885-848F69FD2853.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0263BAB0-3D44-E311-B71F-848F69FD471E.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/027320D2-C344-E311-8132-848F69FD29B8.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02A67701-7E44-E311-8C87-00266CF9B1C4.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02D3D9B0-D044-E311-8AC8-00A0D1EE9424.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02DCABAC-FF43-E311-B56E-7845C4FC3893.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/02F159CE-5B44-E311-BC35-00A0D1EE8C64.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/040CCF1A-8546-E311-A0BA-00266CFAE24C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0421FE95-2744-E311-8A71-7845C4FC370D.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04346E2A-6544-E311-BCEE-7845C4FC3998.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04374E35-4544-E311-87F0-00A0D1EE26D0.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/045E7F4E-8B46-E311-B86E-00266CFAE614.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/0490B36E-8246-E311-A57D-00266CF25218.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04B8AA01-D343-E311-9758-848F69FD4568.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04C19814-6D45-E311-8827-848F69FD4DCC.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/04EBDA94-E143-E311-A627-008CFA00148C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06150CD5-CF44-E311-A1B4-00A0D1EE9424.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06333EA3-C544-E311-9A06-848F69FD294C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/068F590F-C746-E311-BB21-00266CFAE368.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06AF7D34-DC45-E311-95F1-00266CFAE318.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06B16744-CD44-E311-B4AA-00A0D1EE9424.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06C9C029-2744-E311-8D9C-00266CF9BE6C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/06F6BA8B-6B44-E311-9973-848F69FD4E98.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/080500CC-6644-E311-9DDC-00266CF9B970.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/081E5167-0C44-E311-974C-00266CF252D4.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/083E284F-A346-E311-80F8-7845C4FC3602.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08649988-7F44-E311-B940-848F69FD295B.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08823EA7-C846-E311-A508-00266CFAE368.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/088B9F8D-3944-E311-88B0-848F69FD43A0.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/088F00BC-B746-E311-8044-7845C4FC39C8.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08A7D075-0345-E311-A1AA-848F69FD294C.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08B3D2E7-3A47-E311-9EF6-7845C4FC3B00.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08D06BDC-E645-E311-92B5-00A0D1EEF204.root',
'/store/mc/Summer12_DR53X/TTJets_MSDecays_central_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V19-v1/00000/08DB24EA-4D44-E311-8436-00266CF9AEA4.root'
)

#the source and output
process.source = cms.Source("PoolSource",
                            #fileNames = width5
                            fileNames = widthsm
                            )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.out = cms.OutputModule("PoolOutputModule",
                               outputCommands = cms.untracked.vstring('keep *'),
                               fileName = cms.untracked.string("Events.root")
                               )


process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")

process.TFileService = cms.Service("TFileService", fileName = cms.string("DataAnalysis.root"))

process.analysis = cms.EDFilter("OffshellWidthAnalyzer")

process.p = cms.Path( process.analysis )

