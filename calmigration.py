def smallUnc(val, name=''):
  #print name, val, round(val,3), abs(round(val,3)-1.)
  if round(abs(val-1.),3)<=0.001:
    #print 'small'
    return True
  else:
    return False

def make2side(sysname):
  for key, value in sysname.items():
    if value['Up'] > 1 and value['Down'] > 1:
      #print(key+' is one-sided >1', value['Up'], value['Down'])
      if value['Down'] > value['Up']:
        sysname[key]['Up'] = 1./value['Down']
      else:
        sysname[key]['Down'] = 1./value['Up']
    elif value['Up'] < 1 and value['Down'] < 1:
      #print(key+' is one-sided <1', value['Up'], value['Down'])
      if value['Down'] > value['Up']:
        sysname[key]['Down'] = 1./value['Up']
      else:
        sysname[key]['Up'] = 1./value['Down']
    #print(sysname[key]['Up'], sysname[key]['Down'])
#    if smallUnc(value['Up']) and smallUnc(value['Down']):
#      #print('smallUnc', key)
#      sysname[key]['Up'], sysname[key]['Down'] = -1, -1
#    if smallUnc(value['Up']):
#      sysname[key]['Up'] = 1
#    if smallUnc(value['Down']):
#      sysname[key]['Down'] = 1

def calmigration(df):
  #list of all systematics
  jetUnc = ['jesAbsolute', 'jesBBEC1', 'jesFlavorQCD', 'jesEC2', 'jesHF', 'jesRelativeBal', 'UnclusteredEn']
  jetyearUnc = sum([['jer_'+year, 'jesAbsolute_'+year, 'jesBBEC1_'+year, 'jesEC2_'+year, 'jesHF_'+year, 'jesRelativeSample_'+year] for year in ['2017', '2018', '2016']], [])
  sfUnc = sum([['pu_'+year, 'bTag_'+year] for year in ['2017', '2018', '2016']], [])
  sfUnc += ['pf_2016', 'pf_2017', 'mID', 'mIso', 'mTrg', 'eReco', 'eID', 'eIso', 'eTrig']
  leptonUnc = ['me', 'ess']
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
     sysname[s][UpDown] = nevents/nevents_nom

  #make sure systematics are two-sided
  make2side(sysname) 
  return sysname
