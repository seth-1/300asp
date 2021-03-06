#!/usr/bin/python

'''##################################################################
# Imports
##################################################################'''
import sys, os
root = os.path.abspath(__file__).split("github")[0]
sys.path.append(root+"github/utils/")
from aspmine_imports import *

##############################################################################################################################################
##############################################################################################################################################
####################################################################### ARGUMENTS ############################################################
##############################################################################################################################################
##############################################################################################################################################
startTime = datetime.now() # record runtime

#------------------------------------------------------------------
''' Get command line arguments '''
#------------------------------------------------------------------
parser = CustomArgumentParser(formatter_class=SmartFormatter, 
								description="Get single linkage clusters from gene ID or name", 
								 usage='%(prog)s -gene [gene name] -strain [list of JGI strain names] -dbname [name of database]\n'
								 "Example: python %(prog)s -gene An15g00560 -strain Aspni1 Aspor1 -dbname aspminedb")
#parser.add_argument("-limit", "-l", required=False, default = 100, help="limit length selects, dafault 100, to select all set to 'all' ")
parser.add_argument("-gene", "-g", nargs = '*', required=True, default=[None], action='store', help="List of gene names")
parser.add_argument("-strain", "-s", nargs = '*',  required=True, default=[None], action='store', help="List of organism JGI keys")
parser.add_argument("-dbname", "-d",  required=False, default = "aspminedb", action='store',help="Database name")

args = parser.parse_args()
dbname=args.dbname
genes = args.gene
strains = args.strain

#------------------------------------------------------------------
# Print argument values to screen
#------------------------------------------------------------------
print "#--------------------------------------------------------------"
print "# ARGUMENTS :\n# Database\t:%s\n# Genes\t:%s\n# Strains\t:%s" % (dbname, genes, strains)
print "#--------------------------------------------------------------"


##############################################################################################################################################
##############################################################################################################################################
####################################################################### DATABASE  ############################################################
##############################################################################################################################################
##############################################################################################################################################

#------------------------------------------------------------------
# Connect to specific DB
#------------------------------------------------------------------
try:
    db = mdb.connect("localhost","asp","1234",str(dbname))

except mdb.Error, e:
    sys.exit("# ERROR %d: %s" % (e.args[0],e.args[1]))

try:
	cursor = db.cursor()

except mdb.Error, e: 
	sys.exit("# ERROR %d: %s" % (e.args[0],e.args[1]))

##############################################################################################################################################
##############################################################################################################################################
####################################################################### DATA      ############################################################
##############################################################################################################################################
##############################################################################################################################################

""" fetchGenes """
def fetchGenes (strains, genes):
	(strain_string, gene_string) = ("","")

	for s in range(0,len(strains)):
		strain_string += " h_org = \'" + strains[s] + "\'"
		if s != len(strains)-1:
			strain_string += " or "


	for i in range(0,len(genes)):
		gene_string += " q_seqid like \'%" + genes[i] + "%\'"
		if i != len(genes)-1:
			gene_string += " or "

	#print strain_string
	#print gene_string

	try:
		query = ("SELECT q_org, h_org, q_seqid, h_seqid, pident, \
		(q_end-q_start+1)/q_len*100 as qcov, (h_end-h_start+1)/h_len*100 as scov \
		from blast where (" + gene_string + ") and (" + strain_string + ") and h_seqid != q_seqid; ")
		cursor.execute(query)

	except mdb.Error, e: 
		sys.exit("# ERROR %d: %s" % (e.args[0],e.args[1]))

	result = cursor.fetchall()

	return result, query
""" END fetchGenes """

for ns in range(0, len(strains)):
	(result, query) = fetchGenes(strains, genes)
	for r in result:
		if r[3] not in genes:
			genes.append(r[3])

print query

for r in result:
	print ';'.join(map(str,r))




#print type(result)

