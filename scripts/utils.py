import array
import math
import os
import numpy as np
import sys
import ROOT

def quantiles(histo = None) :
    #areaFractions = np.arange(0.025,0.95,0.025)
    areaFractions = np.arange(0.05,1,0.05)
    probSum = array.array('d', areaFractions)
    q = array.array('d', [0.0]*len(probSum))
    histo.GetQuantiles(len(probSum), q, probSum)
    return q

def rebin(histo,bin):
        histo.Rebin(len(bin)-1,h+'_bin',array.array('d',bin))
        return hist


