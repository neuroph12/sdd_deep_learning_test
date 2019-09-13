import pymssql

class db_extraction:

    def __init__(self,server_name,database_name):
        self.server_name = server_name
        self.database_name =database_name
        self.conn = pymssql.connect(server=self.server_name,user='user',
                                    password='password',database=self.database_name,charset='utf8')
    def get_data(self,query,show=True):
        row_list= []
        
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchone()
        while rows:
            _row=[]
            for  row in rows:
                if repr(type(row))=="<class 'str'>":
                    _row.append(row.strip())
                else:
                    _row.append(row)
            if show:
                print(_row)
            row_list.append(_row)
            rows = cursor.fetchone()
        cursor.close()
        self.conn.close()
        return row_list
    
    def insert_data(self,query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        
    def close(self):
        print('db close')
        return self.conn.close()