from paho.mqtt import client as mqtt_client
import pymongo, random, json, math, asyncio
from telegram import Bot

BOT_TOKEN = "6442773979:AAEhZBu1_1qUxrubsZY0w0WP1YaKE5Kyz34"
bot = Bot(token=BOT_TOKEN)

message_sent = {}

async def send_message_bot(chat_id, msg):
    await bot.send_message(chat_id=chat_id, text=msg)

broker = 'broker.emqx.io'
port = 1883
topic = "chur"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = '1234'
password = '1234'


myclient = pymongo.MongoClient("mongodb+srv://dimenl:dimenl7768@cluster0.rmeqq.mongodb.net/")
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
        print(f"DeviceId : {deviceId} Temperature : {jsondata.get('temperature')}")

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
            
            print("Sending alert")
        
            for user in userCollection.find():
                if math.dist([jsondata.get("latitude"), jsondata.get("longitude")], [user.get("latitude"), user.get("longitude")]) < 0.3:
                    
                    global message_sent
                    print(message_sent)
                    if user.get("teleChatId") and not message_sent.get(deviceId):
                        message_sent[deviceId] = True
                        print("sending to user")
                        try:
                            asyncio.run(send_message_bot(chat_id=user.get("teleChatId"), msg=f"⚠️!!!!!WARNING!!!!!⚠️\nThere is high heat waves in your area. Please follow the following precautions:\n1. You can check that you are getting enough water by noting your urine color. Dark yellow may indicate you are not drinking enough.\n2. Avoid sugary, caffeinated and alcoholic drinks.\n3. If you are sweating a lot, combine water with snacks or a sports drink to replace the salt and minerals you lose in sweat.\n4. Talk to your doctor about how to prepare if you have a medical condition or are taking medicines.\n\nView the Heatmap in your area : https://heatwave-web.vercel.app/"))
                        except:
                            print("Tele fail to send alert")
                        # message_sent = True

            alertDevId = []
            for device in deviceCollection.find({"deviceId":{"$ne":deviceId}}):
                if math.dist([jsondata.get("latitude"), jsondata.get("longitude")], [device.get("latitude"), device.get("longitude")]) < 0.5 and device.get("temperature") > device.get("max_temperature"):
                    alertDevId.append(device.get(deviceId))
            
            for device in deviceCollection.find({"deviceId":{"$ne":deviceId}}):
                 if math.dist([jsondata.get("latitude"), jsondata.get("longitude")], [device.get("latitude"), device.get("longitude")]) < 0.5 and device.get("temperature") > device.get("max_temperature") and device.get(deviceId) not in alertDevId:
                    for user in userCollection.find():
                        if math.dist([device.get("latitude"), device.get("longitude")], [user.get("latitude"), user.get("longitude")]) < 0.5:
                            if user.get("teleChatId"):
                                try:
                                    asyncio.run(send_message_bot(chat_id=user.get("teleChatId"), msg="warning"))
                                except:
                                    print("Tele fail to send warning")
            

        elif message_sent.get(deviceId):
            message_sent[deviceId] = False
                    

            
                


    client.subscribe(f"{topic}/#")
    client.on_message = on_message

client = connect_mqtt()
subscribe(client)
client.loop_forever()
