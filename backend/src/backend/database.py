from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("MONGODB_PASSWORD")

uri = f"mongodb+srv://kevin:{password}@cluster0.wpa355p.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(
    uri, 
    server_api=ServerApi('1'),
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["WinProbDB"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)