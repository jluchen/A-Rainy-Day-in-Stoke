import pandas as pd
import sqlite3

###Given player name, pulls information from db
def pull_players(name):
	#connection
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	qry = """SELECT * FROM similar_players_v2
			WHERE LOWER(Source) = LOWER('{0}')""".format(name)
	cursor = c.execute(qry)
	names = [description[0] for description in cursor.description]
	df = pd.DataFrame(cursor.fetchall(), columns=names)
	df = df[['Source', 'Player', 'Gender', 'Pos', 'Squad', 'Season', 'League']]
	return df.drop_duplicates()

def pull_sample_players():
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	qry = """SELECT * FROM similar_players_v2
			WHERE Source IN ('Lionel Messi', 'Alex Morgan')"""
	cursor = c.execute(qry)
	names = [description[0] for description in cursor.description]
	df = pd.DataFrame(cursor.fetchall(), columns=names)
	df = df[['Source', 'Player', 'Gender', 'Pos', 'Squad', 'Season', 'League']]
	return df.drop_duplicates()

#players is a list, n_degrees is an int, exclude is a list
def extend_graph(players, n_degrees, exclude):
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	rst = pd.DataFrame(columns=['Source','Player', 'degree'])
	for i in range(n_degrees):
		qry = """SELECT Source, Player FROM similar_players_v2
				WHERE Source IN ({0})
				AND Player NOT IN ({1})""".format(','.join(repr(p) for p in players)
												 ,','.join(repr(p) for p in exclude))
		cursor = c.execute(qry)
		names = [description[0] for description in cursor.description]
		df = pd.DataFrame(cursor.fetchall(), columns=names)
		df['degree'] = n_degrees - i - 1
		#df['count'] = 1
		players = df['Player'].tolist()
		exclude += df['Source'].unique().tolist()
		rst = rst.append(df, ignore_index=True)
	return rst.drop_duplicates(subset=['Source','Player'])

def pull_stats(players):
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	qry = """SELECT * FROM player_list
			WHERE Player IN ({0})""".format(','.join(repr(p) for p in players))
	cursor = c.execute(qry)
	names = [description[0] for description in cursor.description]
	df = pd.DataFrame(cursor.fetchall(), columns=names)
	df = df[['Player', 'Gender', 'Pos', 'Squad', 'Season', 'League']]
	return df.drop_duplicates()

###Given league name, pulls information from db
###ATTENTION: NEED FINAL LEAGUE TABLE, AUSTRALIA IS JUST FOR EXAMPLE PURPOSE
def pull_leagues(name):
	conn = sqlite3.connect('soccer_data.db')
	c = conn.cursor()
	qry = """SELECT * FROM australia_team
			WHERE LOWER(Squad) = LOWER('{0}')""".format(name)
	cursor = c.execute(qry)
	names = [description[0] for description in cursor.description]
	df = pd.DataFrame(cursor.fetchall(), columns=names)
	df = df[['Squad', 'Season', 'League', '# Pl']]

	conn = sqlite3.connect('soccer_data2.db')
	c = conn.cursor()

	sql_command = "SELECT name FROM sqlite_master WHERE type='table' and name!='members' order by name"
	cursor = c.execute(sql_command)

	table_names = [x[0] for x in cursor.fetchall()]
	team_tables = [x for x in table_names if 'team' in x]

	team_dict = {}
	for table_name in team_tables:
	    sql_command = "Select * from '" + table_name + "'"
	    cursor = c.execute(sql_command)
	    names = [description[0] for description in cursor.description]
	    temp_df = pd.DataFrame(cursor.fetchall(), columns=names)

	    team_dict[table_name] = temp_df
	team_df = pd.concat(team_dict.values(), ignore_index=True)
	team_df["('Performance', 'Fls')"] = team_df["('Performance', 'Fls')"].fillna(0).astype("int")
	team_df["Season"] = team_df["Season"].apply(lambda x : str(x).split("-")[0]).astype("int")

	return df, team_df

def lc_data(team_df, attr="('Per 90 Minutes', 'Gls')"):
	print(team_df.columns.values)
	grouped_data = team_df.groupby(["Season", "League"]).agg({attr:"mean"}).unstack().T
	grouped_data = grouped_data.fillna(0)
	print(grouped_data)
	return grouped_data

def bc_data(team_df):
	league_prof = team_df[['League', 'Season', "Win/Loss", "('Per 90 Minutes', 'Gls')", "('Per 90 Minutes', 'G+A')", "('Performance', 'CrdY')", "('Performance', 'Fls')"]].groupby(['League', 'Season']).agg({ "Season" : "count","('Per 90 Minutes', 'Gls')"  : "mean", "('Per 90 Minutes', 'G+A')" : "mean" ,"('Performance', 'CrdY')" : "mean", "('Performance', 'Fls')" : "mean", "Win/Loss" : "mean"}).rename(columns={"Season":"Games_Played"})
	league_prof["('Performance', 'CrdY')"] /= league_prof["Games_Played"]
	league_prof["('Performance', 'Fls')"] /= league_prof["Games_Played"]

	bar_data = league_prof.drop("Games_Played", axis=1)[["('Per 90 Minutes', 'Gls')", "('Per 90 Minutes', 'G+A')", "('Performance', 'CrdY')", "Win/Loss"]].groupby("League").mean()

	return bar_data
