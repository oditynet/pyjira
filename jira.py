#version: 0.1.1
#owner: oditynet

from datetime import datetime
import sqlite3
import sys
import arrow


act = ""
act1 = ""
act2 = ""
#-------------------------------------------------------------------------------------------------------------------------------
def help():
    print("python jira.py command table arg")
    print("python jira.py a/g/e/d u/t")
    print("python jira.py a t 'выдать комп' '' 'выделить стол и комп, ноут' new 04-04-2024")
    print("python jira.py g u")
    print("python jira.py g u test")
    print("python jira.py e t 'отсобеседовать' status=work")
    print("python jira.py d u test")
#-------------------------------------------------------------------------------------------------------------------------------
def get_tasks_list(db):
    res = db.execute('SELECT * FROM tasks')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("Задачи:")
        print ("{:<35} {:<20} {:<40} {:<15} {:<15}".format('Название проекта(name)','Исполнитель(owner)','Описание(text)','Статус(status)', 'Дата окончания(datelast)'))
        for i in res:
            n1,n2,n3,n4,n5 = i
            print ("{:<40} {:<20} {:<40} {:<15} {:<15}".format(n1,n2,n3,n4,n5))
#-------------------------------------------------------------------------------------------------------------------------------
def get_tasks_data(db):
    res = db.execute('SELECT * FROM tasks')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("Даты:")
        print ("{:<40} {:<20} {:<40} {:<15} {:<15} {:<15}".format('Название проекта','Исполнитель','Описание','Статус', 'Дата окончания','Просрочили'))
        for i in res:
            n1,n2,n3,n4,n5 = i
            now = datetime.now()
            date1 = datetime.strptime(n5, '%Y-%m-%d')
            delta=date1-now      
            print("{:<40} {:<20} {:<40} {:<15} {:<15} {:<15}".format(n1,n2,n3,n4,n5,delta.days))
#-------------------------------------------------------------------------------------------------------------------------------
def get_user_list(db):
    res = db.execute('SELECT * FROM users')
    res = res.fetchall()
    #print(res)
    if res is not None:
        print("Пользователи:")
        print ("{:<20} {:<40}".format('Исполнитель','Название проекта'))
        for i in res:
            n1,n2 = i
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
    print(f"Изменили в задаче '{taskname}'")
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
        sql="UPDATE tasks SET {arg1}=? WHERE name=?".format(**values) 
        #print(sql)
        db.execute(sql,(arg2,taskname))  
        con.commit()

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
    date=now.shift(days=int(argv[7])).date()
    print(argv[3],argv[4],desc,argv[6],date)
    db.execute('INSERT INTO tasks (name ,owner, text, status, datelast) VALUES (?, ?, ?, ?, ?)', (argv[3],argv[4],desc,argv[6],date))
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
        print(usertasks,user)
        if user is not None:
            usertasks = usertasks.replace(taskname,'',1)
            usertasks = usertasks.replace(',,',',')
            if usertasks[0] == ',':
                usertasks = usertasks.replace(',','',1)
            if usertasks[-1] == ',':
                usertasks = usertasks[:-1]
            print(usertasks,user)
            print(usertasks.find(','),len(usertasks))
        
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
    #print(res,taskname)
    if res is not None:
        res = db.execute('SELECT task FROM users WHERE name=?',(username,))
        res = res.fetchall()
        print(res)
        for listtask in res:
            print(listtask[0])
            for i in listtask[0].split(','):
                print(i+"=I")
                db.execute('UPDATE tasks SET owner=? WHERE name=?',('',i))   
                con.commit()
                print(f'У задачи {i} удалил исполнителя')
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

    db.execute('INSERT INTO users (name ,task) VALUES (?, "")', (argv[3],))
    con.commit() 
    print(f"Добавил пользователя {argv[3]}")
#-------------------------------------------------------------------------------------------------------------------------------
def main(argv, argc):
    if argc <= 1:
        connection = sqlite3.connect('jira.db',check_same_thread=False)
        dbtask = connection.cursor()
        get_tasks_data(dbtask)
        connection.close()
        return
    if argv[1] == '--help' or argv[1] == '-h': #get
        help()
        return
    if argc < 3:
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
    connection = sqlite3.connect('jira.db',check_same_thread=False)
    dbtask = connection.cursor()
    dbtask.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
        name TEXT,
        task TEXT   ,
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
        datelast timestamp
    );
    ''')
    if act == 'a' and act1 == 't':  #a t t3 user1 "texts  s" new 02.04.2024
        add_tasks(connection,dbtask,argv)
    if act == 'a' and act1 == 'u' and argc > 3:  
        add_user(connection,dbtask,argv)
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
