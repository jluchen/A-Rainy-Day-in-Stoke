import pandas as pd
import numpy as np
import sqlite3
from functools import reduce
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pylab as pl
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import base64
from io import BytesIO
import matplotlib 

matplotlib.use('Agg')

def pull_all():
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	qry = "SELECT * FROM player_list"
	cursor = c.execute(qry)
	names = [description[0] for description in cursor.description]
	df = pd.DataFrame(cursor.fetchall(), columns=names)
	return df.drop_duplicates()

def clean_df(df):
	renamed = ['index', 'Player', 'Pos', 'Squad', 'Gender', 'League', 'Gen+League', 'Season',
       'Age', 'Born', 'Nation', 'ATT', 'MID', 'DEF', 'MP', 'Min', 'Starts', 'Ast', 'G+A/90',
       'G+A-PK/90',  'G-PK/90', 'Gls/90', 'Ast/90', 'CrdR', 'CrdY',
       'Fls', 'Gls', 'OG', 'PK','PKatt', 'G/SoT','SoT', 'SoT/90', 'Tkl+Int']
	df.columns = renamed

	total_matches = df.groupby('Gen+League').agg({'MP': 'max'})
	total_matches.rename(columns ={'MP': 'Total_MP'}, inplace = True)
	top_fls = df.groupby('Gen+League').agg({'Fls': 'max'})
	top_fls.rename(columns ={'Fls': 'Top_Fls'}, inplace = True)
	top_tkl = df.groupby('Gen+League').agg({'Tkl+Int': 'max'})
	top_tkl.rename(columns ={'Tkl+Int': 'Top_Tkl'}, inplace = True)
	df = df.merge(total_matches, on = "Gen+League", how = 'left')
	df = df.merge(top_fls, on = "Gen+League", how = 'left')
	df = df.merge(top_tkl, on = "Gen+League", how = 'left')

	df["%MP"] = df['MP']/df['Total_MP']
	df['%Starts'] = df['Starts']/df['Total_MP']
	df['%Min'] = df['Min']/(df['Total_MP']*90)
	return(df)


def normalize(df, attribute, group):
    col_name = 'norm ' + attribute
    a = df.groupby(group)
    aDict = {}
    for name, g in a:
        mu = g[attribute].mean()
        sigma = g[attribute].std()
        aDict[name] = [mu, sigma]
    df1 = pd.DataFrame(aDict).transpose()
    df1.reset_index(level=0, inplace=True)
    df1.columns = [group, 'mean', 'stdev']
    df = df.merge(df1, how = 'left', on = group)
    df[col_name] = (df[attribute] - df['mean'])/df['stdev']
    df.drop('mean', axis=1 , inplace = True)
    df.drop('stdev', axis=1 , inplace = True)
    return df

def log_scale(df, attribute):
    col_name = 'log ' + attribute
    df[col_name] = np.log(df[[attribute]].replace(0, np.nan)).fillna(0)
    return df

def rank_order(df, attribute, group):
    col_name = 'rank ' + attribute
    df[col_name] = df.groupby(group)[attribute].rank("dense", pct = True)
    return df


def cluster(df, col_list, n):
	df = df[col_list]
	scaler = StandardScaler()
	scaled_features = scaler.fit_transform(df.fillna(0))

	kmeans = KMeans(n_clusters = n, init = 'k-means++', max_iter = 500, n_init = 10, random_state = 0)
	kmeans.fit(scaled_features)
	clusters = kmeans.labels_

	return clusters

def silhouette(df, clusters):
	scaler = StandardScaler()
	scaled_features = scaler.fit_transform(df.fillna(0))
	silhouette = silhouette_score(scaled_features, clusters)
	return silhouette


def cluster_summary(df, clusters):
	df['clusters'] = clusters
	counts = df.groupby('clusters').agg({'Player': 'count'})
	summary = df.groupby('clusters').agg('mean')
	summary = summary.merge(counts, on= 'clusters')
	summary = summary[['Player', 'Age', 'ATT', 'MID', 'DEF', '%MP', '%Min', '%Starts', 'SoT/90', 'G+A/90', 'Tkl+Int','Fls', 'CrdY', 'CrdR']]
	summary = summary.round(decimals=2)
	summary.rename(columns={"Player": "Count"}, inplace = True)
	# summary.reset_index(inplace=True)
	# summary = summary.drop('clusters')
	return summary

def pca_viz(df, clusters):
	pca = PCA(n_components=3)
	principalComponents = pca.fit_transform(df.fillna(0))

	sns.set(style = "darkgrid")

	fig = plt.figure()
	ax = fig.add_subplot(111, projection = '3d')

	principalDf = pd.DataFrame(data = principalComponents
	             , columns = ['PC1', 'PC2', 'PC3'])

	x = principalDf['PC1']
	y = principalDf['PC2']
	z = principalDf['PC3']

	ax.set_xlabel("PC1")
	ax.set_ylabel("PC2")
	ax.set_zlabel("PC3")

	scatter = ax.scatter(x, y, z, c=clusters)

	labels = np.unique(clusters)
	handles = [plt.Line2D([],[],marker="o", ls="", 
                      color=scatter.cmap(scatter.norm(yi))) for yi in labels]
	ax.legend(handles, labels, loc='upper left')

	plt.savefig('static/plot.png')

	return 'function finished running'




















