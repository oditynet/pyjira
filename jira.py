#version: 0.2
#owner: oditynet

from datetime import datetime
import sqlite3
import sys
import arrow
from colorama import Fore, Back, Style
import getpass
import hashlib
path = "/home/odity/bin/pyjira/jira.db"

act = ""
act1 = ""
act2 = ""
whoami = ''

#-------------------------------------------------------------------------------------------------------------------------------
def help():
    print("python jira.py command table arg")
    print("python jira.py a/g/e/d u/t")
    print("python jira.py a t 'выдать комп' '' 'выделить стол и комп, ноут' new 04-04-2024")
    print("python jira.py g u")
    print("python jira.py g u test")
    print("python jira.py d k")
    print("python jira.py e t 'отсобеседовать' status=work")
    print("python jira.py d u test")
#-------------------------------------------------------------------------------------------------------------------------------
def print_prior(t,p): # -2, -1, 0, 1, 2
    #BLACK           = 30
    #RED             = 31
    #GREEN           = 32
    #YELLOW          = 33
    #BLUE            = 34
    #MAGENTA         = 35
    #CYAN            = 36
    #WHITE           = 37
    #RESET     
    if p == -2:
        return Fore.GREEN +str(t)+Style.RESET_ALL
    if p == -1:
        return Fore.CYAN +str(t)+Style.RESET_ALL
    if p == 0:
        return Fore.WHITE +str(t)+Style.RESET_ALL
    if p == 1:
        return Fore.YELLOW +str(t)+Style.RESET_ALL
    if p == 2:
        return Fore.RED +str(t)+Style.RESET_ALL
    if p == '' or p == None:
        return ''
#-------------------------------------------------------------------------------------------------------------------------------
def get_katban(db): #new,progress,done
    res = db.execute('SELECT name,status,prior FROM tasks')
    n = res.fetchall()
    nl=[]
    pl=[]
    fl=[]
    if n is not None:
        #print(n)
        for i,j,p in n:
            if j == "new":
                nl.append([i,p])
            if j == "process":
                pl.append([i,p])
            if j == "done":
                fl.append([i,p])
            
        max = len(nl);
        if len(pl) !=0:
            if (len(pl) > len(nl) ):
                max = len(pl);
                #print(max)
        if len(fl) != 0:
            if (len(fl) > max):
                max = len(fl);
                #print(max)
                #print("@")
        print(max,len(nl),len(pl),len(fl))
        for i in range(len(nl),max):
            nl.append(['',''])
        for i in range(len(pl),max):
            pl.append(['',''])
        for i in range(len(fl),max):
            fl.append(['',''])
        #print(nl)
        print ("{:<35} {:<35} {:<35}".format('Новый',Fore.YELLOW + 'В работе'+Style.RESET_ALL,Fore.GREEN +'Завершен'+Style.RESET_ALL))
        #print("_______________________________________________________________________________________________________________")
        for i in range(0,max):
            #print(print_prior(nl[i][0],nl[i][1]),print_prior(pl[i][0],pl[i][1]),print_prior(fl[i][0],fl[i][1]))
            print("{:<35} {:<35} {:<35}".format(print_prior(nl[i][0],nl[i][1]),print_prior(pl[i][0],pl[i][1]),print_prior(fl[i][0],fl[i][1])))              

#-------------------------------------------------------------------------------------------------------------------------------
def get_tasks_list(db):
    res = db.execute('SELECT * FROM tasks')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("Задачи:")
        print ("{:<35} {:<20} {:<40} {:<15} {:<15} {:<15}".format('Название проекта(name)','Исполнитель(owner)','Описание(text)','Статус(status)', 'Приоритет(prior)', 'Дата окончания(datelast)'))
        for i in res:
            n1,n2,n3,n4,n5,n6 = i
            print ("{:<40} {:<20} {:<40} {:<15} {:<15} {:<15}".format(n1,n2,n3,n4,n5,n6))
#-------------------------------------------------------------------------------------------------------------------------------
def get_tasks_data(db):
    res = db.execute('SELECT * FROM tasks')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("Даты:")
        print ("{:<40} {:<20} {:<40} {:<15} {:<15} {:<15} {:<15}".format('Название проекта','Исполнитель','Описание','Статус', 'Приоритет', 'Дата окончания','Просрочили'))
        for i in res:
            n1,n2,n3,n4,n5,n6 = i
            now = datetime.now().date()
            date1 = datetime.strptime(n6, '%Y-%m-%d').date()
            delta=date1-now     
            print("{:<40} {:<20} {:<40} {:<15} {:<15} {:<15} {:<15}".format(n1,n2,n3,n4,n5,n6,delta.days))
#-------------------------------------------------------------------------------------------------------------------------------
def get_user_list(db):
    res = db.execute('SELECT * FROM users')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("")
        print ("{:<20} {:<40}".format('Исполнитель','Название проекта'))
        for i in res:
            n1,n2,n3 = i
            print ("{:<20} {:<40}".format(n1,n2))
#-------------------------------------------------------------------------------------------------------------------------------
def get_task_desc(db,taskname):
    res = db.execute('SELECT * FROM tasks WHERE name=?',(taskname,))
    res = res.fetchone()
    #print(res)
    if res is not None:
        print("Описание задачи:")
        tmp=''
        for i in res:
            desc="'"+i+"'"
            tmp = tmp + desc + "\t"
        print(tmp)
#-------------------------------------------------------------------------------------------------------------------------------
def edit_task(con,db,taskname,arg): #connection,dbtask,act1, act2
    #print(taskname,arg)
    res = db.execute('SELECT name FROM tasks WHERE owner=?',(taskname,))
    res = res.fetchone()
    #print(res)
    #if res is not None:
    
    arg1,arg2 = arg.split("=")
    #print(arg1,arg2)
    if arg1 == 'owner':
        res = db.execute('SELECT name FROM users WHERE name=?',(arg2,))
        res = res.fetchone()
        #if arg2 != '':
        if res is None:
            print('Пользователя не существует')
            return
    #print(arg1,arg2,taskname)
    if arg1 is not None and arg2 is not None:
        values = {"arg1": arg1}
        if arg1 == "status" and arg2 == "done" and whoami != "admin":
            print("Только админ может сменить статус")
            return 0
        sql="UPDATE tasks SET {arg1}=? WHERE name=?".format(**values) 
        #print(sql)
        db.execute(sql,(arg2,taskname))  
        con.commit()
        print(f"Изменили в задаче '{taskname}'")
        db.execute('UPDATE users SET task=? WHERE name=?', (taskname,arg2))  
        con.commit()
        print('Задачу обновил')
#-------------------------------------------------------------------------------------------------------------------------------
def get_user_desc(db,username):
    res = db.execute('SELECT * FROM users WHERE name=?',(username,))
    res = res.fetchone()
    #print(res)
    if res is not None:
        print("Пользователь:")
        tmp=''
        for i in res:
            desc="'"+i+"'"
            tmp = tmp + desc + " "
        print(tmp)
#-------------------------------------------------------------------------------------------------------------------------------
def get_user_task(db,username):
    #print(username)
    res = db.execute('SELECT task FROM users WHERE name=?',(username))
    res = res.fetchone()
    #print(res)
    if res is not None:
        print("Пользователь:")
        tmp=''
        for i in res:
            return i
#-------------------------------------------------------------------------------------------------------------------------------
def find_task_at_alluser(db,taskname):
    res = db.execute('SELECT * FROM users')
    res = res.fetchall()
    #print(res)
    if res is not None:
        #print("Пользователь:")
        for i in res:
            name,tasklist= i
            #print( tasklist.find(taskname))
            if tasklist.find(taskname) >= 0:
                return tasklist,name
    return None,None
#-------------------------------------------------------------------------------------------------------------------------------          
def get_task(db,taskname):
    res = db.execute('SELECT name FROM tasks  WHERE name=?',(taskname,))
    res = res.fetchone()
    #print(res,taskname)
    return res
#-------------------------------------------------------------------------------------------------------------------------------
def get_user(db,username):
    res = db.execute('SELECT name FROM users  WHERE name=?',(username,))
    res = res.fetchone()
    return res
#-------------------------------------------------------------------------------------------------------------------------------
def add_tasks(con,db,argv):
    tmp_task = get_task(db,argv[3])
    #print(tmp_task,argv[3])
    if tmp_task is not None:
        print(f"Задача '{tmp_task}' существует")
        return
    userreal = get_user(db,argv[4])
    if userreal is None:
        print(f"Пользователь {argv[4]} не существует")
        return
    #print(argv[3],argv[4],argv[5],argv[6],argv[7])
    desc = argv[5]
    if argv[5].find(" ") > 0:
           desc="'"+argv[5]+"'"
    now = arrow.now()
    date=now.shift(days=int(argv[8])).date()
    #print(argv[3],argv[4],desc,argv[6],date)
    db.execute('INSERT INTO tasks (name ,owner, text, status, prior, datelast) VALUES (?, ?, ?, ?, ?, ?)', (argv[3],argv[4],desc,argv[6],argv[7],date))
    con.commit() 
    print(f"Добавил задачу '{argv[3]}'")
    tmp_user = get_user(db,argv[4])
    if tmp_user is not None:
        tasklist=get_user_task(db,tmp_user)
        if  len(tasklist) == 0:
        #tasklist=tasklist+","+argv[3]
            tasklist=argv[3] 
        else:
            tasklist=tasklist+","+argv[3]
        db.execute('UPDATE users SET task=? WHERE name=?', (tasklist,argv[4]))  
        con.commit()
        print(f"Пользователю установил задачу '{tasklist}'")    
#-------------------------------------------------------------------------------------------------------------------------------
def delete_task(con,db,taskname):
    res = db.execute('SELECT name FROM tasks WHERE name=?',(taskname,))
    res = res.fetchall()

    if res is not None:
        usertasks,user=find_task_at_alluser(db,taskname)
        #print(usertasks,user)
        if user is not None:
            usertasks = usertasks.replace(taskname,'',1)
            usertasks = usertasks.replace(',,',',')
            if usertasks[0] == ',':
                usertasks = usertasks.replace(',','',1)
            if usertasks[-1] == ',':
                usertasks = usertasks[:-1]
            #print(usertasks,user)
            #print(usertasks.find(','),len(usertasks))
        
            db.execute('UPDATE users SET task=? WHERE name=?', (usertasks,user))  
            con.commit()

        db.execute('DELETE FROM tasks  WHERE name=?',(taskname,))
        con.commit()
        print(f"Задача '{taskname}' удалена")
    else:
        print("Задачи такой нет в БД")
#-------------------------------------------------------------------------------------------------------------------------------
def delete_user(con,db,username):
    res = db.execute('SELECT name FROM users WHERE name=?',(username,))
    res = res.fetchall()
    if len(res) >0:
        res = db.execute('SELECT task FROM users WHERE name=?',(username,))
        res = res.fetchall()
       # print(res)
        for listtask in res:
            #print(listtask[0])
            for i in listtask[0].split(','):
                #print(i+"=I")
                db.execute('UPDATE tasks SET owner=? WHERE name=?',('',i))   
                con.commit()
                print(f'У задачи "{i}" удалил исполнителя')
        db.execute('DELETE FROM users  WHERE name=?',(username,))
        con.commit()

        print(f"Пользователь {username} удален")
    else:
        print("Пользователя нет в БД")
#-------------------------------------------------------------------------------------------------------------------------------
def add_user(con,db,argv):
    tmp_user = get_user(db,argv[3])
    if tmp_user is not None:
        print(f"Пользователь '{argv[3]}' существует")
        return
    password = getpass.getpass()
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    db.execute('INSERT INTO users (name ,task,pass) VALUES (?, "",?)', (argv[3],hash))
    con.commit() 
    print(f"Добавил пользователя {argv[3]}")
#-------------------------------------------------------------------------------------------------------------------------------
def main(argv, argc):
    if argc > 1:
        if (argv[1] == '--help' or argv[1] == '-h'): 
            help()
            return
    print("DB:"+path)
    connection = sqlite3.connect(path,check_same_thread=False)
    dbtask = connection.cursor()
    dbtask.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
        name TEXT,
        task TEXT   ,
        pass TEXT   ,
        PRIMARY KEY ( name )
    );
      ''')
    dbtask.execute('''
    CREATE TABLE IF NOT EXISTS tasks
    (
        name TEXT PRIMARY KEY,
        owner TEXT,
        text TEXT,               
        status INTEGER,
        prior INTEGER,
        datelast timestamp
    );
    ''')
    if argc <= 1:
        get_tasks_data(dbtask)
        connection.close()
        return

    password = getpass.getpass()
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    #print(hash)
    res = dbtask.execute('SELECT name FROM users WHERE pass=?',(hash,))
    res = res.fetchone()
    if res is None:
        print("Ошибка авторизации")
        return 0
    global whoami
    whoami=res[0]
    print("Приветствую '"+whoami+"'")
    if argc < 3 and argv[2] != 'k':
        return
    global act,act1,act2
    #print(argv[2],argv[2],argv[3])
    if argv[1] == 'g': #get 
        act='g'
    if argv[1] == 'e': #edit
        act='e'
    if argv[1] == 'a': #add
        act='a'
    if argv[2] == 't': #task
        act1 = 't'
        if argc >= 3 + 1: # get task name desc
            act2 = argv[3]
    if argv[2] == 'k': #task
        act1 = 'k'
    if argv[2] == 'u': #user
        act1 = 'u'
        if argc == 3 + 1: # get task name desc
            act2 = argv[3]
    if argv[1] == 'd': #delete
        act='d'
        #print(argc)
        if argc == 3 + 1: # del task name 
            act2 = argv[3]
    if act == '' or act1 == '':
        exit
    #print(act,act1,act2)
    
    if act == 'a' and act1 == 't':  #a t t3 user1 "texts  s" new 02.04.2024
        add_tasks(connection,dbtask,argv)
    if act == 'a' and act1 == 'u' and argc > 3:  
        add_user(connection,dbtask,argv)
    if act == 'g' and act1 == 'k': 
            get_katban(dbtask)
    if act == 'g' and act1 == 't': 
        if act2 != "":
            get_task_desc(dbtask,act2)
        else:
            get_tasks_list(dbtask)
    if act == 'g' and act1 == 'u': 
        if act2 != "":
            get_user_desc(dbtask,act2)
        else:
            get_user_list(dbtask)
    #print(act,act1)
    if act == 'e' and act1 == 't':
        #print(act2) 
        if act2 != "":
            edit_task(connection,dbtask, act2,argv[4])
    
    if act == 'd' and act1 == 'u':
        delete_user(connection,dbtask,act2)
    elif act == 'd' and act1 == 't' and act2 != '':
        delete_task(connection,dbtask,act2)
    connection.close()
#-------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv, len(sys.argv))
