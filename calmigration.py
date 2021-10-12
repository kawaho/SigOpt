def make2side(sysname):
  for key, value in sysname.items():
    if value['Up'] > 1 and value['Down'] > 1:
      if value['Down'] > value['Up']:
        sysname[key]['Up'] = round(1./value['Down'], 3)
      else:
        sysname[key]['Down'] = round(1./value['Up'], 3)
    elif value['Up'] < 1 and value['Down'] < 1:
      if value['Down'] > value['Up']:
        sysname[key]['Down'] = round(1./value['Up'], 3)
      else:
        sysname[key]['Up'] = round(1./value['Down'], 3)

def calmigration(df):
  #list of all systematics
  jetUnc = ['jesAbsolute', 'jesBBEC1', 'jesFlavorQCD', 'jesEC2', 'jesHF', 'jesRelativeBal']
  jetyearUnc = sum([[f'jer_{year}', f'jesAbsolute_{year}', f'jesBBEC1_{year}', f'jesEC2_{year}', f'jesHF_{year}', f'jesRelativeSample_{year}', f'UnclusteredEn_{year}'] for year in ['2017', '2018', '2016preVFP', '2016postVFP']], [])
  sfUnc = sum([[f'pu_{year}', f'bTag_{year}'] for year in ['2017', '2018', '2016preVFP', '2016postVFP']], [])
  sfUnc += ['pf_2016preVFP', 'pf_2016postVFP', 'pf_2017']
  leptonUnc = ['me']#['ees', 'eer', 'me']
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
