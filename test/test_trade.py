# coding=utf-8
# 

import unittest2
from blp_tools.trade import numTrades, tradeInfo, tradeTable
from blp_tools.utility import getCurrentDirectory
from os.path import join
from datetime import datetime



class TestTrade(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTrade, self).__init__(*args, **kwargs)


    def testFile(self):
        inputFile = join(getCurrentDirectory(), 'samples', 'test1.xml')
        self.assertEqual(numTrades(inputFile, '40006'), (6, 3))



    def testFile2(self):
        inputFile = join(getCurrentDirectory(), 'samples', 'test2.xml')
        self.assertEqual(numTrades(inputFile, '40006'), (8, 4))



    def testTradeInfo(self):
        func = tradeInfo('40006')
        inputFile = join(getCurrentDirectory(), 'samples', 'TransToGeneva20190207.xml')
        self.assertEqual(func(inputFile), (datetime(2019,2,7), 8, 4))



    def testTradeTable(self):
        file1 = join(getCurrentDirectory(), 'samples', 'TransToGeneva20190207.xml')
        file2 = join(getCurrentDirectory(), 'samples', 'TransToGeneva20190213.xml')
        file3 = join(getCurrentDirectory(), 'samples', 'TransToGeneva20190405.xml')
        table = tradeTable([file1, file2, file3], '40006')
        self.assertEqual(len(table), 2)
        self.assertEqual(table['201902'], (14, 7))  # (6, 3) + (8, 4)
        self.assertEqual(table['201904'], (8, 4))