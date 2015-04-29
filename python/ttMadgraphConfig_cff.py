import FWCore.ParameterSet.Config as cms

from Configuration.Generator.PythiaUEZ2starSettings_cfi    import pythiaUESettingsBlock as pythiaUESettings_Z2starBlock
from Configuration.Generator.PythiaUEZ2starLEPSettings_cfi import pythiaUESettingsBlock as pythiaUESettings_Z2starLEPBlock
from Configuration.Generator.PythiaUEP11Settings_cfi       import pythiaUESettingsBlock as pythiaUESettings_P11Block


def configureTTGenerator(process,tune):

  pythiaUESettingsBlock=None

  #UE
  if 'Z2star' in tune:
    if 'LEP' in tune:
      pythiaUESettingsBlock=pythiaUESettings_Z2starLEPBlock.clone()
    else:
      pythiaUESettingsBlock=pythiaUESettings_Z2starBlock.clone()
  if 'P11' in tune:
    pythiaUESettingsBlock=pythiaUESettings_P11Block.clone()
  if 'P12' in tune:
    pythiaUESettingsBlock=cms.PSet( pythiaUESettings = cms.vstring('MSTU(21)=1     ! Check on possible errors during program execution', 
                                                                   'MSTJ(22)=2     ! Decay those unstable particles', 
                                                                   'PARJ(71)=10 .  ! for which ctau  10 mm',
                                                                   'MSTP(51) =      10042 ! PDF set',
                                                                   'MSTP(52) =      2 ! PDF set internal (=1) or pdflib (=2)',
                                                                   'MSTP( 3) =      1 ! INT switch for choice of LambdaQCD',
                                                                   'MSTU(112)=      5 ! INT n(flavors) for LambdaQCD',
                                                                   'PARU(112)= 0.1600 ! INT LambdaQCD',
                                                                   'PARP( 1) = 0.1600 ! ME/UE LambdaQCD',
                                                                   'PARJ(81) = 0.2600 ! FSR LambdaQCD (inside resonance decays)',
                                                                   'PARP(72) = 0.2600 ! IFSR LambdaQCD (outside resonance decays',
                                                                   'PARP(61) = 0.2600 ! ISR LambdaQCD',
                                                                   'MSTP(64) =      2 ! ISR alphaS type',
                                                                   'PARP(64) = 1.0000 ! ISR renormalization scale prefactor',
                                                                   'MSTP(67) =      2 ! ISR coherence option for 1st emission',
                                                                   'MSTP(68) =      3 ! ISR phase space choice & ME corrections',
                                                                   'PARP(67) = 1.0000 ! ISR Q2max factor',
                                                                   'MSTP(72) =      2 ! IFSR scheme for non-decay FSR',
                                                                   'PARP(71) = 1.0000 ! IFSR Q2max factor in non-s-channel procs',
                                                                   'MSTP(70) =      0 ! ISR IR regularization scheme',
                                                                   'PARP(62) = 1.5000 ! ISR IR cutoff',
                                                                   'PARJ(82) = 1.0000 ! FSR IR cutoff',
                                                                   'MSTP(33) =      0 ! "K" switch for K-factor on/off & type',
                                                                   'MSTP(81) =     21 ! UE model',
                                                                   'PARP(82) = 2.6500 ! UE IR cutoff at reference ecm',
                                                                   'PARP(89) = 7000.0 ! UE IR cutoff reference ecm',
                                                                   'PARP(90) = 0.2400 ! UE IR cutoff ecm scaling power',
                                                                   'MSTP(82) =      3 ! UE hadron transverse mass distribution',
                                                                   'MSTP(88) =      0 ! BR composite scheme',
                                                                   'MSTP(89) =      0 ! BR color scheme',
                                                                   'PARP(79) = 2.0000 ! BR composite x enhancement',
                                                                   'PARP(80) = 0.0150 ! BR breakup suppression',
                                                                   'MSTP(91) =      1 ! BR primordial kT distribution',
                                                                   'PARP(91) = 1.0000 ! BR primordial kT width <|kT|>',
                                                                   'PARP(93) =      10.0000 ! BR primordial kT UV cutoff',
                                                                   'MSTP(95) =      8 ! FSI color (re-)connection model',
                                                                   'PARP(78) = 0.0350 ! FSI color reconnection strength',
                                                                   'PARP(77) = 1.0000 ! FSI color reco high-pT damping strength',
                                                                   'MSTJ(11) =      5 ! HAD choice of fragmentation function(s)',
                                                                   'PARJ( 1) = 0.0850 ! HAD diquark suppression',
                                                                   'PARJ( 2) = 0.2000 ! HAD strangeness suppression',
                                                                   'PARJ( 3) = 0.9200 ! HAD strange diquark suppression',
                                                                   'PARJ( 4) = 0.0430 ! HAD vector diquark suppression',
                                                                   'PARJ( 5) = 0.5000 ! HAD P(popcorn)',
                                                                   'PARJ( 6) = 1.0000 ! HAD extra popcorn B(s)-M-B(s) supp',
                                                                   'PARJ( 7) = 1.0000 ! HAD extra popcorn B-M(s)-B supp',
                                                                   'PARJ(11) = 0.3500 ! HAD P(vector meson), u and d only',
                                                                   'PARJ(12) = 0.4000 ! HAD P(vector meson), contains s',
                                                                   'PARJ(13) = 0.5400 ! HAD P(vector meson), heavy quarks',
                                                                   'PARJ(21) = 0.3300 ! HAD fragmentation pT',
                                                                   'PARJ(25) = 0.7000 ! HAD eta0 suppression',
                                                                   'PARJ(26) = 0.1350 ! HAD eta0prim suppression',
                                                                   'PARJ(41) = 0.4500 ! HAD string parameter a(Meson)',
                                                                   'PARJ(42) = 1.0000 ! HAD string parameter b',
                                                                   'PARJ(45) = 0.8600 ! HAD string a(Baryon)-a(Meson)',
                                                                   'PARJ(46) = 1.0000 ! HAD Lund(=0)-Bowler(=1) rQ (rc)',
                                                                   'PARJ(47) = 1.0000 ! HAD Lund(=0)-Bowler(=1) rb')
                                    )

  #fragmentation specific (use with Z2lep with care)                             
  if 'peterson' in tune:
    pythiaUESettingsBlock.pythiaUESettings.push_back('MSTJ(11)=3')
  if 'lund' in tune:
    pythiaUESettingsBlock.pythiaUESettings.push_back('MSTJ(11)=1')
  if 'hard' in tune:
    pythiaUESettingsBlock.pythiaUESettings.push_back('PARJ(41)  = 0.225 ! a in FF')
    pythiaUESettingsBlock.pythiaUESettings.push_back('PARJ(42)  = 1.5   ! b in FF')
  if 'soft' in tune:
    pythiaUESettingsBlock.pythiaUESettings.push_back('PARJ(41)  = 0.9   ! a in FF')
    pythiaUESettingsBlock.pythiaUESettings.push_back('PARJ(42)  = 0.5   ! b in FF')
 
  
  return pythiaUESettingsBlock
  
 
