import MySQLdb
import MySQLdb.cursors
def f():
    db = MySQLdb.connect('127.0.0.1', 'root', '15478xx', 'sina', )
    cursor = db.cursor()
    sql ="""insert into information 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    params = (1557755, 'Lonenso', 'm', 'Fuji', 'quan', 'fasdf', "1996/11/07", 134125, 555556, 34123, 'asdf', 'asdf', 'asdfasf')

    # cursor.execute(sql, params)
    # sql = "select * from information"

    cursor.execute(sql, params)
    db.commit()

    # info = cursor.fetchmany(aa)
    # for ii in info:
    #     print(ii)
    cursor.close()
    db.close()

if __name__ == "__main__":
    f()
    print("OK!")