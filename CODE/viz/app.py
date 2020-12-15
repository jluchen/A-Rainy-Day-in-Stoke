from flask import Flask, flash, redirect, render_template, request, session, abort,send_from_directory,send_file,jsonify
import pandas as pd
import json
from comp_utility import pull_players, pull_sample_players, extend_graph, pull_stats, pull_leagues, lc_data
from cluster_utility import pull_all, clean_df, normalize, log_scale, rank_order, cluster, silhouette, cluster_summary, pca_viz

app = Flask(__name__)

###Essentially internal data storage###
class player_store():
	name = None
	df = None
	graph = None
	stats = None
player_data = player_store()

class league_store():
	name = None
	df = None
league_data = league_store()

###Render homepage###
@app.route('/')
def home():
	return render_template('home.html')

###Takes form input and pulls from sqlite###
@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/player_comp', methods=['GET'])
def player_comp():
	player_data.name = request.args.get('player_name', '')
	#if we have form input
	if player_data.name:
		player_data.df = pull_players(player_data.name)
	#show popular players (launch page)
	else:
		player_data.name = 'popular ones like Lionel Messi or Alex Morgan!'
		player_data.df = pull_sample_players()
	#How far do we want to extend the graph (more degrees of separation)
	n_degrees = 1
	player_data.graph = player_data.df[['Source','Player']].copy()
	#player_data.graph['count'] = 1
	player_data.graph['degree'] = n_degrees
	extend = extend_graph(players=player_data.graph['Player'].tolist()
		, n_degrees=n_degrees
		, exclude=player_data.graph['Source'].unique().tolist())
	player_data.graph = player_data.graph.append(extend, ignore_index=True)
	player_data.graph.drop_duplicates(subset=['Source','Player'], inplace=True)

	return render_template('player_comp.html', player=player_data.name,
		player_rst=[player_data.df.drop(['Source'], axis=1).to_html(classes='table-center', index=False)])
	#return render_template('player_comp.html', player=player_data.name)

@app.route('/league_comp', methods=['GET'])
def league_comp():
	league_data.name = request.args.get('league_name', '')
	league_data.df, league_data.team_df = pull_leagues(league_data.name)

	return render_template('league_comp.html', league_rst=[league_data.df.to_html(classes='data', index=False)], team_df=league_data.team_df)

@app.route('/clustering', methods=['GET','POST'])
def clustering():

	player_df = pull_all()
	player_df = clean_df(player_df)

	n = request.args.get('n_clusters', '')
	Age = request.args.get('Age', '')
	Pos = request.args.get('Pos', '')
	MP = request.args.get('MP', '')
	Min = request.args.get('Min', '')
	Starts = request.args.get('Starts', '')
	Gls = request.args.get('Gls', '')
	Ast = request.args.get('Ast', '')
	SoT = request.args.get('SoT', '')
	GSoT = request.args.get('GSoT', '')
	CrdR = request.args.get('CrdR', '')
	CrdY = request.args.get('CrdY', '')
	Fls = request.args.get('Fls', '')
	PKatt = request.args.get('PK', '')
	TI = request.args.get('TI', '')

	var_list = [Age, Pos, MP, Min, Starts, Gls, Ast, SoT, GSoT, CrdR, CrdY, Fls, PKatt, TI]
	name_list = ['Age', 'Pos', '%MP', '%Min', '%Starts', 'Gls/90', 'Ast/90', 'SoT/90', 'G/SoT', 'CrdR', 'CrdY', 'Fls', 'PK', 'Tkl+Int']

	cols = []
	if n != '':
		try:
			for i in range(len(var_list)):
				if name_list[i] != 'Pos':
					if var_list[i] == "Unadjusted":
						cols.append(name_list[i])
					elif var_list[i] == "Z":
						player_df = normalize(player_df, name_list[i], 'League')
						col = 'norm ' + name_list[i]
						cols.append(col)
					elif var_list[i] == "Log":
						player_df = log_scale(player_df, name_list[i])
						col = 'log ' + name_list[i]
						cols.append(col)
					elif var_list[i] == "Rank":
						player_df = rank_order(player_df, name_list[i], 'League')
						col = 'rank ' + name_list[i]
						cols.append(col)

			final_df = player_df[cols]

			clusters = cluster(player_df, cols, int(n))
			# coeff = silhouette(player_df[cols], clusters)
			summ = cluster_summary(player_df, clusters)
			pca = pca_viz(final_df, clusters)

			return render_template('clustering.html', n_clusters = n,
				summary = [summ.to_html(classes='data table-center', header = 'true')], cols = cols)
		except:
			pass
	return render_template('clustering.html')


###Send data to js files for d3###
@app.route('/get-stats', methods=['GET','POST'])
def get_stats():
	players = player_data.graph['Source'].unique().tolist() + player_data.graph['Player'].unique().tolist()
	player_data.stats = pull_stats(players).astype(str)
	rst = player_data.stats.groupby(['Player', 'Gender']).agg(lambda x: ', '.join(x.unique())).reset_index()
	#filter out duplicate positions
	try:
		rst['Pos'] = rst['Pos'].apply(lambda x: ', '.join(a for a in set([p.replace(' ', '') for p in x.split(',')])))
	except:
		pass
	return rst.to_csv()
	#return player_data.stats.to_csv()

@app.route('/get-player-graph', methods=['GET','POST'])
def get_player_graph():
	return player_data.graph.to_csv()
	#return player_data.graph.groupby(['Source','Player', 'degree']).count().reset_index().to_csv()

@app.route('/get-league-data', methods=['GET','POST'])
def get_league_data():
	return league_data.df.to_csv()

@app.route('/get-league-chart-data', methods=['GET','POST'])
def get_league_chart_data():
	return league_data.team_df.to_csv()

@app.route('/get-line-chart-data', methods=['GET','POST'])
def get_line_chart_data():
	attr = request.args.get('attr', default = 1, type = str)
	line_chart_data = lc_data(league_data.team_df, attr)
	return line_chart_data.to_csv()


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=3001, debug=True)
