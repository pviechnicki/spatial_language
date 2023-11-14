#Test dependency parse output on multi-word basic locative constructions

from nltk.parse import CoreNLPDependencyParser
import graphviz
import sys
import getopt


def usage():
	usageString = '''usage: python visualizeDepGraph.py -s/--sentence=[SENTENCE] -h/-?/--help
	'''
	sys.stderr.write(usageString)

def main():

	myParser = CoreNLPDependencyParser(url='http://localhost:29000')

	sentence = ''

	opts, args = getopt.getopt(sys.argv[1:],"h?s:",["sentence=", "help"])
	for opt, arg in opts:
		if opt in ('-h', '-?', '--help'):
			usage()
			exit(0)
		elif opt in ("-s", "--sentence"):
			sentence = arg
		else:
			sys.stderr.write("Unrecognized arg {}\n".format(opt))
			usage()
			exit(1)

	print(sentence)

	try:
		parses = myParser.parse(sentence.split())
	except:
		sys.stderr.write("Couldn't connect to Dependency Parser. \nMake sure you've started local parser before attempting to run this script.\n")
		exit(1)



	for p in parses:

		with open('sentence.dot', 'wt') as f:
			f.write(p.to_dot().replace('\\', ''))
		graphviz.render('dot', 'png', filepath='sentence.dot')

		
if __name__ == '__main__':
	main()



