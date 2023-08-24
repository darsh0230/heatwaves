from paho.mqtt import client as mqtt_client
import pymongo, random, json, math, asyncio
from telegram import Bot

BOT_TOKEN = "6442773979:AAEhZBu1_1qUxrubsZY0w0WP1YaKE5Kyz34"
bot = Bot(token=BOT_TOKEN)

message_sent = False

async def send_message_bot(chat_id, msg):
    await bot.send_message(chat_id=chat_id, text=msg)

broker = 'broker.emqx.io'
port = 1883
topic = "chur"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = '1234'
password = '1234'


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["heatwaves"]
deviceCollection = mydb["devices"]
userCollection = mydb["users"]



def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # print(msg.payload.decode())
        # print(msg.payload.decode())
        deviceId = msg.topic.split("/")[-1]
        jsondata = json.loads(msg.payload.decode())
        # print(deviceId, jsondata)

        deviceCollection.find_one_and_update({"deviceId": deviceId},
                                    {"$set": {
                                        "temperature": jsondata.get("temperature"),
                                        "max_temperature": jsondata.get("max_temperature"),
                                        "humidity":jsondata.get("humidity"),
                                        "uv_index":jsondata.get("uv_index"),
                                        "pressure":jsondata.get("pressure"),
                                        "latitude":jsondata.get("latitude"),
                                        "longitude":jsondata.get("longitude"),
                                        }},
                                    upsert=True)
        
        if jsondata.get("temperature") > jsondata.get("max_temperature"):

        # if jsondata.get("temperature") < jsondata.get("max_temperature"): return
            print("Sending alert")
        
            for user in userCollection.find():
                print(math.dist([1,2], [2, 3]))
                if math.dist([jsondata.get("latitude"), jsondata.get("longitude")], [user.get("latitude"), user.get("longitude")]) < 0.5:
                    
                    global message_sent
                    print("sending to user")
                    if user.get("teleChatId") and not message_sent:
                        asyncio.run(send_message_bot(chat_id=user.get("teleChatId"), msg="GTFO"))
                        message_sent = True
            
                


    client.subscribe(f"{topic}/#")
    client.on_message = on_message

client = connect_mqtt()
subscribe(client)
client.loop_forever()
