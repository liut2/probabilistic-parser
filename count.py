#count.py
#written by Tao Liu
#the training data is in single-line json format, not the original treebank
#I select the training set format like this because it makes it easier to get the 
#the grammar from the parsed sentences compared to treebank
import sys
import json
import string
import types
import operator
# basestring doesn't exist in Python3, so I need to define it here
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring	
#this class is used to calculate the freq that each production rules occurs in the training set
class Counter:
	def __init__(self):
		#init dict to count the freq of A -> BC binary rules
		self.binaryCount = {}
		#init dict to count the freq of A -> w unary rules
		self.unaryCount = {}
		#init dict to count the freq of lefthand non-terminal that expands to all the rules
		self.nonterminalCount = {}
		#init dict to calculate the binary prob
		self.binaryProb = {}
		#init dict to calculate the unary prob
		self.unaryProb = {}
	#calculate prob for each production rule
	def calcProb(self):
		for (lefthand, terminal), count in self.unaryCount.items():
			self.unaryProb[lefthand, terminal] = float(count)/ self.nonterminalCount[lefthand]
		for (lefthand, righthand1, righthand2), count in self.binaryCount.items():
			self.binaryProb[lefthand, righthand1, righthand2] = float(count)/self.nonterminalCount[lefthand]
		for (lefthand, righthand1, righthand2), count in self.binaryProb.items():
			if (lefthand == "S"):
				string = lefthand + " -> " + righthand1 + " " + righthand2 + " " + str(count)
				print(string)
	#read the tree as json format and output the result to count.txt
	def count(self, fileName):
		f = open(fileName)
		for line in f:
			line = line.strip()
			tree = json.loads(line)
			self.countHelper(tree)
		#print(self.nonterminalCount)
		self.calcProb()
		self.unknownProb()
		self.output()
		f.close()
		#print(self.nonterminalCount)

	#this function recursively decode the tree to count the freq of each rule
	def countHelper(self, tree):
		#base case
		if isinstance(tree, basestring):
			return
		#non-terminal that expands to all its production rules
		lefthand = tree[0]
		#remove extra tag
		if ("+" in lefthand):
			#print(lefthand)
			fields = lefthand.split("+")
			lefthand = fields[1]
			#print(lefthand)
		#count the freq of non-terminal, which will be used as denominator
		self.nonterminalCount.setdefault(lefthand, 0)
		self.nonterminalCount[lefthand] += 1
		#the case of a binary-rule production, A -> BC
		if (len(tree) == 3):
			righthand1, righthand2 = (tree[1][0], tree[2][0])
			if ("+" in righthand1):
			#print(lefthand)
				fields = righthand1.split("+")
				righthand1 = fields[1]
			if ("+" in righthand2):
				fields = righthand2.split("+")
				righthand2 = fields[1]
			key = (lefthand, righthand1, righthand2)
			self.binaryCount.setdefault(key, 0)
			self.binaryCount[key] += 1
			#recursively count the subtree
			self.countHelper(tree[1])
			self.countHelper(tree[2])
		#the case of a unary-rule, A -> w
		elif (len(tree) == 2):
			righthand = tree[1].lower()
			
			key = (lefthand, righthand)
			self.unaryCount.setdefault(key, 0)
			self.unaryCount[key] += 1
	#output the freq to a text file to read by the parser later
	def output(self):
		f = open("count.txt", "w")
		for (lefthand, terminal), count in self.unaryProb.items():
			string = "unary" + " " + lefthand + " " + terminal + " " + str(count) + " \n"
			f.write(string)
		for (lefthand, righthand1, righthand2), count in self.binaryProb.items():
			string = "binary" + " " +  lefthand + " " + righthand1 + " " + righthand2 + " " + str(count) + " \n"
			f.write(string)
		for lefthand, count in self.nonterminalCount.items():
			string = "non-terminal" + " " + lefthand + " " + str(count) +  " \n"
			f.write(string)
		f.close()
	#this function deals with the unknown words
	def unknownProb(self):
		totalCount = 0
		#calculate the distribution of non-terminals and assign proper weight to 
		#unknown words unary rule probabilities
		for key, value in self.nonterminalCount.items():
			totalCount += value
		for key, value in self.nonterminalCount.items():
			self.unaryProb[key, "UNKNOWN"] = float(value)/totalCount
	

if __name__ == "__main__": 
  fileName = sys.argv[1]
  counter = Counter()
  counter.count(fileName)
  