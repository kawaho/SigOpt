def smallUnc(val):
  if abs(val-1.)<0.001:
    return True
  else:
    return False

def make2side(sysname):
  for key, value in sysname.items():
    if value['Up'] > 1 and value['Down'] > 1:
      #print(key+' is one-sided >1', value['Up'], value['Down'])
      if value['Down'] > value['Up']:
        sysname[key]['Up'] = 1#round(1./value['Down'], 3)
      else:
        sysname[key]['Down'] = 1#round(1./value['Up'], 3)
    elif value['Up'] < 1 and value['Down'] < 1:
      #print(key+' is one-sided <1', value['Up'], value['Down'])
      if value['Down'] > value['Up']:
        sysname[key]['Down'] = 1#round(1./value['Up'], 3)
      else:
        sysname[key]['Up'] = 1#round(1./value['Down'], 3)
#    if smallUnc(value['Up']) and smallUnc(value['Down']):
#      sysname[key]['Up'], sysname[key]['Down'] = -1, -1
#    if smallUnc(value['Up']):
#      sysname[key]['Up'] = 1
#    if smallUnc(value['Down']):
#      sysname[key]['Down'] = 1

def calmigration(df):
  #list of all systematics
  jetUnc = ['jesAbsolute', 'jesBBEC1', 'jesFlavorQCD', 'jesEC2', 'jesHF', 'jesRelativeBal', 'UnclusteredEn']
  jetyearUnc = sum([['jer_'+year, 'jesAbsolute_'+year, 'jesBBEC1_'+year, 'jesEC2_'+year, 'jesHF_'+year, 'jesRelativeSample_'+year] for year in ['2017', '2018', '2016']], [])
  sfUnc = sum([['pu_'+year, 'bTag_'+year] for year in ['2017', '2018', '2016preVFP', '2016postVFP']], [])
  sfUnc += ['pf_2016preVFP', 'pf_2016postVFP', 'pf_2017', 'mID', 'mIso', 'mTrg', 'eReco', 'eID']
  leptonUnc = ['me', 'ees', 'eer']
  sys = jetUnc+jetyearUnc+sfUnc+leptonUnc

  #Get nomial weight
  nevents_nom = df['weight']
  #return ratio of weight/nom weight in form of {'sth':{'Up':, 'Down':}, ....}
  sysname = {}

  #Loop through systematic weight
  for s in sys:
   sysname[s] = {'Up':-1, 'Down':-1}
   for UpDown in ['Up', 'Down']:
     nevents = df['weight_'+s+'_'+UpDown]
     sysname[s][UpDown] = round(nevents/nevents_nom, 3)

  #make sure systematics are two-sided
  make2side(sysname) 
  return sysname
