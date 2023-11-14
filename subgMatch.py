#Test filtering sentences which don't match template

from nltk.parse import CoreNLPDependencyParser, DependencyGraph
import sys
import getopt

DEBUGFLAG = False

class SearchableDG(DependencyGraph):

	#Child class of nltk.parse.dependencyparser.DependencyGraph
	# To get all the nodes of the graph --for address in searchableWorld.DG.nodes.keys():

	def __init__(self, thisDG):

		self.DG = thisDG

	def next_node_relationship(self, thisNode):

		result = 'UNKNOWN'
		#Is the next node in the depth-first search a sibling or a child?

		parent = self.DG.get_by_address(thisNode)['head']

		if len(self.DG.get_by_address(thisNode)['deps']) > 0:

			result = 'CHILD'

		elif len(self.DG.get_by_address(parent)['deps']) > 1:

			result = 'SIBLING'


		return(result)

	def get_first_dependency_relation(self):
		#return the dependency of the left-most child of the first dependency of the root node

		rel = ''

		parent_address = self.DG.get_by_address(0)['address']

		child_address = next(iter(self.DG.get_by_address(parent_address)['deps'].values()))[0]

		rel = next(iter(self.DG.get_by_address(child_address)['deps'].keys()))

		return rel

	def search_nodes_by_attribute(self, attr, value):
		#Search the nodes of the graph, returning any whose attribute matches the value

		result = []

		for node in self.DG.nodes:

			try:

				if self.DG.get_by_address(node)[attr] == value:

					result.append(node)

			except KeyError:

				print("Key error: {} not found in node keys.".format(attr))

		return result

	def search_nodes_by_relation(self, relation):
		#search graph for any nodes with a relation matching the argument
		matches = set()

		#Start with list of nodes
		for node in self.DG.nodes.keys():

			for (rel, node_list) in self.DG.get_by_address(node)['deps'].items():

				if rel == relation:

					matches.add(node)

		return list(matches)

	def is_sibling_or_child(self, thisNode, thisPotentialFamilyMemberNode):
		#The name says it all: is this node either a sibling or child of the second arg?
		result = False
		if self.is_sibling(thisNode, thisPotentialFamilyMemberNode):
			result = True
		elif self.is_child(thisNode, thisPotentialFamilyMemberNode):
			result = True

		return result

	def is_sibling(self, thisNode, thisPotentialSibling):
		#Is the first arg a sibling in the graph of the second arg?

		head1 = self.DG.get_by_address(thisNode)['head']
		head2 = self.DG.get_by_address(thisPotentialSibling)['head']

		if head1 == head2:

			if DEBUGFLAG:
				print("Node {} is sibling of node {}".format(thisNode, thisPotentialSibling))
			return True

		else:

			if DEBUGFLAG:
				print("Node {} is not a sibling of node {}".format(thisNode, thisPotentialSibling))
			return False 

	def is_child(self, thisNode, thisPotentialParent):
		#Is the first arg a child of the second arg in the graph?

		trueParent = self.DG.get_by_address(thisNode)['head']

		if trueParent == thisPotentialParent:
			if DEBUGFLAG:
				print("Node {} is child of node {}".format(thisNode, thisPotentialParent))
			return True 
		else:
			print("Node {} is not a child of node {}".format(thisNode, thisPotentialParent))
			return False 


	# A function used by DFSearch
	def DFSearchUtil(
		self, 
		world_start_node, 
		thisTemplate, 
		world_nodes_visited, 
		template_start_node, 
		template_nodes_matched,
		template_nodes_visited,
		last_world_match_node
		):

		# Mark the current node as visited
		# and print it
		world_nodes_visited.add(world_start_node)
		if DEBUGFLAG:
			print("visiting {}".format(world_start_node))

		template_nodes = set(list(thisTemplate.DG.nodes.keys()))

		# Recur for all the vertices
		# adjacent to this vertex
		for (world_rel, address_list) in self.DG.get_by_address(world_start_node)["deps"].items():
			for address in address_list:
				#Get next template rel
				if address not in world_nodes_visited and template_nodes_matched != template_nodes:

					if DEBUGFLAG:
						print("Traversing dependency arc to node {} with relationship {}".format(address, world_rel))
						print("Template_start_node: ", template_start_node)

					for (template_rel, template_address_list) in thisTemplate.DG.get_by_address(template_start_node)["deps"].items():

						if DEBUGFLAG:
							print("template_address_list: ", template_address_list)

						for template_address in template_address_list:

							template_nodes_visited.add(template_address)

							if DEBUGFLAG:
								print("template_address {}, template_rel = {}, world_rel = {}".format(template_address, template_rel, world_rel))	
							if template_rel == world_rel and self.is_sibling_or_child(address, last_world_match_node):

								#Keep track of which world node was the parent of the one you just matched
								last_world_match_node = address

								if DEBUGFLAG:
									print("Match conditions met for world node {} and template node {}".format(address, template_address))
								template_nodes_matched.add(template_address)

								#This might be the tricky part. If next world node is sibling, then set template_start_node to head
								#If it is a child, then set template_start_node to template_address
								if thisTemplate.next_node_relationship(template_address) == 'SIBLING':
									template_start_node = thisTemplate.DG.get_by_address(template_address)["head"]
								elif thisTemplate.next_node_relationship(template_address) == 'CHILD':
									template_start_node = template_address
								else:
									print("Warning: couldn't determine relationship of next template node for template_address {}.".format(template_address))
								
								if DEBUGFLAG:
									print("New template_start_node: ", template_start_node)
								

								if DEBUGFLAG:
									print("Visited: ", template_nodes_visited)
									print("Matched: ", template_nodes_matched)
								

					self.DFSearchUtil(
						address, 
						thisTemplate, 
						world_nodes_visited,
						template_start_node,
						template_nodes_matched,
						template_nodes_visited,
						last_world_match_node)

		return(template_nodes_matched)

	# The function to do DFS search, only traversing if the link type matches the pattern. It uses
	# recursive DFSearchUtil()
	def DFSearch(self, world_start_node, thisTemplate):

		#thisTemplate is the pattern/subgraph we are looking to find in the world graph

		# Create a set to store visited vertices
		world_nodes_visited = set()

		#Store all the template nodes successfully matched
		template_nodes = set(list(thisTemplate.DG.nodes.keys()))
		template_nodes_matched = set()
		template_nodes_matched.add(0) #No need to match root node
		template_nodes_visited = set()
		template_nodes_visited.add(0)
		template_start_nodes = next(iter(thisTemplate.DG.get_by_address(0)['deps'].values()))
		template_start_node = template_start_nodes[0]
		template_nodes_matched.add(template_start_node)
		last_world_match_node = world_start_node
		#last_world_match_node = self.DG.get_by_address(world_start_node)['head']
		
		# Call the recursive helper function
		# to print DFSearch		
		final_nodes_matched = self.DFSearchUtil(
			world_start_node, 
			thisTemplate, 
			world_nodes_visited, 
			template_start_node, 
			template_nodes_matched,
			template_nodes_visited,
			last_world_match_node
			)

		if final_nodes_matched == template_nodes:

			return True 
		
		else:
		
			return False 

def usage():
	usageString = '''usage: python subgMatch.py -w/--world=[WORLD SENTENCE] -t/--template=[TEMPLATE SENTENCE] -h/-?/--help
	'''
	sys.stderr.write(usageString)

def main():

	myParser = CoreNLPDependencyParser(url='http://localhost:29000')

	world = ''
	template = ''

	opts, args = getopt.getopt(sys.argv[1:],"h?w:t:",["world=", "template=", "help"])
	for opt, arg in opts:
		if opt in ('-h', '-?', '--help'):
			usage()
			exit(0)
		elif opt in ("-w", "--world"):
			world = arg
		elif opt in ("-t", "--template"):
			template = arg
		else:
			sys.stderr.write("Unrecognized arg {}\n".format(opt))
			usage()
			exit(1)

	print("Template: {}".format(template))
	print("World: {}".format(world))


	try:
		parses_t = myParser.parse(template.split())
		parses_w = myParser.parse(world.split())
	except:
		sys.stderr.write("Couldn't connect to Dependency Parser. \nMake sure you've started local parser before attempting to run this script.\n")
		exit(1)



	for pt in parses_t:

		searchableTemplate = SearchableDG(pt)

		for pw in parses_w:

			searchableWorld = SearchableDG(pw)

			starting_relation = searchableTemplate.get_first_dependency_relation()

			candidate_start_nodes = searchableWorld.search_nodes_by_relation(starting_relation)

			for n in candidate_start_nodes:

				print("{}: {}".format(n, searchableWorld.DFSearch(n, searchableTemplate)))

	
if __name__ == '__main__':
	main()



