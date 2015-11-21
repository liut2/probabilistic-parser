import sys
import string
import operator
class Parser:
	def __init__(self, binaryProb, unaryProb, nonterminalCount):
		self.binaryProb = binaryProb
		self.unaryProb = unaryProb
		self.nonterminalCount = nonterminalCount

	def printTree(self, words, back, i, j, lefthand):
		#base case
		if (i == j):
			return [lefthand, words[i]]
		else:
			(k, righthand1, righthand2) = back[i][j][lefthand]
			return [lefthand, self.printTree(words, back, i, k, righthand1), self.printTree(words, back, k, j, righthand2)]



	def CKY(self, words):
		#split the sentence
		words = words.strip().split(" ")
		n = len(words)
		#init the table and the backpointer
		table = [[{} for i in range(n + 1)] for j in range(n + 1)]
		back = [[{} for i in range(n + 1)] for j in range(n + 1)]
		for j in range(1, len(words) + 1):
			ifUnknown = True
			terminal = words[j - 1]
			for lefthand in  self.nonterminalCount.keys():
				if (lefthand, terminal) in self.unaryProb:
					ifUnknown = False
					table[j - 1][j][lefthand] = self.unaryProb[lefthand, terminal]
			if ifUnknown:
				for lefthand in self.nonterminalCount.keys():
					table[j - 1][j][lefthand] = self.unaryProb[lefthand, "UNKNOWN"]
			for i in reversed(range(0, j - 1)):
				for k in range(i + 1, j):
					for (lefthand, righthand1, righthand2) in self.binaryProb:
						if righthand1 in table[i][k] and righthand2 in table[k][j]:
							prob = self.binaryProb[lefthand, righthand1, righthand2]*table[i][k][righthand1]*table[k][j][righthand2]
							if lefthand not in table[i][j]:
								table[i][j][lefthand] = prob
								back[i][j][lefthand] = (k, righthand1, righthand2)
							elif prob > table[i][j][lefthand]:
								table[i][j][lefthand] = prob
								back[i][j][lefthand] = (k, righthand1, righthand2)
		print(back)
		#if "S" in table[0][len(words)]:
		#	print(self.printTree(words, back, 0, len(words), "S"))


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
  parser.CKY("i like cats and dogs")
  
