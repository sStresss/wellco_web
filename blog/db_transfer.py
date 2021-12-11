import pymysql
import django



def getMySqlBase(SqlHostname, SqlPort, SqlUserName, SqlPwd, SqlDBName):
    try:
        con = pymysql.connect(host=SqlHostname,
                              port=SqlPort,
                              user=SqlUserName,
                              passwd=SqlPwd,
                              db=SqlDBName)
        with con:
            data = con.cursor()
            data.execute("SELECT * FROM treeobjtbl")
            data_rows = data.fetchall()
            print(data_rows)
    except ex
        return data_rows


