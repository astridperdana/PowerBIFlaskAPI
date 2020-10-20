from flask import Flask, request, jsonify, render_template, redirect, url_for
import pymongo
from werkzeug.utils import secure_filename
import os
import locale
import datetime

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['dboDataKeuangan']
mycol = mydb["cashIn"]

app = Flask(__name__)

app.config['UPLOAD_PATH'] = 'uploads'

def dateformat(dt):
    d = dt.split('/')
    x = datetime.datetime(int(d[2]), int(d[0]), int(d[0]))
    m = x.strftime("%B")
    d = x.strftime('%A')
    dt = x.strftime("%d")
    y = x.strftime("%Y")
    full = d+", "+dt+" "+m+" "+y
    return(full)

def csv_reader(csvs):
    with open (csvs) as f:
        dump = f.readlines()
        ip_list = []
        for i in dump:
            spl = i.split(',')
            ip_list.append(spl)
    return(ip_list)

def db_reader(lim='a', sk='b'):
    myli = []
    print(lim,' ', sk)
    if lim == 'a' and sk == 'b':
        for i in mycol.find().sort("_id"):
            del i['_id']
            myli.append(i)
        return(myli)
    else: 
        # for i in mycol.find().sort("_id", -1).limit(20):
        # for i in mycol.find().sort("_id").skip(sk).limit(lim): skip 2 row tapi yang ditampilin 2 data karena limit 2
        for i in mycol.find().sort("_id").skip(sk).limit(lim):
            del i['_id']
            myli.append(i)
        return(myli)

@app.route('/home')
# @app.route('/')
def home():
    locale.setlocale( locale.LC_ALL, 'IND' )
    if request.args.get('counter'):
        if int(request.args.get('counter')) < 1:
            counter = 1
        else:    
            counter = int(request.args.get('counter'))
    else: 
        counter = 1
    base = counter*10-10
    # end = counter * 10
    limit = 10
    status = db_reader(limit, base)
    viewli = []
    
    for i in status:
        date = dateformat(i['tanggal'])
        viewli.append([i['divisi'],i['customer'],date,locale.currency( int(i['aktual']), grouping=True ),locale.currency( int(i['plan']), grouping=True )])
    print(len(viewli))
    return render_template('index.html', listi = viewli, counter = counter)

@app.route('/home', methods=['POST'])
def uploads():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        # file_ext = os.path.splitext(filename)[1]
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    
    data_li = []
    li_split = csv_reader(os.path.join(app.config['UPLOAD_PATH'], filename))
    
    for i in li_split:
        temp_dict = {}
        temp_dict['divisi'] = i[0]
        temp_dict['customer'] = i[1]
        temp_dict['tanggal'] = i[2]
        temp_dict['aktual'] = i[3]
        temp_dict['plan'] = i[4].replace("\n","")
        data_li.append(temp_dict)
    for i in data_li:
        mydict = i
        x = mycol.insert_one(mydict)

    return redirect(url_for('home'))


@app.route('/api', methods = ['GET'])
def json_api():
    status = db_reader() 
    
    final_dict = {
        'server_name':'BSMRI_Monitor',
        'server_ip':'192.168.xxx.xxx',
        'status_server':1,
        'data':status
    }
    return jsonify(final_dict), 200

if __name__ == '__main__':
    app.run()