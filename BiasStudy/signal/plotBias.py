import ROOT, re, os
from datetime import datetime
if not os.path.exists('BiasPlot'):
  os.makedirs('BiasPlot')
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)
cats = ['ggcat0','ggcat1','ggcat2','ggcat3','vbfcat0','vbfcat1']

parser = argparse.ArgumentParser(
    "Bias Study for LFV H analysis")
parser.add_argument(
    "-m",
    action="store",
    default=125,
    type=int,
    help="mass point")

args = parser.parse_args()

for cat in cats:
  outfile = open(cat+'BiasStudy.txt','a', buffering=0) 
  outfile.write("%s\n"%str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
  for sigtype in ['cb', 'gaus']:
    altsigtype = 'cb' if sigtype=='gaus' else 'gaus'
    print "Scanning fitDiagnosticsGen"+sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)+".root"
    file_ = ROOT.TFile("fitDiagnosticsGen"+sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)+".root")
    tree = file_.Get("tree_fit_sb")
    if not tree: 
      print "Fit Failed: Gen"+sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)
      outfile.write(sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)+" is missing\n")
      continue
    tree.Draw("(r-0.01)/(0.5*(rHiErr+rLoErr))>>h(100,-5,5)")
    h = ROOT.gPad.GetPrimitive("h")
    h.Fit("gaus")
    try:
      h_mean = h.GetFunction("gaus").GetParameter(1)
      h_sigma = h.GetFunction("gaus").GetParameter(2)
    except:
      h_mean = h.GetMean()
      h_sigma = h.GetStdDev()
    h.SetTitle(sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)+";Pull;");
    h.SetName(sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m))
    ROOT.gPad.SaveAs('BiasPlot/'+sigtype+"Fit"+altsigtype+'_'+cat+'_'+str(args.m)+'.png')
    print "Mean of bias of "+cat+" for sig "+altsigtype+" generated with sig "+sigtype, h_mean
    print "Standard Deviation of bias", h_sigma
    outfile.write(cat + " " + sigtype + " " + altsigtype +" "+ str(round(h_mean*100,3)) + " " + str(round(h_sigma,3)) + "\n")
    file_.Close()
  outfile.close()
