from pymongo import MongoClient
from datetime import datetime
import random
import string

class DB:
    def __init__(self) -> None:
        try:
            self.client = MongoClient(
                'mongodb+srv://nimpoAdmin:nimpoPass@cluster0.he1vjgo.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true'
            )
            self.db = self.client.nimpo_db
            self.chatsCollection = self.db.chats
        except Exception as e:
            print("Could not connect to MongoDB:", e)
            raise

    def generate_unique_code(self):
        """Generate a unique code for user identification."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


    def addAdmin(self, chat_id, username):
        chat = self.chatsCollection.find_one({"_id": chat_id})
        if(not chat):
            unique_code = self.generate_unique_code()
            chat = {
                "_id": chat_id,
                "admin_username": username,
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

    # def addOperatorToChat(self, chatId, operator_username, operator_chatId):
    #     self.chatsCollection.update_one(
    #         {"_id": chatId},
    #         {"$set": {f"operators.{operator_username}": operator_chatId}, "$setOnInsert": {"created_at": datetime.now()}},
    #         upsert=True
    #     )

    def addOperatorToChat(self, chatId, operator_username, operator_chatId):
        chat = self.chatsCollection.find_one({"_id": chatId})

        if chat:
            # Operator exists, update its value
            result = self.chatsCollection.update_one(
                {"_id": chatId},
                {
                    "$set": {
                        f"operators.{operator_username}": operator_chatId,
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