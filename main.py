from flask import Flask, render_template, request, redirect, make_response
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask('app')
from waitress import serve


import base64

def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def decode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string
@app.route("/getTheme")
def getTheme():
  with open("accounts.json") as r:
    r = json.load(r)
  for i in range(0,len(r)):
      if r[i]["email"] == request.cookies.get("email"):
        try:
          return r[i]["theme"]
        except:
          return "/static/stylesheets/darkblue.css"
  return "/static/stylesheets/darkblue.css"
@app.route("/changeTheme",methods=["POST"])
def changeTheme():
  with open("accounts.json") as r:
    r = json.load(r)
  for i in range(0,len(r)):
    if r[i]["email"] == request.cookies.get("email"):
      r[i]["theme"] = request.form.get("v")
      print(r[i]["theme"])
      with open("accounts.json",'w') as w:
        json.dump(r,w,indent=4)
      print(request.form.get("v"))
      return "cool"
  return request.form.get("v")
@app.route('/textbook')
def textbook():
  return render_template("textbook.html")
@app.route("/PearsonSync", methods=['POST'])
def pearsonsync():
  
  e = request.form.get('e')
  p = request.form.get('p')
  pin = request.form.get('pin')
  p = encode(pin,p)
  pin = generate_password_hash(pin)
  return "Incorrect Password!"
  return "Invalid Username~"
  return "Syncing with "+username+"!"
@app.route("/ScrapeSchoology",methods=["POST"])
def scrape():
  print("Complete")
  #return 'a'
  print('Starting to Scrape')
  e = request.form.get('e')
  p = request.form.get('p')
  import os
  os.system(f"python schoology.py {e} {p}")
  import json
  with open('main.json','r') as out:
    file = json.load(out)
  print('success')

  return str(file).replace('\\n','')

@app.route('/settings')
def settings():
  return render_template('settings.html')

@app.route('/grades')
def grades():
  return render_template('grades.html')
@app.route('/cj')
def cj():
  return render_template('cj.html')
@app.route('/resources',methods=['POST'])
def register():
  email = request.form.get('e')
  semail = request.form.get('s')
  name = request.form.get('fn').title()
  image = request.cookies.get('image')
  grade = request.form.get('g')
  element = request.form.get('el')
  password = request.form.get('p')
  psw = encode(semail,password)
  courses = os.system(f"python schoology.py {semail} {request.form.get('p')}")

  a = open('classes.txt','r').readlines()
  string = ''
  for i in a:
    string+=i.strip('\n')
    string+='<br>'
  with open('accounts.json','r') as file:
    file = json.load(file)
  file.append(
    {
      'email':email,
      'school_email':semail,
      'first_name':name,
      'avatar':image,
      'grade_level':int(grade),
      'element':element,
      'schoology_password':str(psw),
      'courses':a
    }
  )
  with open('accounts.json','w') as out:
    file = json.dump(file,out,indent=4)
  
  return redirect('/resources')

@app.route('/schoology')
def schoology():
  with open('accounts.json','r') as file:
    file = json.load(file)
  for i in file:
    if i["email"] == request.cookies.get("email"):
      
      password = (decode(i["school_email"],i["schoology_password"]))
      password = bytes(password, 'ascii')
      return render_template('schoology.html', school_email = i["school_email"],school_password = str(password).strip("'").strip("b'"))
  return render_template('schoology.html')

@app.route('/pearson')
def pearson():
  
  return render_template('pearson.html')

@app.route('/notes')
def notes():
  
  return render_template('notes.html')
@app.route('/planner')
def planner():
  return render_template('planner.html')
  
@app.route('/flog')
def flog():
  return render_template('flog.html')
@app.route('/notepad')
def np():
  return render_template('notepad.html')
@app.route('/spanish')
def physicsl1():
  return render_template('spanish.html')

  

@app.route('/physics/metric-units')
def physicsl2():
  return render_template('physics/metric-units.html')
@app.route('/english')
def english():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('english.html')

 
@app.route('/latin')
def latin():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('latin.html')
@app.route('/pe')
def pe():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('pe.html')
@app.route('/physics')
def physics():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('physics.html')
@app.route('/history')
def history():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('history.html')
@app.route('/chemistry')
def chemistry():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('chemistry.html')

@app.route('/health')
def health():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('health.html')
@app.route('/calendar')
def calendar():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('calendar.html')
@app.route('/algebraii')
def alg2():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('alg2.html')
@app.route('/biology')
def bio():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return render_template('bio.html')
@app.route('/')
def main():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    resp = make_response(render_template('main.html',file=json.dumps(file)))
    resp.set_cookie('email','')
    return resp
  if email != None and name != None and image != None:
    return redirect('/resources')
  with open('allowed.json') as file:
    file = json.load(file)
  return render_template('main.html',file=json.dumps(file))

  

@app.route('/profile')
def profile():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  return 'Under Construction'

@app.route('/resources')
def resources():
  email = request.cookies.get("email")
  name = request.cookies.get("name")
  image = request.cookies.get("image")
  if email == None or name == None or image == None:
    return redirect('/')
  with open('allowed.json') as file:
    file = json.load(file)
  if email not in file:
    return redirect('/')
  for i in json.load(open('accounts.json')):
    if i['email'] == email:
      
      return render_template('resources.html',name=name,email=email,image=image)
  return render_template('register.html', email=email)
serve(app, host='0.0.0.0', port=8080)
