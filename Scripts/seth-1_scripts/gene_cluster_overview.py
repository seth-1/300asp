################################
# Imports ######################
################################

import sys,os
sys.path.append("../utils/")
from aspmine_imports import *
import pandas as pd



#################################
# Arguments #####################
#################################
# action sotre true means argument is boolean, cannot assign values
parser = argparse.ArgumentParser(description="Preprocessing databases for gene clustering", usage="%(prog)s --out filename")
parser.add_argument("--out", "-o", required=False, default = "testing.csv", help="Name of output file")
#parser.add_argument("-R", default="org_shared_gc.R", required=False, help="Name of R script, org_shared_gc.R")
#parser.add_argument("--sec", required=False, default = "Nigri", help="Section name")
parser.add_argument("--plot","-p", required=False, action='store_true', help="Executes R plotting functions on data")
parser.add_argument("--single_plots","-sp", required=False, action='store_true', help="Executes R plotting functions on single clusters")
parser.add_argument("--cutoff1", "-c1", type = float, required=False, help="Select a cutoff for gene cluster similarity, i.e. how many genes must be shared among two gene clusters in order to call them homolog/ the same")
parser.add_argument("--cutoff2", "-c2", type = int, required=False, default = 0, help="Select a cutoff for gene cluster sizes, defaults to 0")
parser.add_argument("--ana1", "-a1", required=False, action='store_true', help="Overview of Clusters")
parser.add_argument("--ana2", "-a2", required=False, action='store_true', help="Clusters shared among organisms")
parser.add_argument("--bestclusters", "-bc", required=False, action='store_true', help="Find which clusters are found in most organisms, TOP 20, remember cutoffs!")
parser.add_argument("--uniqueclusters", "-uc", required=False, action='store_true', help="Find which clusters are unique among organisms, remember cutoffs!")
parser.add_argument("--singleclusters", "-single", required=False, action='store_true', help="Pass a list of clusters to be analyzed seperately and illustrate their distribution in a stacked boxplot, right now it needs a list as input")
parser.add_argument("--max_gc_abundance", "-max", required=False, action='store_true', help="Calculates max values for gene clusters")
parser.add_argument("--normalize", "-norm", required=False, action='store_true', help="Normalizes results from analysis 2 for heatmap")
parser.add_argument("--interpro", "-ipr", required=False, action='store_true', help="TODO connection to Interpro table")
parser.add_argument("--save", "-save", required=False, action='store_true', help="Save a csv file of the query")
parser.add_argument("--tcve_plot","-tp", required=False, action='store_true', help="Executes R plotting functions on single clusters")
#TODO: Fix type and choices
parser.add_argument("--tcve_custom", "-tc", required=False, action='store_true', help="custom for tcve based on single_bar_plots")
args = parser.parse_args()

outfile = args.out
cutoff1 = args.cutoff1
cutoff2 = args.cutoff2
plot = args.plot
ana1 = args.ana1
ana2 = args.ana2
normalize = args.normalize
interpro = args.interpro
save = args.save
tcve_custom = args.tcve_custom
tcve_plot = args.tcve_plot
best = args.bestclusters
single = args.singleclusters
single_plots = args.single_plots
unique = args.uniqueclusters
max_gc_abundance = args.max_gc_abundance
# done = args.done



section = 'Nigri' # TODO Needs implementation in mysql, here the table only has Nigri members....


print cutoff1
print cutoff2
print section
# IMPORTANT!  DELETE FROM antismashLoopAntismash where q_orgname = 'Aspac1' and h_realname, = 'Aspac1'; bc Aspac 1 entries are still weird...
def make_heatmap(outfile):
	print "# INFO: running Rscript"
	try:
		os.system("R CMD BATCH '--args %s %s %s %s' gc_shared_through_orgs.R test.out" % (outfile, section, cutoff1*100, cutoff2))
	except:
		print "Cannot connect to R"

def single_bar_plots(outfile, clust, score, org, completeMembers):
	print "# INFO: running Rscript"
	try:
		os.system("R CMD BATCH '--args %s %s %s %s %s' gc_plot.R test.out" % (outfile, clust, score, org, completeMembers))
	except:
		print "Cannot connect to R"
# CONNECTING

def asp_con(path):
#------------------------------------------------------------------
# Connect to specific DB
#------------------------------------------------------------------
	try:
		if path == 'remote':
			db = mdb.connect(host="192.38.13.9", user="setd" ,passwd="1234",db= 'aspminedb') #host="localhost", user="root" ,passwd="Gru3n3r+T33",db= database)
	except mdb.Error, e:
		sys.exit("Cannot connect to database")#"# ERROR %d: %s" % (e.args[0],e.args[1]))
	try:
		cursor = db.cursor()
	except mdb.Error, e:
		sys.exit("# ERROR %d: %s" % (e.args[0],e.args[1]))
	return cursor

cursor = asp_con('remote')

if max_gc_abundance:
	cursor.execute("DROP TABLE IF EXISTS t_testing_max")
	query ="CREATE TABLE t_testing_max as select q_realname, max(shared) as max_shared from (select q_realname, h_realname, q_clustid, count(*) as shared from t_antismashLoopAntismashCandidates where clustCov >%f and q_clust_size > %i and q_sec = 'Nigri' and h_sec = 'Nigri' and q_realname != 'aculeatus' and h_realname != 'aculeatus' group by q_realname, h_realname) ta group by q_realname;" % (cutoff1, cutoff2)

if ana1:
	query = "SELECT q_clustid, q_clust_size, q_realname, h_realname, h_clust_backbone,  members from (\
		SELECT *, count(*) as members from antismashLoopAntismash\
		where h_clust_backbone is not null group by q_clustid, q_realname, h_realname, h_clust_backbone) ta\
		where members > q_clust_size*%f and q_clust_size>%i;" % (cutoff1, cutoff2)
#h_clust_protein-id not in Candidates!
if ana2:
	cursor.execute("DROP TABLE IF EXISTS t_gc_shared_count")
	query = " CREATE TABLE t_gc_shared_count AS SELECT q_realname, h_realname, q_clustid, count(*) as shared from t_antismashLoopAntismashCandidates where clustCov >%f and q_clust_size > %i and q_sec = 'Nigri' and h_sec = 'Nigri' group by q_realname, h_realname;" % (cutoff1, cutoff2)

# old
#		SELECT q_clustid, q_clust_size, q_realname, h_realname, h_clust_backbone, members from (\ #h_clust_protein-id not in Candidates!
#		SELECT *, count(*) as members from antismashLoopAntismash\
#		where h_clust_backbone is not null group by h_clust_backbone) ta\
#		where members > q_clust_size*%f and q_clust_size>%i) tb group by q_realname ,h_realname,;" % (cutoff1, cutoff2)

if best:
	query ="SELECT q_clustid, count(*) as found from (SELECT * from t_antismashLoopAntismashCandidates\
		where h_clust_backbone is not null and clustCov > %f and q_clust_size>%i group by h_clust_backbone) ta\
		group by q_clustid order by found DESC limit 20;" % (cutoff1, cutoff2)

if unique:
	query = " SELECT * from (SELECT q_clustid, count(*) as found from (\
		SELECT * from t_antismashLoopAntismashCandidates where h_clust_backbone is not null and clustCov > %f and q_clust_size>%i\
		 group by h_clust_backbone) ta group by q_clustid order by found) tb where found =1;" % (cutoff1, cutoff2)

if normalize:
	query = "SELECT t_gc_shared_count.q_realname, t_gc_shared_count.h_realname, (t_gc_shared_count.shared/t_testing_max.max_shared)*100 as norm_shared from t_gc_shared_count join t_testing_max ON t_gc_shared_count.q_realname = t_testing_max.q_realname ;"


##################################
# Analysis for each gene cluster #
##################################

if single:

	with open('best.csv') as f:
		reader = csv.reader(f)
		bestHits = list(reader)

	for i in bestHits:
		clust, score = i
		print(clust)
		query = " SELECT organism.real_name, tx.In_cluster FROM (\
			SELECT org_id, In_cluster FROM (SELECT a2b.clust_id AS q_clust_id, concat(smash.org_id, '_', smash.clust_backbone, '_', smash.clust_size) AS h_clust_id, smash.org_id, count(*) AS In_cluster\
			from t_antismash2blast_reduced AS a2b JOIN antismash AS smash on h_seqkey = smash.sm_protein_id WHERE a2b.clust_id = '%s' and smash.org_id\
			GROUP BY h_clust_id) ta ORDER BY org_id, In_cluster DESC) tx join organism on tx.org_id = organism.org_id;" % (str(clust))
		print(query)
		try:
			cursor.execute(query)
			result = cursor.fetchall()
		except:
			print "Error in Analysis"

		genome = {}

		for line in result:
			a,b = line
			if a in genome:
				genome[a].append(int(b))
			else:
				genome[a] = list()
				genome[a].append(int(b))
			
	# To do: If runs slow, improve here by filling up with NAs before to avoid transposing
		gframe = pd.DataFrame.from_dict(genome, orient='index', dtype=float)
		#gframe = gframe.transpose()
		gframe.to_csv('single_%s.csv' % clust)

# TODO finish here!
#if done:
#	query = "SELECT t_gc_shared_count.q_orgname, t_gc_shared_count.h_realname,, (t_gc_shared_count.shared/testing_max.maxsh)*100 as norm_shared  from t_gc_shared_count left join testing_max ON t_gc_shared_count.q_orgname = testing_max.q_orgname ;"


# TODO finish here!!!
if interpro:
	with open('best.csv') as f:
		reader = csv.reader(f)
		bestHits = list(reader)

	for i in bestHits:
		clust, score = i
		query ="SELECT sm_protein_id, ipr.ipr_id, ipr_desc from (SELECT sm_protein_id, protein_has_ipr.* from (SELECT * from antismash where clust_backbone = 433535 and antismash.org_id = 11) ta join protein_has_ipr on sm_protein_id = protein_id and ta.org_id = protein_has_ipr.org_id) tb join ipr on tb.ipr_id = ipr.ipr_id group by ipr.ipr_id , sm_protein_id order by sm_protein_id;"
		try:
			cursor.execute(query)
			result = cursor.fetchall()
		except:
			print "Error in Analysis"

#print query
if plot == False:
	try:
		cursor.execute(query)
		result = cursor.fetchall()
		print result
	except:
		print "Error in Analysis"

if save:
	f = open(outfile,'wb')
	writer = csv.writer(f, dialect = 'excel')
	writer.writerows(result)
	f.close()

'''------------------------------------------------------------------
# Plotting
------------------------------------------------------------------'''

if plot:
	make_heatmap(outfile)

if single_plots:
	with open('best.csv') as f:
		reader = csv.reader(f)
		bestHits = list(reader)

	for i in bestHits:
		clust, score = i
		query = "SELECT real_name FROM organism WHERE org_id = '%s'" % clust[:2]
		try:
			cursor.execute(query)
			org = cursor.fetchall()[0][0]

		except:
			print "cannot find this Organism"

		try:
			if clust[-2] == '_':
				completeMembers = clust[-1]
			else:
				completeMembers = clust[-2:]
		except:
			print "Cannot convert number of complete members from cluster id"
		print completeMembers
		single_bar_plots('single_%s.csv' % clust, clust, score, org, completeMembers)

if tcve_custom:
	with open('/home/seth/Dropbox/seth-1/barplots_metabolites.tab') as f:
		reader = csv.reader(f, dialect = 'excel-tab')
		bestHits = list(reader)

	for i in bestHits:
		clust = i[0]
		print(clust)
		query = " SELECT organism.real_name, tx.In_cluster FROM (\
			SELECT org_id, In_cluster FROM (SELECT a2b.clust_id AS q_clust_id, concat(smash.org_id, '_', smash.clust_backbone, '_', smash.clust_size) AS h_clust_id, smash.org_id, count(*) AS In_cluster\
			from t_antismash2blast_reduced AS a2b JOIN antismash AS smash on h_seqkey = smash.sm_protein_id WHERE a2b.clust_id = '%s' and smash.org_id\
			GROUP BY h_clust_id) ta ORDER BY org_id, In_cluster DESC) tx join organism on tx.org_id = organism.org_id;" % (str(clust))
		try:
			cursor.execute(query)
			result = cursor.fetchall()
		except:
			print "Error in Analysis"

		genome = {}

		for line in result:
			a,b = line
			if a in genome:
				genome[a].append(int(b))
			else:
				genome[a] = list()
				genome[a].append(int(b))
			
	# To do: If runs slow, improve here by filling up with NAs before to avoid transposing
		gframe = pd.DataFrame.from_dict(genome, orient='index', dtype=float)
		#gframe = gframe.transpose()
		gframe.to_csv('single_%s.csv' % clust)
		infile = 'single_%s.csv' % clust

#	with open('/home/seth/Dropbox/seth-1/barplots_metabolites.tab') as f:
#		reader = csv.reader(f, dialect = 'excel-tab')
#		bestHits = list(reader)

if tcve_plot:
	score = 0
	with open('/home/seth/Dropbox/seth-1/barplots_metabolites.tab') as f:
	# with open('/home/seth/Dropbox/seth-1/test.tab') as f: # just for testing
		reader = csv.reader(f, dialect = 'excel-tab')
		bestHits = list(reader)

	for i in bestHits:
		clust = i[0]
		print(clust)
# TODO find a regex way? forgot this so some clusters went missing, but it also worked for some, for some reason....

		try:
			if clust[1] == '_':
				orga = clust[0]
			else:
				orga = clust[:1]
		except:
			print "Cannot convert number of complete members from cluster id"
		query = "SELECT real_name FROM organism WHERE org_id = '%s'" % orga
		print query
		try:
			cursor.execute(query)
			org = cursor.fetchall()[0][0]

		except:
			print "cannot find this Organism"

		try:
			if clust[-2] == '_':
				completeMembers = clust[-1]
			else:
				completeMembers = clust[-2:]
		except:
			print "Cannot convert number of complete members from cluster id"
		print completeMembers
		single_bar_plots('single_%s.csv' % clust, clust, score, org, completeMembers)

'''
	for i in bestHits:
		clust = i[0]
		query = "SELECT real_name FROM organism WHERE org_id = '%s'" % clust[:2]
		try:
			cursor.execute(query)
			org = cursor.fetchall()[0][0]

		except:
			print "cannot find this Organism"

		try:
			if clust[-2] == '_':
				completeMembers = clust[-1]
			else:
				completeMembers = clust[-2:]
		except:
			print "Cannot convert number of complete members from cluster id"
		print completeMembers

		print "# INFO: running Rscript"
		try:
			os.system("R CMD BATCH '--args %s %s %s %s' gc_plot_custom.R test.out" % (infile, clust, org, completeMembers))
		except:
			print "Cannot connect to R"
'''
#if single:
#	print "# INFO: running Rscript"
#	try:
#		os.system("R CMD BATCH '--args %s ' gc_plot.R test.out" % (outfile))
#	except:
#		print "Cannot connect to R"


