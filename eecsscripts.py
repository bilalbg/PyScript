from fabric import Connection
from patchwork.files import exists
from patchwork.transfers import rsync
import paramiko

import sys, os


if(len(sys.argv) < 5):
     print("Error: Require command, username, password, filename. ")
     sys.exit(1)
     
command = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
filename = ""
lpath = "" 
rpath = ""
assignment=""
coursecode = ""

for arg in sys.argv:
     if(arg.startswith("f=")):
          filename=arg[2:]
     if(arg.startswith("l=")):
          if(os.path.isdir(arg[2:])):
               lpath = arg[2:] + "/" + filename
               localpath = arg[2:]
          else:
               print("Error: Path does not exist")
               sys.exit(1)
     if(arg.startswith("r=")):
          if(arg[0] == "/"):
               rpath = arg[3:] + "/" + filename
          else:
               rpath = arg[2:] + "/" + filename
          remotepath = sys.argv[6]
     if(arg.startswith("c=")):
          coursecode=arg[2:]
     if(arg.startswith("a=")):
          assignment = arg[2:]
locatpath = None
if lpath == "":
     lpath = "" + filename
if rpath == "":
     rpath = filename
#print(assignment, coursecode, filename, lpath, rpath)

c = Connection

try:
     c = Connection(host="red.eecs.yorku.ca", user=user, 
               connect_kwargs={"password": password})
     
except paramiko.AuthenticationException:
     print("Error: Incorrect username or password")
     

def printee():
     print("print")
     c.put(lpath, rpath)
     c.run(('lpr ' + filename))
     c.run('lpq')
     return
     
def upload():
     print("upload")
     print("Moving to folder... \n\n")
     if("." not in filename):
          rsync(c,lpath, (rpath))
     else:
          c.put(lpath, rpath)
     c.run('ls')
     return
def submit():
     print("submit")
     print("Moving to folder... \n\n")
     with c.cd(rpath):
          #c.put(lpath)
          c.run(('submit ' + coursecode + ' ' + assignment 
                    + ' ' + filename))
     return
     

def download(path = rpath):
     global locatpath 
     global localpath
     if(filename not in localpath):
          localpath = localpath + "/" + filename
     if(locatpath is None):
          locatpath = path
     #print(localpath)
     #os.listdir()
     os.mkdir(localpath )
     os.chdir(localpath)
     local = localpath
     #global rpath
     
     #print(path)
     #print(localpath)
     
          
     files = ((c.run('ls ' + path)).stdout).split()
     #print(files)
     for f in files:
          print("\t" + f)
          if("." not in f):
               #print("directory: ")
               #print(path + "/" + f)
               locatpath = path + "/" + f
               #os.mkdir(f)
               localpath = localpath + "/" + f
               #print(rpath)
               download(locatpath)
               print(localpath)
               os.chdir(localpath)
          else:
               #print(locatpath + "/" + f)
               c.get(locatpath + "/" + f)
     if("/" in path):
          #print(path.split("/")[0:-1])
          locatpath = '/'.join(path.split("/")[0:-1])
          #print(localpath + " local")
          localpath = '/'.join(localpath.split('/')[0:-1])
          #print(localpath + " local")
          #print(locatpath)
     
     return

#no brackets here so the functions aren't called multiple times
commands = {"print":printee,
           "upload":upload,
           "submit":submit,
           "download":download
           }


try:
     if len(sys.argv) >= 7 and c.run('test -d {}'.format(sys.argv[5]), warn=True):
          raise IOError
     else:
          if(command == "submit" and (coursecode == "" or 
                                   assignment == "")):
               raise NameError
          else:
               commands[command]()
          
except IOError:
     print("Error: Invalid path or file")
except paramiko.AuthenticationException:
     print("Error: Incorrect username or password")
except NameError:
     print("Course code or assignment name not given")
finally:
     c.close()
     print("\n...Closed connection")
