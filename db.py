from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string
from dotenv import load_dotenv
import os

class DB:
    def __init__(self) -> None:
        load_dotenv()
        MONGO_URI = os.getenv("MONGO_URI")
        try:
            self.client = MongoClient(
                'mongodb+srv://nimpoAdmin:nimpoPass@cluster0.he1vjgo.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true'
            )
            self.db = self.client.nimpo_db
            self.chatsCollection = self.db.chats
            self.usersCollection = self.db.users
        except Exception as e:
            print("Could not connect to MongoDB:", e)
            raise

    def generate_unique_code(self):
        """Generate a unique code for user identification."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


    def addAdmin(self, chat_id, username, name):
        chat = self.chatsCollection.find_one({"_id": chat_id})
        if(not chat):
            unique_code = self.generate_unique_code()
            chat = {
                "_id": chat_id,
                "admin": {
                    "username": username,
                    "name": name
                },
                "unique_code": unique_code,
                "chat_name": "",
                "description": "",
                "operators": {},
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            try:
                self.chatsCollection.update_one(
                    {"_id": chat_id},
                    {"$set": chat},
                    upsert=True
                )
            except Exception as e:
                print("Error adding admin:", e)

    def updateChatName(self, chat_id, chat_name):
        try:
            self.chatsCollection.update_one(
                {"_id": chat_id},
                {"$set": {"chat_name": chat_name, "updated_at": datetime.now()}},
                upsert=True
            )
        except Exception as e:
            print("Error updating chat name:", e)

    def updateChatDescription(self, chat_id, chat_desc):
        try:
            self.chatsCollection.update_one(
                {"_id": chat_id},
                {"$set": {"description": chat_desc, "updated_at": datetime.now()}},
                upsert=True
            )
        except Exception as e:
            print("Error updating chat description:", e)

    def updateFirstMessage(self, chat_id, msg):
        try:
            self.chatsCollection.update_one(
                {"_id": chat_id},
                {"$set": {"greeting": msg, "updated_at": datetime.now()}},
                upsert=True
            )
        except Exception as e:
            print("Error updating chat description:", e)

    def addOperatorToChat(self, chatId: int, operator_username: string, operator_chatId: int, operator_name: string):
        chat = self.chatsCollection.find_one({"_id": chatId})

        if chat:
            # Operator exists, update its value
            result = self.chatsCollection.update_one(
                {"_id": chatId},
                {
                    "$set": {
                        f"operators.{operator_chatId}": {
                            "operator_username": operator_username,
                            "operator_name": operator_name
                        },
                        "updated_at": datetime.now()
                    }
                }
            )

            if result.matched_count > 0:
                print(f"Successfully updated operator {operator_username} with chat ID {operator_chatId}.")
            else:
                print("Failed to update the operator.")
        else:
            print(f"No chat found with id {chatId}.")

    def updateOperatorNameById(self, chatId: int, operator_chatId: int, newName: string):
        chat = self.chatsCollection.find_one({"_id": chatId})

        if chat:
            # Operator exists, update its value
            result = self.chatsCollection.update_one(
                {"_id": chatId},
                {
                    "$set": {
                        f"operators.{operator_chatId}.operator_name": newName,
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {
                        f"operators.{operator_chatId}.operator_username": "None"  # Default value or any other initialization
                    }
                },
                upsert=True
            )

            if chatId == int(operator_chatId):
                self.chatsCollection.update_one(
                    {"_id": chatId},
                    {
                        "$set": {
                            "admin.name": newName,
                            "updated_at": datetime.now()
                        }
                    },
                    upsert=True
                )

            if result.matched_count > 0:
                print(f"Successfully updated operator {newName} with chat ID {operator_chatId}.")
                return True
            else:
                print("Failed to update the operator.")
                return False
        else:
            print(f"No chat found with id {chatId}.")
            return False

    def getOperatorNameById(self, chatId: int, operator_chatId: int):
        chat = self.chatsCollection.find_one({"_id": chatId})
        if chat and "operators" in chat and operator_chatId in chat["operators"]:
            return chat["operators"][operator_chatId].get("operator_name")
        return None

    def removeOperator(self, chatId, operator_username):
        chat = self.chatsCollection.find_one({'_id': chatId})
        if chat:
            # Operator exists, update its value
            result = self.chatsCollection.update_one(
                {"_id": chatId},
                {
                    "$unset": {
                        f"operators.{operator_username}": 1,
                        "updated_at": datetime.now()
                    }
                }
            )

            if result.matched_count > 0:
                print(f"Successfully updated operator list.")
                return True
            else:
                print("Failed to update the operator.")
                return False
        else:
            print(f"No operator with username {operator_username} found in chat {chatId}.")

    def getChatConfig(self, chat_id):
        try:
            chat_config = self.chatsCollection.find_one({"_id": chat_id})
            return chat_config
        except Exception as e:
            print("Error getting chat config:", e)
            return None

    def getChatByCode(self, user_code):
        return self.chatsCollection.find_one({"unique_code": user_code})
    
    def setUser(self, chat_id, unique_code, plan, planDuration):
        user = self.usersCollection.find_one({"_id": chat_id})
        if(not user):
            user = {
                "_id": chat_id,
                "plan": plan,
                "unique_code": unique_code,
                "until": datetime.now() + timedelta(days=planDuration),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            try:
                self.usersCollection.update_one(
                    {"_id": chat_id},
                    {"$set": user},
                    upsert=True
                )
            except Exception as e:
                print("Error adding admin:", e)
        
    def getUserByCode(self, user_code):
        return self.usersCollection.find_one({"unique_code": user_code})