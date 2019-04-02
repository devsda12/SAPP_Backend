import string
import random
import mysql.connector
import datetime
import firebase_Handler
from flask import request

class database_Handlers:

    def __init__(self):

        #Declaring the global database handler and its cursor
        self.sapp_database = mysql.connector.connect(host="localhost", user="sapp_user", passwd="SAPP-PASSWORD_F0R-YOU", database="SAPP_Backend")
        self.sapp_cursor = self.sapp_database.cursor(buffered=True)

    #The device identification database function
    def identifyDevice(self, requestContent):
        requestedId = requestContent["device_Id"]

        if requestedId != "0":
            self.sapp_cursor.execute('SELECT device_Id FROM Device_Table WHERE device_Id = "' + requestedId + '";')
            result = self.sapp_cursor.fetchall()
            if len(result) > 0:
                return result[0][0]

        inserted = False
        while not inserted:
            new_id = self.id_generator()
            self.sapp_cursor.execute('SELECT device_Id FROM Device_Table WHERE device_Id = "' + new_id + '";')
            result = self.sapp_cursor.fetchall()
            if len(result) == 0:
                self.sapp_cursor.execute('INSERT INTO Device_Table (device_Id) VALUES ("' + new_id + '");')
                self.sapp_database.commit()
                inserted = True

        return new_id


    #The login database function
    def login(self, requestContent):
        requestedUsername = requestContent["acc_Username"]
        requestedPassword = requestContent["acc_Password"]

        #Using query on the database
        self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Username = "' + requestedUsername + '" AND acc_Password = "' + requestedPassword + '";')
        result = self.sapp_cursor.fetchall()

        if len(result) == 0:
            return False
        else:
            requestedId = result[0][0]
            return requestedId


    #The create account database function
    def create_Account(self, requestContent):
        requestedUsername = requestContent["acc_Username"]
        requestedPassword = requestContent["acc_Password"]

        #Querying the database to see if username already exists
        self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Username = "' + requestedUsername + '";')
        result = self.sapp_cursor.fetchall()

        #If this username exists it is rejected
        if len(result) > 0:
            return False

        #If the username does not yet exist it is inserted into the database
        inserted = False
        while not inserted:
            newAcc_Id = self.id_generator()
            self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Id = "' + newAcc_Id + '";')
            result = self.sapp_cursor.fetchall()
            if len(result) == 0:
                self.sapp_cursor.execute('INSERT INTO Acc_Table (acc_Id, acc_Username, acc_Password) VALUES ("' + newAcc_Id + '", "' + requestedUsername + '", "' + requestedPassword + '");')
                self.sapp_database.commit()
                inserted = True

        return newAcc_Id


    #Requesting chats database function V2
    def getChatsV2(self, requestContent):
        chatsDict = {}
        requestedAccId = requestContent[0]["acc_Id"]

        #Getting all conv_id's from the conv_Table
        self.sapp_cursor.execute('SELECT conv_Id from Conv_Table;')
        result = self.sapp_cursor.fetchall()

        #Determine if requested acc_Id in one of the id's (OLD VERSION)
        for item in result:
            if item[0][0:10] == requestedAccId:
                #Getting details from the conv_table
                self.sapp_cursor.execute('SELECT conv_LastMessage, conv_LastMessageSender, conv_LastMessageDate FROM Conv_Table WHERE conv_Id = "' + item[0] + '";')
                detailsResult = self.sapp_cursor.fetchall()

                #Getting details of the partner username
                self.sapp_cursor.execute('SELECT acc_Username FROM Acc_Table WHERE acc_Id = "' + item[0][10:20] + '";')
                partnerResult = self.sapp_cursor.fetchall()

                #Writing all the information to the dictionary in format dic[tablename] = [lastmessage, lastmessageSender, lastMessageDate, partnername]
                chatsDict[item[0]] = [item[0][10:20], partnerResult[0][0], detailsResult[0][0], detailsResult[0][1], detailsResult[0][2]]
            elif item[0][10:20] == requestedAccId:
                # Getting details from the conv_table
                self.sapp_cursor.execute('SELECT conv_LastMessage, conv_LastMessageSender, conv_LastMessageDate FROM Conv_Table WHERE conv_Id = "' + item[0] + '";')
                detailsResult = self.sapp_cursor.fetchall()

                # Getting details of the partner username
                self.sapp_cursor.execute('SELECT acc_Username FROM Acc_Table WHERE acc_Id = "' + item[0][0:10] + '";')
                partnerResult = self.sapp_cursor.fetchall()

                # Writing all the information to the dictionary in format dic[tablename] = [lastmessage, lastmessageSender, lastMessageDate, partnername]
                chatsDict[item[0]] = [item[0][0:10], partnerResult[0][0], detailsResult[0][0], detailsResult[0][1], detailsResult[0][2]]

        #Checking whether the dict is empty
        if len(chatsDict) == 0:
            return False
        else:
            return chatsDict


    # Requesting chats database function V3
    def getChatsV3(self, requestContent):
        chatsDict = {}
        requestedAccId = requestContent[0]["acc_Id"]

        # Getting all conv_id's from the conv_Table
        self.sapp_cursor.execute('SELECT conv_Id from Conv_Table;')
        result = self.sapp_cursor.fetchall()

        # Determine if requested acc_Id in one of the id's (NEW VERSION)
        for item in result:
            tempSplitList = [item[0][i:i + 10] for i in range(0, len(item[0]), 10)]
            for index, tenPart in enumerate(tempSplitList):
                # Als een van de gedeelten van 10 chars overeenkomt met het gegeven acc_Id
                if tenPart == requestedAccId:
                    # Als de lengte van de totale lijst minder of gelijk is aan 2. Oftewel het is een gesprek tussen 2 personen
                    if len(tempSplitList) <= 2:
                        # Als het de eerste index is van de tempSplitList dan is de tweede de partner en andersom
                        if index == 0:
                            tempPartnerId = tempSplitList[1]
                        else:
                            tempPartnerId = tempSplitList[0]

                        #Nu wordt de partner informatie opgehaald van de db
                        self.sapp_cursor.execute('SELECT acc_Username FROM Acc_Table WHERE acc_Id = "' + tempPartnerId + '";')
                        partnerResult = self.sapp_cursor.fetchall()
                    else:
                        doSomethingToFetchGroupConversationInfo = ""

                    #Nu wordt de overige informatie van het gesprek uit de db gehaald
                    self.sapp_cursor.execute('SELECT conv_LastMessage, conv_LastMessageSender, conv_LastMessageDate FROM Conv_Table WHERE conv_Id = "' + item[0] + '";')
                    detailsResult = self.sapp_cursor.fetchall()

                    # Writing all the information to the dictionary in format dic[tablename] = [partner_Id, partner_Username, lastMessage, messageSender, messageDate]
                    chatsDict[item[0]] = [tempPartnerId, partnerResult[0][0], detailsResult[0][0], detailsResult[0][1], detailsResult[0][2]]

        # Checking whether the dict is empty
        if len(chatsDict) == 0:
            return False
        else:
            return chatsDict


    # Searching for users in the database
    def findUser(self, requestContent):
        foundUsers = {}
        request_Username = requestContent[0]["acc_Username"]

        self.sapp_cursor.execute('SELECT acc_Username, acc_Id FROM Acc_Table WHERE acc_Username LIKE "%' + request_Username + '%";')
        result = self.sapp_cursor.fetchall()
        for item in result:
            foundUsers[item[0]] = item[1]

        # Checking whether the dict is empty
        if len(foundUsers) == 0:
            return False
        else:
            return foundUsers


    # creating new conversation table
    def createTable(self, requestContent):
        requestpartner_id = requestContent["partner_Id"]
        requestaccount_id = requestContent["acc_Id"]

        #Catching the creation if the two requested id's are the same
        if requestaccount_id == requestpartner_id:
            return False

        # creating name for the conversation (partner id still has to be defined)
        newTableName = requestaccount_id + requestpartner_id

        self.sapp_cursor.execute('SHOW TABLES')
        result = self.sapp_cursor.fetchall()

        if any(newTableName in item for item in result):
            return False
        else:
            self.sapp_cursor.execute('CREATE TABLE ' + newTableName + ' (Sender Text, Receiver Text, Message Text, DateTime Datetime);')
            self.sapp_cursor.execute('INSERT INTO Conv_Table (conv_Id, conv_LastMessage, conv_LastMessageSender, conv_LastMessageDate) VALUES ("' + newTableName + '", Null, Null, Null);')
            self.sapp_database.commit()
            return True


    # Retrieve messages of a chat
    def getCompleteChat(self, requestContent):
        chatDict = {}
        requestconv_id = requestContent[0]["conv_Id"]

        self.sapp_cursor.execute('SELECT * FROM ' + requestconv_id + ';')
        result = self.sapp_cursor.fetchall()

        i = 0
        for item in result:
            chatDict[i] = [item[0], item[1], item[2], item[3]]
            i += 1

        # Checking whether the dict is empty
        if len(chatDict) == 0:
            return False
        else:
            return chatDict


    # Creer hier nog een functie die alle berichten van een bepaalde tabel ophaald die geplaatst zijn na een bepaalde datetime.
    def getPartialChat(self, requestContent):
        requestDateTime = requestContent[0]["lastMessageDate"]
        requestconv_id = requestContent[0]["conv_Id"]
        chatDict = {}

        self.sapp_cursor.execute('SELECT * FROM ' + requestconv_id + ' WHERE DateTime > "' + requestDateTime + '";')
        result = self.sapp_cursor.fetchall()

        i = 0
        for item in result:
            chatDict[i] = [item[0], item[1], item[2], item[3]]
            i += 1

        print(chatDict)
        # Checking whether the dict is empty
        if len(chatDict) == 0:
            return False
        else:
            return chatDict


    # Clears a single chat of all messages
    def clearChat(self, requestContent):
        requestconv_id = requestContent["conv_Id"]

        self.sapp_cursor.execute('DELETE * FROM ' + requestconv_id + ';')

        return True


    # Add a message to conversation table
    def addMessage(self, requestContent):
        requestconv_id = requestContent["conv_Id"]
        requestSender = requestContent["Sender"]
        requestReceiver = requestContent["Receiver"]
        requestMessage = requestContent["Message"]
        requestDatetime = requestContent["DateTime"]

        #self.sapp_cursor.execute('SELECT CURRENT_TIMESTAMP();')
        #result = self.sapp_cursor.fetchone()

        self.sapp_cursor.execute('INSERT INTO ' + requestconv_id + ' (Sender, Receiver, Message, DateTime) '
                                                                   'VALUES ("' + requestSender + '", '
                                                                            '"' + requestReceiver + '", '
                                                                            '"' + requestMessage + '", '
                                                                            '"' + requestDatetime + '");')
        self.sapp_database.commit()

        self.sapp_cursor.execute('UPDATE Conv_Table '
                                 'SET conv_LastMessageSender = "' + requestSender + '", '
                                    'conv_LastMessage =  "' + requestMessage + '", '
                                    'conv_LastMessageDate = "' + requestDatetime + '" '
                                    'WHERE conv_Id = "' + requestconv_id + '";')
        self.sapp_database.commit()

        return True

    #NON primary database functions
    def fetchAccIdByUsername(self, username):
        self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Username = "' + username + '";')
        result = self.sapp_cursor.fetchall()
        return result[0][0]

    # request statistical data from database
    def requestStats(self):
        tempDict = {}
        self.sapp_cursor.execute('SELECT * FROM StatsTable;')
        result = self.sapp_cursor.fetchall()
        # The Format: {{10,2,1,'Monday'},{50,4,1,'Tuesday'}}

        for item in result:
            tempDict[3] = [item[0], item[1]]

        return tempDict

    # Add stat to database
    def addStat(self, Type):
        # Type will be given in the function that calls this functions
        # For example if addMessage calls this Type will be message

        # Check if its the same week
        self.sapp_cursor.execute('SELECT week FROM StatsTable')
        resultStatstWeek = self.sapp_cursor.fetchone()
        resultCurrentWeek = str(datetime.date.today().isocalendar()[1])

        if resultStatstWeek[0] != resultCurrentWeek:
            self.sapp_cursor.execute('UPDATE StatsTable SET logins = 0;')
            self.sapp_database.commit()
            self.sapp_cursor.execute('UPDATE StatsTable SET messages = 0;')
            self.sapp_database.commit()
            self.sapp_cursor.execute('UPDATE StatsTable SET week = ' + resultCurrentWeek + ';')
            self.sapp_database.commit()

        weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
        resultWeekDay = weekDays[datetime.date.today().weekday()]

        print('UPDATE StatsTable Set ' + Type + ' = ' + Type + ' + 1 WHERE weekday = "' + resultWeekDay + '";')
        self.sapp_database.commit()
        self.sapp_cursor.execute('UPDATE StatsTable Set ' + Type + ' = ' + Type + ' + 1 WHERE weekday = "' + resultWeekDay + '";')
        self.sapp_database.commit()


    # NON-database functions

    #Function to generate 10 digit ID
    def id_generator(self, size=10, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
