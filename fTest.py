import ROOT
import signalModel
ROOT.gROOT.SetBatch(True)
pLUT2 = {'dm':{mode:{i:[] for i in range(4)} for mode in ['qqH','ggH']}, 'sigma':{mode:{i:[] for i in range(4)}for  mode in ['qqH','ggH']}}
pLUT3 = {'dm':{mode:{i:[] for i in range(4)} for mode in ['qqH','ggH']}, 'sigma':{mode:{i:[] for i in range(4)}for  mode in ['qqH','ggH']}}

pLUT2['dm']['ggH'][0] = [-.5,-1,1]
pLUT2['dm']['ggH'][2] = [-1,-2,2] 
pLUT2['dm']['ggH'][1] = [-5,-10,10]
pLUT2['dm']['ggH'][3] = [0.0,-5,5]

pLUT2['sigma']['ggH'][0] = [1,0,4]
pLUT2['sigma']['ggH'][2] = [2,0,4] 
pLUT2['sigma']['ggH'][1] = [5,0,10]
pLUT2['sigma']['ggH'][3] = [2,0.5,10.0]

pLUT2['dm']['qqH'][0] = [-.5,-1,1]
pLUT2['dm']['qqH'][2] = [-1,-2,2] 
pLUT2['dm']['qqH'][1] = [-5,-10,10]
pLUT2['dm']['qqH'][3] = [0.0,-5,5]

pLUT2['sigma']['qqH'][0] = [1,0,4]
pLUT2['sigma']['qqH'][2] = [2,0,4] 
pLUT2['sigma']['qqH'][1] = [5,0,10]
pLUT2['sigma']['qqH'][3] = [2,0.5,10.0]

pLUT3['dm']['ggH'][0] = [-.5,-1,1]
pLUT3['dm']['ggH'][1] = [-1,-2,2] 
pLUT3['dm']['ggH'][2] = [-5,-10,10]
pLUT3['dm']['ggH'][3] = [0.0,-5,5]

pLUT3['sigma']['ggH'][0] = [1,0,4]
pLUT3['sigma']['ggH'][1] = [2,0,4] 
pLUT3['sigma']['ggH'][2] = [5,0,10]
pLUT3['sigma']['ggH'][3] = [2,0.5,10.0]

pLUT3['dm']['qqH'][0] = [-.5,-1,1]
pLUT3['dm']['qqH'][1] = [-1,-2,2] 
pLUT3['dm']['qqH'][2] = [-5,-10,10]
pLUT3['dm']['qqH'][3] = [0.0,-5,5]

pLUT3['sigma']['qqH'][0] = [1,0,4]
pLUT3['sigma']['qqH'][1] = [2,0,4] 
pLUT3['sigma']['qqH'][2] = [5,0,10]
pLUT3['sigma']['qqH'][3] = [2,0.5,10.0]


def fTest(ggWS, vbfWS, cat, proc, masspt, bins, bin_=True):
  #Fit signal
  effl, effh = bins[0], bins[1]
  finalOrder = -1
  inWS = ggWS if proc=='ggH' else vbfWS
  mass_sig = inWS.var("CMS_emu_Mass")
  mass_sig.setBins(360)
  mass_sig.setRange("higgsRange",masspt-15.,masspt+10.)
  dataFull = inWS.data("norm_range%i"%effl).Clone()
  if bin_:
    dh = ROOT.RooDataHist("data_{}_{}".format(cat,proc),"data_{}_{}".format(cat,proc), ROOT.RooArgSet(mass_sig), dataFull)
    for i in range(effl+1, effh):
      dh.add(inWS.data("norm_range%i"%i))
  else:
    dh = dataFull
    for i in range(effl+1, effh):
      dh.append(inWS.data("norm_range%i"%i))
#  dh = dh.binnedClone()

  dh.SetName("data_{}_{}".format(cat,proc))
  prevNll = 999
  for norder in range(1,5):
    sigfrac, dm_dcb, sigma_nom_dcb, subpdf = [], [], [], []
    gaus_List, frac_List = ROOT.RooArgList(), ROOT.RooArgList()
    print(proc)
    for i in range(norder):
      dm_dcb.append(ROOT.RooRealVar("{}_{}_mean_gaus_nom_order{}".format(cat,proc,i), "{}_{}_mean_gaus_nom_order{}".format(cat,proc,i), masspt+pLUT['dm'][proc][i][0], masspt+pLUT['dm'][proc][i][1], masspt+pLUT['dm'][proc][i][2])) #-0.1,-1,1
    
      sigma_nom_dcb.append(ROOT.RooRealVar("{}_{}_sigma_gaus_nom_order{}".format(cat,proc,i), "{}_{}_sigma_gaus_nom_order{}".format(cat,proc,i), pLUT['sigma'][proc][i][0], pLUT['sigma'][proc][i][1], pLUT['sigma'][proc][i][2])) #1.5, .8, 2

      subpdf.append(ROOT.RooGaussian("{}_{}_pdf_order{}".format(cat,proc,i), "{}_{}_pdf_order{}".format(cat,proc,i), mass_sig, dm_dcb[-1], sigma_nom_dcb[-1]))
      gaus_List.add(subpdf[-1])
      if i!=norder-1:
        sigfrac.append(ROOT.RooRealVar("{}_{}_sigfrac_order{}".format(cat,proc,i),"{}_{}_sigfrac_order{}".format(cat,proc,i),0.5+i*0.1,0.,1.))
        frac_List.add(sigfrac[-1])
    pdf = ROOT.RooAddPdf("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), gaus_List, frac_List, True)
    fitResult = pdf.fitTo(dh, ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Minimizer("Minuit2","minimize"))
    signalModel.plot_model(cat+'_fTest_'+str(norder), masspt, mass_sig, dh, pdf, fitResult, proc)

    thisNll = fitResult.minNll() 
    chi2 = 2.*(prevNll-thisNll)
    prob = ROOT.TMath.Prob(chi2,1)
    print(prob, thisNll)
    if prob > 0.05: 
      finalOrder = norder-1
      break
    prevNll = thisNll
  print('final Order is '+str(finalOrder))
  return finalOrder, prevNll, thisNll, prob
