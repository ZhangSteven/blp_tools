# coding=utf-8
# 

import unittest2
from os.path import join
from blp_trade.utility import get_current_path
from blp_trade.blp import extractTradesToXML, extractOtherToXML, isTrade, \
                            isDeletion, addRemoveHeader, fileToLines
from blp_trade.db import setDatabaseMode, clearTestDatabase, closeConnection
import xml.etree.ElementTree as ET


class TestBlp(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBlp, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        """
        Before starting the tests, let's set database to test mode and
        clear its contents.

        Run only once before all tests.
        """
        setDatabaseMode('test')
        clearTestDatabase()


    @classmethod
    def tearDownClass(cls):
        """
        Close connection. Run only once after all tests.
        """
        closeConnection()



    def testFile1(self):
        inputFile = join(get_current_path(), 'samples', 'test1.xml')
        outputTrade = join(get_current_path(), 'samples', 'output_trade1.xml')
        outputOther = join(get_current_path(), 'samples', 'output_other1.xml')
        extractTradesToXML(inputFile, outputTrade)
        extractOtherToXML(inputFile, outputOther)
        self.assertEqual(['000002', '000005', '000006'], list(extractTradeKeys(outputTrade)))
        self.assertEqual(['000002'], list(extractDeletionKeys(outputTrade)))
        self.assertEqual(['000001', '000003', '000004'], list(extractTradeKeys(outputOther)))
        self.assertEqual(['000001', '123256', '123254'], list(extractDeletionKeys(outputOther)))




    def testFile2(self):
        """
        test2.xml is a super set of test1.xml, with more trades and deletions.

        But after testFile1() is called, outputTrade file should just reflect
        the incremental 40006 trades and deletions, outputOther file should 
        still reflect everything else, i.e., a super set of outputOther in
        testFile1().
        """
        inputFile = join(get_current_path(), 'samples', 'test2.xml')
        outputTrade = join(get_current_path(), 'samples', 'output_trade2.xml')
        outputOther = join(get_current_path(), 'samples', 'output_other2.xml')
        extractTradesToXML(inputFile, outputTrade)
        extractOtherToXML(inputFile, outputOther)
        self.assertEqual(['000008'], list(extractTradeKeys(outputTrade)))
        self.assertEqual(['000008', '000005'], list(extractDeletionKeys(outputTrade)))
        self.assertEqual(['000001', '000003', '000004', '000007'], list(extractTradeKeys(outputOther)))
        self.assertEqual(['000001', '123256', '123254', '000003'], list(extractDeletionKeys(outputOther)))




def keyValue(transaction):
    """
    [ET node] transaction => [String] key value of that transaction.

    A transaction can be a trade or trade deletion, both have a key value.
    """
    return transaction.find('KeyValue').text



def extractTradeKeys(file):
    """
    [String] full path of XML file => [Iterable] key values of trades
    """
    return map(keyValue
               , filter(isTrade
                        , ET.fromstringlist(addRemoveHeader(fileToLines(file)))))



def extractDeletionKeys(file):
    """
    [String] full path of XML file => [Iterable] key values of trades
    """
    return map(keyValue
               , filter(isDeletion
                        , ET.fromstringlist(addRemoveHeader(fileToLines(file)))))

