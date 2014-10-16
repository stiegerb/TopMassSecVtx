import ROOT as rt

# CMS_lumi
#   Initiated by: Gautier Hamel de Monchenault (Saclay)
#   Translated in Python by: Joshua Hardenbrook (Princeton)
#

CMS_lumi_cmsText     = "CMS";
CMS_lumi_cmsTextFont   = 61  
CMS_lumi_cmsTextSize      = 0.6
CMS_lumi_cmsTextOffset    = 0.1

CMS_lumi_writeExtraText = True
CMS_lumi_extraText   = "work in progress"
CMS_lumi_writeExtraTextFont = 52
CMS_lumi_writeExtraTextSize = 0.5
CMS_lumi_lumiTextSize     = 0.6
CMS_lumi_lumiTextOffset   = 0.2
CMS_lumi_relPosX    = 0.045
CMS_lumi_relPosY    = 0.035
CMS_lumi_relExtraDY = 1.2

CMS_lumi_intlumi13TeV = "20.1 fb^{-1}"
CMS_lumi_intlumi8TeV  = "19.7 fb^{-1}" 
CMS_lumi_intlumi7TeV  = "5.1 fb^{-1}"

CMS_lumi_drawLogo      = False

def CMS_lumi(pad,  iPeriod,  iPosX ):
    outOfFrame    = False
    if(iPosX/10==0 ): outOfFrame = True

    alignY_=3
    alignX_=2
    if( iPosX/10==0 ): alignX_=1
    if( iPosX==0    ): alignY_=1
    if( iPosX/10==1 ): alignX_=1
    if( iPosX/10==2 ): alignX_=2
    if( iPosX/10==3 ): alignX_=3
    align_ = 10*alignX_ + alignY_

    H = pad.GetWh()
    W = pad.GetWw()
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()
    e = 0.025

    pad.cd()

    lumiText = ""
    if( iPeriod==1 ):
        lumiText += CMS_lumi_intlumi7TeV
        lumiText += " (7 TeV)"
    elif ( iPeriod==2 ):
        lumiText += CMS_lumi_intlumi8TeV
        lumiText += " (8 TeV)"

    elif( iPeriod==3 ):      
        lumiText = CMS_lumi_intlumi8TeV 
        lumiText += " (8 TeV)"
        lumiText += " + "
        lumiText += CMS_lumi_intlumi7TeV
        lumiText += " (7 TeV)"
    elif ( iPeriod==4 ):
        lumiText += CMS_lumi_intlumi13TeV
        lumiText += " (13 TeV)"
    elif ( iPeriod==7 ):
        if( outOfFrame ):lumiText += "#scale[0.85]{"
        lumiText += CMS_lumi_intlumi13TeV 
        lumiText += " (13 TeV)"
        lumiText += " + "
        lumiText += CMS_lumi_intlumi8TeV 
        lumiText += " (8 TeV)"
        lumiText += " + "
        lumiText += CMS_lumi_intlumi7TeV
        lumiText += " (7 TeV)"
        if( outOfFrame): lumiText += "}"
    elif ( iPeriod==12 ):
        lumiText += "8 TeV"
            
    print lumiText

    latex = rt.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(rt.kBlack)    
        
    latex.SetTextFont(42)
    latex.SetTextAlign(31) 
    latex.SetTextSize(CMS_lumi_lumiTextSize*t)    

    latex.DrawLatex(1-r,1-t+CMS_lumi_lumiTextOffset*t,lumiText)

    if( outOfFrame ):
        latex.SetTextFont(CMS_lumi_cmsTextFont)
        latex.SetTextAlign(11) 
        latex.SetTextSize(CMS_lumi_cmsTextSize*t)    
        latex.DrawLatex(l,1-t+CMS_lumi_lumiTextOffset*t,CMS_lumi_cmsText)
  
    pad.cd()

    posX_ = 0
    if( iPosX%10<=1 ):
        posX_ =   l + CMS_lumi_relPosX*(1-l-r)
    elif( iPosX%10==2 ):
        posX_ =  l + 0.5*(1-l-r)
    elif( iPosX%10==3 ):
        posX_ =  1-r - CMS_lumi_relPosX*(1-l-r)

    posY_ = 1-t - CMS_lumi_relPosY*(1-t-b)

    if( not outOfFrame ):
        if( CMS_lumi_drawLogo ):
            posX_ =   l + 0.045*(1-l-r)*W/H
            posY_ = 1-t - 0.045*(1-t-b)
            xl_0 = posX_
            yl_0 = posY_ - 0.15
            xl_1 = posX_ + 0.15*H/W
            yl_1 = posY_
            CMS_logo = rt.TASImage("CMS-BW-label.png")
            pad_logo =  rt.TPad("logo","logo", xl_0, yl_0, xl_1, yl_1 )
            pad_logo.Draw()
            pad_logo.cd()
            CMS_logo.Draw("X")
            pad_logo.Modified()
            pad.cd()          
        else:
            latex.SetTextFont(CMS_lumi_cmsTextFont)
            latex.SetTextSize(CMS_lumi_cmsTextSize*t)
            latex.SetTextAlign(align_)
            latex.DrawLatex(posX_, posY_, CMS_lumi_cmsText)
            if( CMS_lumi_writeExtraText ) :
                latex.SetTextFont(CMS_lumi_writeExtraTextFont)
                latex.SetTextAlign(align_)
                latex.SetTextSize(CMS_lumi_writeExtraTextSize*t)
                #latex.DrawLatex(posX_, posY_- CMS_lumi_relExtraDY*CMS_lumi_cmsTextSize*t, CMS_lumi_extraText)
                latex.DrawLatex(posX_*1.2, posY_, CMS_lumi_extraText)
    elif( CMS_lumi_writeExtraText ):
        if( iPosX==0):
            posX_ =   l +  CMS_lumi_relPosX*(1-l-r)
            posY_ =   1-t+CMS_lumi_lumiTextOffset*t

        latex.SetTextFont(CMS_lumi_writeExtraTextFont)
        latex.SetTextSize(CMS_lumi_writeExtraTextSize*t)
        latex.SetTextAlign(align_)
        latex.DrawLatex(posX_*1.2, posY_, CMS_lumi_extraText)      

    pad.Update()
