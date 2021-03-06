#! /usr/bin/env python
"""
Copyright (C) 2014 CompleteDB LLC.

This program is free software: you can redistribute it and/or modify
it under the terms of the Apache License Version 2.0 http://www.apache.org/licenses.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

import unittest
import time
from pubsubsql import Client

class TestClient(unittest.TestCase):
    """MAKE SURE TO RUN PUBSUBSQL SERVER!"""

    def __ADDRESS(self):
        return "localhost:7777"

    def __ROWS(self):
        return 3

    def __COLUMNS(self):
        # including id
        return 4

    def __generateTableName(self):
        return "T" + str(int(round(time.time() * 1000)))

    def __insertRow(self, tableName):
        client = Client()
        client.connect(self.__ADDRESS())
        command = "insert into {} (col1, col2, col3) values (1:col1, 1:col2, 1:col3)".format(tableName)
        client.execute(command)
        client.disconnect()

    def __insertRows(self, tableName):
        client = Client()
        client.connect(self.__ADDRESS())
        for row in range(self.__ROWS()):
            command = "insert into {} (col1, col2, col3) values ({}:col1, {}:col2, {}:col3)".format(tableName, row, row, row)
            client.execute(command)
        client.disconnect()

    def __checkPubsubResultSet(self, client, pubsubId, action, rows, columns):
        readRows = 0
        while readRows < rows:
            self.assertTrue(client.waitForPubSub(100), "expected {} rows but got {}".format(rows, readRows))
            self.assertNotEqual("", client.getPubSubId())
            self.assertEqual(action, client.getAction())
            while client.nextRow():
                readRows += 1
                self.assertEqual(client.getColumnCount(), columns)
                for col in range(columns):
                    self.assertTrue(client.getValue(col))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConnectDisconnect(self):
        client = Client()
        #
        client.connect(self.__ADDRESS())
        self.assertTrue(client.isConnected())
        client.disconnect()
        #
        with self.assertRaises(Exception):
            client.connect("addresswithnoport")
        self.assertFalse(client.isConnected())
        client.disconnect()
        #
        with self.assertRaises(Exception):
            client.connect("addresswithnoport:")
        self.assertFalse(client.isConnected())
        client.disconnect()
        #
        with self.assertRaises(Exception):
            client.connect("localhost:7778")
        self.assertFalse(client.isConnected())
        client.disconnect()

    def testExecuteStatus(self):
        client = Client()
        client.connect(self.__ADDRESS())
        #
        client.execute("status")
        self.assertEqual("status", client.getAction())
        client.disconnect()

    def testExecuteInvalidCommand(self):
        client = Client()
        client.connect(self.__ADDRESS())
        #
        with self.assertRaises(Exception):
            client.execute("blablabla")

    def testInsertOneRow(self):
        client = Client()
        client.connect(self.__ADDRESS())
        tableName = self.__generateTableName()
        command = "insert into {} (col1, col2, col3) values (1:col1, 1:col2, 1:col3) returning *".format(tableName)
        #
        client.execute(command)
        self.assertEqual("insert", client.getAction())
        self.assertEqual(1, client.getRowCount())
        self.assertTrue(client.nextRow())
        #
        self.assertNotEqual("", client.getValue("id"))
        self.assertEqual("1:col1", client.getValue("col1"))
        self.assertEqual("1:col2", client.getValue("col2"))
        self.assertEqual("1:col3", client.getValue("col3"))
        self.assertTrue(client.hasColumn("col1"))
        self.assertTrue(client.hasColumn("col2"))
        self.assertTrue(client.hasColumn("col3"))
        self.assertEqual(4, client.getColumnCount()) # including id
        #
        self.assertFalse(client.nextRow())
        client.disconnect()

    def testInsertManyRow(self):
        client = Client()
        client.connect(self.__ADDRESS())
        tableName = self.__generateTableName()
        command = "insert into {} (col1, col2, col3) values (1:col1, 1:col2, 1:col3) returning *".format(tableName)
        for _ in range(self.__ROWS()):
            client.execute(command)
            self.assertEqual("insert", client.getAction())
            self.assertEqual(1, client.getRowCount())
            self.assertTrue(client.nextRow())
            #
            self.assertNotEqual("", client.getValue("id"))
            self.assertEqual("1:col1", client.getValue("col1"))
            self.assertEqual("1:col2", client.getValue("col2"))
            self.assertEqual("1:col3", client.getValue("col3"))
            self.assertTrue(client.hasColumn("col1"))
            self.assertTrue(client.hasColumn("col2"))
            self.assertTrue(client.hasColumn("col3"))
            self.assertEqual(4, client.getColumnCount()) # including id
            #
            self.assertFalse(client.nextRow())
        client.disconnect()

    def testSelectOneRow(self):
        tableName = self.__generateTableName()
        self.__insertRow(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        # select one row
        command = "select * from {}".format(tableName)
        client.execute(command)
        self.assertEqual("select", client.getAction())
        self.assertEqual(1, client.getRowCount())
        self.assertTrue(client.nextRow())
        #
        self.assertNotEqual("", client.getValue("id"))
        self.assertEqual("1:col1", client.getValue("col1"))
        self.assertEqual("1:col2", client.getValue("col2"))
        self.assertEqual("1:col3", client.getValue("col3"))
        self.assertTrue(client.hasColumn("col1"))
        self.assertTrue(client.hasColumn("col2"))
        self.assertTrue(client.hasColumn("col3"))
        self.assertEqual(4, client.getColumnCount()) # including id
        #
        self.assertFalse(client.nextRow())
        client.disconnect()

    def testSelectManyRows(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        # select one row
        command = "select * from {}".format(tableName)
        client.execute(command)
        self.assertEqual("select", client.getAction())
        self.assertEqual(self.__ROWS(), client.getRowCount())
        for row in range(self.__ROWS()):
            self.assertTrue(client.nextRow())
            self.assertNotEqual("", client.getValue("id"))
            self.assertEqual("{}:col1".format(row), client.getValue("col1"))
            self.assertEqual("{}:col2".format(row), client.getValue("col2"))
            self.assertEqual("{}:col3".format(row), client.getValue("col3"))
            self.assertTrue(client.hasColumn("col1"))
            self.assertTrue(client.hasColumn("col2"))
            self.assertTrue(client.hasColumn("col3"))
            self.assertEqual(4, client.getColumnCount()) # including id
        #
        self.assertFalse(client.nextRow())
        client.disconnect()

    def testUpdateOneRow(self):
        tableName = self.__generateTableName()
        self.__insertRow(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "update {} set col1 = newvalue".format(tableName)
        client.execute(command)
        self.assertEqual("update", client.getAction())
        self.assertEqual(1, client.getRowCount())
        client.disconnect()

    def testUpdateManyRow(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "update {} set col1 = newvalue".format(tableName)
        client.execute(command)
        self.assertEqual("update", client.getAction())
        self.assertEqual(self.__ROWS(), client.getRowCount())
        client.disconnect()

    def testDeleteOneRow(self):
        tableName = self.__generateTableName()
        self.__insertRow(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "delete from {}".format(tableName)
        client.execute(command)
        self.assertEqual("delete", client.getAction())
        self.assertEqual(1, client.getRowCount())
        client.disconnect()
    
    def testDeleteManyRow(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "delete from {}".format(tableName)
        client.execute(command)
        self.assertEqual("delete", client.getAction())
        self.assertEqual(self.__ROWS(), client.getRowCount())
        client.disconnect()
    
    def testKey(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "key {} col1".format(tableName)
        client.execute(command)
        self.assertEqual("key", client.getAction())
        client.disconnect()
    
    def testTag(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        #
        client = Client()
        client.connect(self.__ADDRESS())
        command = "tag {} col1".format(tableName)
        client.execute(command)
        self.assertEqual("tag", client.getAction())
        client.disconnect()
    
    def testSubscribeUnsubscribe(self):
        client = Client()
        client.connect(self.__ADDRESS())
        tableName = self.__generateTableName()
        command = "subscribe * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # unsubscribe
        command = "unsubscribe from {}".format(tableName)
        client.execute(command)
        self.assertEqual("unsubscribe", client.getAction())
        #
        client.disconnect()
    
    def testSubscribeUnsubscribeByPubSubId(self):
        client = Client()
        client.connect(self.__ADDRESS())
        tableName = self.__generateTableName()
        command = "subscribe * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # unsubscribe
        command = "unsubscribe from {} where pubsubid = {}".format(tableName, client.getPubSubId())
        client.execute(command)
        self.assertEqual("unsubscribe", client.getAction())
        #
        client.disconnect()
    
    def testPubSubTimeout(self):
        client = Client()
        client.connect(self.__ADDRESS())
        self.assertFalse(client.waitForPubSub(10))
    
    def testSubscribeSkip(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        client = Client()
        client.connect(self.__ADDRESS())
        command = "subscribe skip * from {}".format(tableName)
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertFalse(client.waitForPubSub(10))
        client.disconnect()
    
    def testPubSubAddOnSubscribe(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        client = Client()
        client.connect(self.__ADDRESS())
        command = "subscribe * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # pubsub add
        pubsubId = client.getPubSubId()
        self.__checkPubsubResultSet(client, pubsubId, "add", self.__ROWS(), self.__COLUMNS())
        client.disconnect()

    def testPubSubInsert(self):
        tableName = self.__generateTableName()
        client = Client()
        client.connect(self.__ADDRESS())
        command = "subscribe * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # generate insert event
        self.__insertRows(tableName)
        # pubsub insert
        self.__checkPubsubResultSet(client, client.getPubSubId, "insert", self.__ROWS(), self.__COLUMNS())
        client.disconnect()
    
    def testPubSubUpdate(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        client = Client()
        client.connect(self.__ADDRESS())
        command = "subscribe skip * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # generate update event
        command = "update {} set col1 = newvalue".format(tableName)
        client.execute(command)
        self.assertEqual(self.__ROWS(), client.getRowCount())
        # expected id and updated column (col1)
        self.__checkPubsubResultSet(client, client.getPubSubId, "update", self.__ROWS(), 2)
        client.disconnect()

    def testPubSubDelete(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        client = Client()
        client.connect(self.__ADDRESS())
        command = "subscribe skip * from {}".format(tableName)
        # subscribe
        client.execute(command)
        self.assertEqual("subscribe", client.getAction())
        self.assertNotEqual("", client.getPubSubId())
        # generate insert event
        command = "delete from {}".format(tableName)
        client.execute(command)
        self.assertEqual(self.__ROWS(), client.getRowCount())
        # expected id and updated column (col1)
        self.__checkPubsubResultSet(client, client.getPubSubId, "delete", self.__ROWS(), self.__COLUMNS())
        client.disconnect()
        
    def testPubSubRemove(self):
        tableName = self.__generateTableName()
        self.__insertRows(tableName)
        client = Client()
        client.connect(self.__ADDRESS())
        # key col1
        command = "key {} col1".format(tableName)
        client.execute(command)
        command = "subscribe skip * from {} where col1 = 1:col1".format(tableName)
        client.execute(command)
        # generate remove
        command = "update {} set col1 = newvalue where col1 = 1:col1".format(tableName)
        client.execute(command)
        self.__checkPubsubResultSet(client, client.getPubSubId, "remove", 1, self.__COLUMNS())
        client.disconnect()
        
if __name__ == "__main__":
    unittest.main()
