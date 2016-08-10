#!/usr/bin/python3
import http.server
import jinja2
import pymongo
import cgi
from datetime import datetime

MONGO_PORT = 12016
MONGO_DB = "contacts"


FIELDNAMES = ["Имя", 
            "Группа", 
            "Откуда вы (город, школа, класс, ...)",
            "email",
            "телефон",
            "вКонтакте",
            "Телеграмм",
            "Почтовый адрес",
            "Дополнительный контакт",
            "Дополнительный контакт",
            "Дополнительный контакт",
            "Дополнительный контакт",
            "Дополнительный контакт"
            ]

FIELDS = []
for i in range(len(FIELDNAMES)):
    FIELDS.append({"id": str(i), "name": FIELDNAMES[i]})

def init_data(contacts):
    print(client.database_names())
    
client = pymongo.MongoClient(port=MONGO_PORT)
db = client[MONGO_DB]
contacts = db.contacts
init_data(contacts)

def load_template(filename):
    with open(filename) as f:
        text = f.read()
    return jinja2.Template(text)

main_template = load_template("main.html")
form_template = load_template("form.html")
contacts_template = load_template("contacts.html")
root_template = load_template("root.html")
ok_template = load_template("ok.html")

class ContactsHandler(http.server.BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super(ContactsHandler, self).__init__(*args, **kwargs)
   
    def write(self, s):
        self.wfile.write(bytes(s, "utf-8"))
        
    def send_css(self):
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        with open("main.css") as f:
            self.write(f.read())
        
    def write_form(self):
        return form_template.render(fields=FIELDS)
    
    def write_root(self):
        return root_template.render()
    
    def write_contacts(self):
        cursor = contacts.find({}, sort=[("number", pymongo.ASCENDING)])
        cs = []
        for doc in cursor:
            cs.append(doc)
        return contacts_template.render(contacts=cs, fields=FIELDS)
    
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            return
        if self.path == "/main.css":
            self.send_css()
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if self.path == "/":
            content = self.write_root()
        elif self.path == "/form":
            content = self.write_form()
        elif self.path == "/contacts":
            content = self.write_contacts()
        else:
            content = "Wrong path"
        self.write(main_template.render(content=content))
        
    def get_post_vars(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            data = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            data = cgi.parse_qs(self.rfile.read(length).decode('utf-8'), keep_blank_values=1)
        else:
            data = {}
        # keep only first element from each list
        for key in data:
            data[key] = data[key][0]
        return data
        
    def do_POST(self):
        if self.path != "/addcontact":
            self.send_response(404)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        vals = self.get_post_vars()
        vals["number"] = contacts.find({}).count()
        vals["ip"] = self.client_address[0]
        vals["time"] = datetime.now().isoformat()
        contacts.insert_one(vals)
        self.write(main_template.render(content=ok_template.render()))
        
        
        
        


server_address = ('', 8000)
httpd = http.server.HTTPServer(server_address, ContactsHandler)
httpd.serve_forever()