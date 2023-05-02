import os, requests, zipfile, io
import pymongo
import matplotlib.pyplot as plt
from datetime import datetime, date
from requests_auth_aws_sigv4 import AWSSigV4
import secret

export_folder = './export'
items_sorted = {}

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["para"]
mycol = mydb["data"]

def export_para():
    if os.path.exists(export_folder) == False:
        print("Exporting Database...")
        aws_auth = AWSSigV4('para',
            aws_access_key_id=secret.access_key,
            aws_secret_access_key=secret.secret,
            aws_session_token='',
            region='us-east-1',
        )

        r = requests.get("https://paraio.com/v1/_export", stream=True, auth=aws_auth)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(export_folder)
    else:
        print("Skipping Export, remove folder 'export' to get the newest data")
    
    if ('data' in mydb.list_collection_names()):
        print("MongoDB collection 'data' exists, skipping import")
    else:
        for f in os.listdir(export_folder):
            os.system("mongoimport.exe --jsonArray --db para --collection data --file "+export_folder+"/"+f)
    pass

def get_data():
    dates = []
    spaces = {}
    kinds = {}
    
    mydoc = mycol.find({"$or":[ {"type":"question"}, {"type":"user"},{"type":"report"},{"type":"reply"}]})
    
    for x in mydoc:
        stmp = x['timestamp']
        dates.append(stmp)
        kinds[x['timestamp']] = x['type']
        if(x['type'] == "question"):
            spaces[x['timestamp']] = x['properties']['space'].split(":")[1]

    for x in sorted(dates):
        date_time = datetime.fromtimestamp(x * 0.001)
        dt = date(date_time.year, date_time.month, date_time.day)
        st = dt.strftime("%d/%m/%y")
        if st in items_sorted: #exists
            if kinds[x] in items_sorted[st]: #exists
                items_sorted[st][kinds[x]]["total"] += 1
                if x in spaces:
                    if spaces[x] in items_sorted[st][kinds[x]]:
                        items_sorted[st][kinds[x]][spaces[x]] += 1
                    else:
                        items_sorted[st][kinds[x]][spaces[x]] = 1
            else:
                items_sorted[st][kinds[x]] = {"total": 1}
                if x in spaces:
                    items_sorted[st][kinds[x]][spaces[x]] = 1
        else: # not exists
            items_sorted[st] = {}
            items_sorted[st][kinds[x]] = {"total": 1}
            if x in spaces:
                items_sorted[st][kinds[x]][spaces[x]] = 1
    return

export_para()
get_data()

data = {}
fetched_data = ["question","user","report", "reply"]
for f in fetched_data:
    data[f+"_count"] = []
    data[f+"_sum"] = []

for k in items_sorted:
    ref = items_sorted[k]
    for f in fetched_data:
        if f in ref:
            data[f+"_count"].append(int(ref[f]["total"]))
            data[f+"_sum"].append(sum(filter(None,data[f+"_count"])))
        else:
            data[f+"_count"].append(None)
            data[f+"_sum"].append(None)

fig, axs = plt.subplots(2)
axs[1].plot(data['user_sum'], marker = 'o', label = "Gebruikers")
axs[1].plot(data['question_sum'], marker = 'o', label = "Vragen")
axs[1].plot(data['reply_sum'], marker = 'o', label = "Antwoorden")
axs[1].plot(data['report_sum'], marker = 'o', label = "Meldingen")
axs[1].legend()
axs[1].set_xticks(range(0,len(items_sorted)), labels = items_sorted.keys(), rotation = 50)

count = {}
vals = []
labels = []
for i in items_sorted:
    if "question" in items_sorted[i]:
        for k in items_sorted[i]['question']:
            if k in count:
                count[k] += items_sorted[i]['question'][k]
            else:
                count[k] = 0
                count[k] += items_sorted[i]['question'][k]

countfilt = count.copy()
countfilt.pop("total")
for k in countfilt:
    vals.append(count[k])
    labels.append(k + " " + str(count[k]))

axs[0].pie(vals, labels = labels)
axs[0].set_title("Vragen (" + str(count['total']) + ")  & Ruimtes")
plt.show()