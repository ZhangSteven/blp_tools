# coding=utf-8
# 
# Look into XML trade files generated by Bloomberg, then:
# 
# 1. Count the total number of trades each month.
# 2. Count the number of trades for a specific portfolio in each month.
# 



import xml.etree.ElementTree as ET
from os.path import join
from datetime import datetime
from functools import reduce
import logging
import re
logger = logging.getLogger(__name__)



def numTrades(file, portfolio):
	"""
	[String] file, [String] portfolio => a tuple (int, int) consisting of 
		[int] number of trades in total,
		[int] number of trades for that portfolio

	Return the total number of trades in that file if portfolio is "None",
	otherwise the number of trades for that particular portfolio.
	"""
	def numElements(it):
		"""
		Count the number of elements in an interable (it).
		"""
		return sum([1 for _ in it])


	nodes = transactions(file)
	return (numElements(filter(trade, nodes)) \
			, numElements(filter(forPortfolio(portfolio, '{http://www.advent.com/SchemaRevLevel758/Geneva}')
								, filter(trade, nodes)
								)
						 )
			)



def transactions(file):
	"""
	[String] file => [ET root] the root node that contain all the transactions
						in the XML file.
	
	The XML file looks like below:

	<GenevaLoader xmlns=... >
		<TransactionRecords>
			<Buy_New>
				<Portfolio>30001</Portfolio>
				<KeyValue>000001</KeyValue>
				...
			</Buy_New>
			<SellShort_New>
				...
			</SellShort_New>
			...

		</TransactionRecords>
	</GenevaLoader>
	"""
	tree = ET.parse(file)
	root = tree.getroot()
	return root[0]	# the <TransactionRecords> element




def trade(transaction):
	""" 
	Tell whether a transaction node is a trade.

	A transaction tag may looks like:

	{http://www.advent.com/SchemaRevLevel758/Geneva}Buy_New

	Where {http://xxx} is the name space of the XML file, "Buy_New" is the
	transaction type.
	"""
	m = re.match('\{.*\}(.*)', transaction.tag)
	if m != None:
		tag = m.group(1)
	else:
		tag = transaction.tag

	# print(tag)
	if tag in ['Buy_New', 'Sell_New', 'SellShort_New', 'CoverShort_New']:
		return True
	else:
		return False



def forPortfolio(portId, xmlns):
	"""
	[String] portfolio id => [Function] a function that checks whether a 
							 transaction has the portfolio id.

	This may look a bit weird, but the returned function will be used to
	filter transactions based on portfolio id. 
	"""
	def _forPortfolio(transaction):
		"""
		[ET node] transaction => [Bool] yesno

		the transaction looks like follows:

		<SellShort_New>
			<Portfolio>40006-C</Portfolio>
			...
		</SellShort_New>

		We need to find out whether the "Portfolio" matches what we look for.
		"""
		portfolio = transaction.find(xmlns + 'Portfolio')
		if portfolio != None and portfolio.text.startswith(portId):
			return True
		else:
			return False


	return _forPortfolio



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('file', metavar='<input file>', type=str)
	args = parser.parse_args()

	print(numTrades(args.file, '40006'))
