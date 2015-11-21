#parser.py
#Written by Tao Liu
import sys
import string
import operator

#this class reads the probabilities we calculated and use the CKY algorithm 
#along with the probabilities to calculate the most probable parse tree, I also print the 
#the parse tree in json format
class Parser:
	def __init__(self, binaryProb, unaryProb, nonterminalCount):
		#init the probabilities dicts
		self.binaryProb = binaryProb
		self.unaryProb = unaryProb
		self.nonterminalCount = nonterminalCount
	#this function recursively prints the tree.
	#since the tree satisfies the binarization, it's very easy to 
	#use the divide and conquer to parse the tree
	def printTree(self, words, back, i, j, lefthand):
		#base case
		if (i == j):
			return [lefthand, words[i]]
		#go deeper to left and right subtree
		else:
			(k, righthand1, righthand2) = back[i, j, lefthand]
			return [lefthand, self.printTree(words, back, i, k, righthand1), self.printTree(words, back, k + 1, j, righthand2)]


	#this is the revised version of the CKY with the probabilities
	def CKY(self, words):
		#split the sentence
		words = words.strip().split(" ")
		n = len(words)
		#init the table and the backpointer
		table = {}
		back = {}
		#table = [[{} for i in range(n + 1)] for j in range(n + 1)]
		#back = [[{} for i in range(n + 1)] for j in range(n + 1)]
		for i in range(n):
			terminal = words[i]
			#deal with unknown words
			ifUnknown = True
			for lefthand in self.nonterminalCount.keys():
				if (lefthand, terminal) in self.unaryProb:
					table[i, i, lefthand] = self.unaryProb[lefthand, terminal]
					ifUnknown = False
			if ifUnknown:
				for lefthand in self.nonterminalCount.keys():
					table[i, i, lefthand] = self.unaryProb[lefthand, "UNKNOWN"]
			#outter loop
			for split in range(1, n):
				for i in range(n - split):
					j = i + split
					for lefthand in self.nonterminalCount.keys():
						maxProb = 0
						backInfo = None
						for lh in self.binaryProb.keys():
							if lh[0] == lefthand:
								#forall{A|A → BC ∈ grammar,and table[i,k,B] > 0 and table[k, j,C] > 0 }
								righthand1, righthand2 = lh[1], lh[2]
								
								for k in range(i,j):
									if (i, k, righthand1) in table and (k+1, j, righthand2) in table:
										#f (table[i,j,A] < P(A → BC) × table[i,k,B] × table[k,j,C]) then
										#table[i,j,A]←P(A → BC) × table[i,k,B] × table[k,j,C]
										#back[i,j,A]←{k,B,C}
										prob = self.binaryProb[lefthand, righthand1, righthand2]*table[i, k, righthand1]*table[k + 1, j, righthand2]
										if prob > maxProb:
											maxProb = prob
											backInfo = k, righthand1, righthand2
						if maxProb > 0:
							#print("yes")
							table[i, j, lefthand] = maxProb
							back[i, j, lefthand] = backInfo
		
		if (0, len(words) - 1, "S") in table:
			print(self.printTree(words, back, 0, len(words) - 1, "S"))
		else:
			print("there is no parse tree that can be generated from the grammar rule")

#this class read probabilites we calculated before from the text file
class ProbBuilder:
	def __init__(self):
		#init the binary prob dict
		self.binaryProb = {}
		#init the unary prob dict
		self.unaryProb = {}
		#init non-terminal count dict
		self.nonterminalCount = {}

	def readCount(self, fileName):
		f = open(fileName)
		#read the count from the file
		for line in f:
			fields = line.strip().split(" ")
			if (fields[0] == "unary"):
				lefthand = fields[1]
				terminal = fields[2]
				prob = fields[3]
				self.unaryProb[lefthand, terminal] = float(prob)
			elif (fields[0] == "binary"):
				lefthand = fields[1]
				righthand1 = fields[2]
				righthand2 = fields[3]
				prob = fields[4]
				self.binaryProb[lefthand, righthand1, righthand2] = float(prob)
			elif (fields[0] == "non-terminal"):
				lefthand = fields[1]
				count = fields[2]
				self.nonterminalCount[lefthand] = int(count)
		f.close()
		return self.binaryProb, self.unaryProb, self.nonterminalCount




if __name__ == "__main__": 
  fileName = sys.argv[1]
  probBuilder = ProbBuilder()
  binaryProb, unaryProb, nonterminalCount = probBuilder.readCount(fileName)
  parser = Parser(binaryProb, unaryProb, nonterminalCount)
  parser.CKY("the man saw the dog with the telescope")
  
