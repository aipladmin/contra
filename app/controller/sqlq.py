import sqlite3
import random
import string
import sqlite3


def madhav():
    return 'madhav'


def sql_query(sql, sqldt):
    # print("SQLDT:"+sqldt)
    try:
        print(sql, "        ", sqldt)
        if sqldt is not None:
            with sqlite3.connect("app.db") as con:
                cur = con.cursor()
                print(sql, "        ", sqldt)
                cur.execute(sql, sqldt)
                if sql.split(' ')[0].lower() == "select" :
                    rows = cur.fetchall()
                    flag =1
                else:
                    con.commit()
                    flag=0

        if sqldt is None:
            with sqlite3.connect("app.db") as con:
                cur = con.cursor()
                print(sql)
                cur.execute(sql)
                rows = cur.fetchall()
                flag=1
    except con.Error as e:
        print("Error: {}".format(e.args[0]))
    finally:
        con.close()
        
        if flag == 0:
            con.close()
            pass
        else:
            con.close()
            return rows
