import pandas as pd
import numpy as np
from functools import reduce
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pylab as pl

### ALL FUNCTIONS
def combine(df_dict):
	# Combines dataframes
	# Input: Dictionary of {name:pd df with data}
	# Output: Combined pd df

    df_list = []
    for df in df_dict.values():
        df_list.append(df)
    final_df = pd.concat(df_list, sort = False)
    return final_df

def lg_yr_filter(data_df,lg_list,gender=["M","W"],minYr=1000,maxYr=3000,top_leagues=None):
    # Places data matching certain criteria into dict of {name/category : pd df with data}
    # Inputs (1): data_df = pd df of data, 
    # 	lg_list = list of league 3-tuples of format (league name, year, gender)
    # Inputs (2): Criteria includes:
    ###>>> gender: Which genders to include, default both "M" and "W"
    ###>>> minYr, maxYr: Which year time frame to include, default range 1000-3000
    ###>>> top_leagues: Which leagues to include, if None then set to all leagues in function
    outdict = {}
    if(not top_leagues):
        top_leagues = [val[0] for val in lg_list]
        
    for lg,yr,gen in lg_list:
        if(lg in top_leagues and gen in gender and yr >= minYr and yr <= maxYr):
            outdict[(lg,yr)] = data_df[(data_df["Gen+Leag"]==lg) & (data_df["Season"]==yr)]
        
    return outdict

def null_count(df_dict):
	# Calculates % missing for every attribute across every category
	# Input: Dictionary of {name/category : pd df with data}
	# Output: pd df of nulls % per name/category
    return_list = []
    for name, df in df_dict.items():        
        df = pd.DataFrame(df.isnull().sum()/len(df), columns = [name])
        df.reset_index(inplace=True)
        return_list.append(df)
    null_df = reduce(lambda  left,right: pd.merge(left,right,on=['index'], how='outer'), return_list).fillna(1.0)
    return null_df

def null_heatmap(null_df):
	# Heat map visualization of % missing by category
	# Input: pd df of nulls % per name/category
    null_df = null_df.set_index('index')
    null_df = null_df[null_df.columns].astype(float)
    null_df = 1 - null_df
    
    fig, ax = plt.subplots(figsize=(15,40))
    sns.heatmap(null_df, linewidths=.5, annot = True)
    plt.show()

def top_attributes(null_df):
	# Returns list of top attributes
	# Input: pd df of nulls % per name/category
	# Output: list of top attributes
    null_df = null_df.set_index('index')
    null_df = null_df[null_df.columns].astype(float)
    attribute_list = []
    null_df['total'] = null_df.apply(lambda row: sum(row), axis=1)
    for index, row in null_df.iterrows():
        if nulls.loc[ index, 'total'] <= 5:
            attribute_list.append(index)

    return attribute_list

def get_nulls_under(null_df,threshold=0.2):
	# Get df of features with average null % less than threshold(default 20%)
	# Inputs: pd df of nulls % per name/category, threshold
	# Output: filtered pd df of format (rows = categories, cols = features)
    null_df["null_avg"] = null_df.mean(axis=1)
    null_df = null_df.sort_values("null_avg").reset_index(drop=True)
    outdf = null_df[null_df["null_avg"]<=threshold].set_index("index")
    return outdf.T



### Read in data from csv's
australia = pd.read_csv("australia_scraped.csv", delimiter = '|')
belgium = pd.read_csv("belgium_scraped.csv", delimiter = '|')
dutch = pd.read_csv("dutch_scraped.csv", delimiter = '|')
korea = pd.read_csv("korea_scraped.csv", delimiter = '|')
EFL_d2 = pd.read_csv("men's efl_div2.csv")
ligamx = pd.read_csv("men's liga mx.csv")
mls = pd.read_csv("men's mls.csv")
russia = pd.read_csv("russia_scraped.csv", delimiter = '|')
sl = pd.read_csv("Super_League.csv")

ligue = pd.read_csv("Ligue1.csv")
pl = pd.read_csv("Premier_League.csv")
bundesliga = pd.read_csv("Bundesliga.csv")
laliga = pd.read_csv("Laliga.csv")
serieA = pd.read_csv("SerieA.csv")

m_euros = pd.read_csv("men's euros.csv")
m_wc = pd.read_csv("men's wc.csv")

nwsl = pd.read_csv("NWSL.csv")
w_cl = pd.read_csv("UEFA_womens_CL.csv")
w_euros = pd.read_csv("UEFA_womens_Euro.csv")
w_wc = pd.read_csv("FIFA_Womens_WC.csv")



### Combine into one df + clean
df_dictLg = {'australia': australia, 
   "belgium": belgium,
   "dutch": dutch, 
   "korea": korea, 
   "russia": russia,
   "EFL_d2": EFL_d2, 
   "m_euros": m_euros,
   "ligamx": ligamx, "mls": mls, "m_wc": m_wc, 
   "ligue": ligue, "pl": pl, "bundesliga":bundesliga, "laliga": laliga,"serieA":serieA,
   "russia":russia, "super": sl, 
   "nwsl": nwsl, "womens cl": w_cl, "womens euros": w_euros, "w_wc":w_wc}

combined = combine(df_dictLg)

combined = combined[combined["('Playing Time', 'Min')"]>90.0]
combined = combined[combined["('Playing Time', 'MP')"]>2]
combined = combined[~combined['Pos'].str.contains("GK",na=False)]

combined['Season'][combined["Season"].str.contains("-",na=False)] = combined['Season'][combined["Season"].str.contains("-",na=False)].str.slice(0,4)
combined["Season"] = combined['Season'].astype(int)

combined['Gen+Leag'] = combined['Gender']+" "+combined['League']

combined["DEF"] = 0
combined["DEF"][combined["Pos"].str.contains("DF",na=False)] = 1
combined["MID"] = 0
combined["MID"][combined["Pos"].str.contains("MF",na=False)] = 1
combined["ATT"] = 0
combined["ATT"][combined["Pos"].str.contains("FW",na=False)] = 1

combined = combined.drop(["Rk","Unnamed: 0"],axis=1)




### Get 3-tuple list of leagues, format (league,year,gender)
lglist_df = combined[["Gen+Leag","Season","Gender",
	"ATT","MID","DEF"]].groupby(['Gen+Leag',"Season","Gender"]).sum()
lglist = lglist_df.index.values.tolist()
print("Prelim Data Setup Complete","\n")




### Find key attributes of Men's data
top_leaguesM = ['M La Liga Men','M Ligue 1 Men','M Premier League Men','M Serie A Men','M Bundesliga Men']
use_leaguesM2 = ['M A-League',
 'M Belgian First Division A',
 'M Dutch Eredivise',
 'M EFL Championship',
 'M Liga MX',
 'M MLS',
 'M Russian Premier League']
use_leaguesM2 = top_leaguesM+use_leaguesM2
intlM = ['M Euros','M FIFA World Cup']

#> Build dicts
lgyr_dict_try_men =  lg_yr_filter(combined,lglist,"M",minYr=1999,top_leagues=use_leaguesM2)
dict_intl_men = lg_yr_filter(combined,lglist,"M",minYr=2016,top_leagues=intlM)
dict_klg_men = lg_yr_filter(combined,lglist,"M",minYr=2016,top_leagues=['M K League Classic'])

lgyr_dict_try_men.update(dict_intl_men)
lgyr_dict_try_men.update(dict_klg_men)

#> Check nulls
nulls_try_men = null_count(lgyr_dict_try_men)
nullAttr_try_men = get_nulls_under(nulls_try_men,threshold=0.5)

#> Pull "Key Attributes" -> less than 50% null, remove duplicates
key_attr1 = nullAttr_try_men.columns.tolist()
rmv1 = ["90s","('Standard', 'PKatt')","('Standard', 'Gls')","('Standard', 'PK')","Ast","Gender","League"]

start = ["Player","Pos","Squad","Gender","League","Gen+Leag","Season","Age","Born","Nation",
         "ATT","MID","DEF",
         "('Playing Time', 'MP')", "('Playing Time', 'Min')", "('Playing Time', 'Starts')"]

key_attr = [attr for attr in key_attr1 if attr not in (rmv1) and attr not in (start)]
key_attr.sort()
key_attrM = start+key_attr




### Find key attributes of Women's data
use_leaguesW = ['W FIFA World Cup', 'W UEFA Champions League']

#> Build dicts
lgyr_dict_try_women = lg_yr_filter(combined,lglist,"W",minYr=1000,top_leagues=use_leaguesW)

dict_eur_women = lg_yr_filter(combined,lglist,"W",minYr=2017,top_leagues=['W UEFA Euro'])
dict_nwsl_women = lg_yr_filter(combined,lglist,"W",minYr=1000,maxYr=2016,top_leagues=['W NWSL'])
dict_wsupl_women = lg_yr_filter(combined,lglist,"W",minYr=1000,maxYr=2018,top_leagues=['W Super League'])
lgyr_dict_try_women.update(dict_eur_women)
lgyr_dict_try_women.update(dict_nwsl_women)
lgyr_dict_try_women.update(dict_wsupl_women)

#> Check nulls
nulls_try_women = null_count(lgyr_dict_try_women)
nullAttr_try_women = get_nulls_under(nulls_try_women,threshold=0.5)

#> Pull "Key Attributes" -> less than 50% null, remove duplicates
key_attr2 = nullAttr_try_women.columns.tolist()
rmv2 = ["90s","('Standard', 'PKatt')","('Standard', 'Gls')","('Standard', 'PK')",
       "Ast","Gender","League","('Performance', '2CrdY')"]

start = ["Player","Pos","Squad","Gender","League","Gen+Leag","Season","Age","Born","Nation",
         "ATT","MID","DEF",
         "('Playing Time', 'MP')", "('Playing Time', 'Min')", "('Playing Time', 'Starts')"]

key_attr = [attr for attr in key_attr2 if attr not in (rmv2) and attr not in (start)]
key_attr.sort()
key_attrW = start+key_attr




### Combine attributes for final df
#> Check non-common attributes
print("Key Attr-->","W:",len(key_attrW),"M:",len(key_attrM))
print()
print("W Only:",list(set(key_attrW)-set(key_attrM)))
print("M Only:",list(set(key_attrM)-set(key_attrW)))
print()

#> Create combined attribute set
key_attr3 = list( set(key_attrW).union(set(key_attrM)) )

start = ["Player","Pos","Squad","Gender","League","Gen+Leag","Season","Age","Born","Nation",
         "ATT","MID","DEF",
         "('Playing Time', 'MP')", "('Playing Time', 'Min')", "('Playing Time', 'Starts')"]

key_attr = [attr for attr in key_attr3 if attr not in (start)]
key_attr.sort()
key_attrTot = start+key_attr

###**********************************************************
### Build final df
men_filtered1 = combine(lgyr_dict_try_men).reset_index(drop=True)
men_filteredT = men_filtered1[key_attrTot]

women_filtered1 = combine(lgyr_dict_try_women).reset_index(drop=True)
women_filteredT = women_filtered1[key_attrTot]

combined_new = pd.concat([women_filteredT,men_filteredT])
print("New df built","\n")

#> Check Nulls
nulls_combin = null_count({"M":men_filteredT,"W":women_filteredT})
#print(nulls_combin)

#> Write final csvs
write=False
if(write):
	#men_filteredT.set_index("Player").to_csv("01 men_filtered.csv")
	#women_filteredT.set_index("Player").to_csv("01 women_filtered.csv")
	combined_new.set_index("Player").to_csv("00 combined_filtered.csv")
	print("Written","\n")
else:
	#print(men_filteredT.shape,",",women_filteredT.shape)
	print("Final Dims:",combined_new.shape,"\n")

print("Terminated")