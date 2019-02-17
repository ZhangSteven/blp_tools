# coding=utf-8
# 
# Read XML trade files from Bloomberg, then:
# 
# 1. Count the total number of trades each month.
# 2. Count the number of trades for a specific portfolio in each month.
# 



import xml.etree.ElementTree as ET
from os.path import join
from datetime import datetime
from functools import reduce, partial
from utils.file import stripPath, getFiles
from utils.utility import writeCsv
from utils.xml4me import findWithoutNamespace, stripNamespace
from utils.iter import numElements
from blp_tools.utility import getInputDirectory
import logging
import re
logger = logging.getLogger(__name__)



def tradeTable(files, portfolio):
	"""
	[List] files => [Dict] a dictionary containing the following:

	month: (# trades, # trades of certain portfolio), e.g.

	'2018-01': (5588, 123)
	'2018-02': (6789, 456)

	"""
	def buildTable(result, tradeInfo):
		date, nTrades, nTradesForPortfolio = tradeInfo
		month = date.strftime('%Y-%m')
		if not month in result:
			result[month] = (0, 0)	# create new entry

		n1, n2 = result[month]
		result[month] = (n1 + nTrades, n2 + nTradesForPortfolio)
		return result


	return reduce(buildTable, map(partial(tradeInfo, portfolio), files), {})



def tradeInfo(portfolio, file):
	"""
	[String] portfolio, [String] file => [Tuple] (datetime, int, int):

		[datetime] datetime of the trade file,
		[int] number of trades in total,
		[int] number of trades for that portfolio
	"""
	nTrades, nTradesForPortfolio = numTrades(file, portfolio)
	return (dateFromFilename(file), nTrades, nTradesForPortfolio)



def dateFromFilename(file):
	"""
	[String] file => [datetime] date of the file from its name.

	Where the file may looks like: TransToGeneva20190207.xml
	"""
	return datetime.strptime(stripPath(file).split('.')[0][-8:], '%Y%m%d')



def numTrades(file, portfolio):
	"""
	[String] file, [String] portfolio => a tuple (int, int) consisting of 
		[int] number of trades in total,
		[int] number of trades for that portfolio

	Return the total number of trades in that file if portfolio is "None",
	otherwise the number of trades for that particular portfolio.
	"""
	nodes = transactions(file)
	return (numElements(filter(trade, nodes)) \
			, numElements(filter(partial(forPortfolio, portfolio) \
								 , filter(trade, nodes)))
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
	logger.info('transactions(): process file {0}'.format(file))
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
	# print(tag)
	if stripNamespace(transaction.tag) in [ 'Buy_New', 'Sell_New' \
										  , 'SellShort_New', 'CoverShort_New']:
		return True
	else:
		return False



def forPortfolio(portId, transaction):
	"""
	[String] portId => [Bool] whether a transaction has the portfolio id.

	A transaction with "Portfolio" sub element looks like:

		<SellShort_New>
			<Portfolio>40006-C</Portfolio>
			...
		</SellShort_New>
	"""
	portfolio = findWithoutNamespace(transaction, 'Portfolio')
	if portfolio != None and portfolio.text.startswith(portId):
		return True
	else:
		return False



def toList(tradeTable):
	"""
	[Dict] tradeTable => [List] tuple (month, # trades, # trades portfolio)

	Where tradeTable is a dictonary like:

	'2018-01': (5588, 123)
	'2018-02': (6789, 456)
	"""
	return [(key, value[0], value[1]) for key, value in tradeTable.items()]



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	"""
	To use the program, put Bloomberg XML trade files into a folder (specified 
	in the config file), then run:

		$python trade.py
		
	"""
	writeCsv('result.csv'
			, sorted(toList(tradeTable(getFiles(getInputDirectory(), True) \
									  , '40006'))))

