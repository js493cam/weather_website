#!/usr/bin/python3
import mariadb, datetime, http.client, json, os
import io
import traceback
from defaults import *
from decimal import *

class mysql_database:
    def __init__(self, debug = False, user = USERNAME,
                       password = PASSWORD,
                       host = HOST,
                       port = PORT,
                       database = DATABASE):
        

        try:
            self.connection = mariadb.connect(user = user,
                       password = password,
                       host = host,
                       port = port,
                       database = database)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")

        if not self.connection:
            print(f"Error connecting to MariaDB Platform: {e}")

        self.cursor = self.connection.cursor()

    def execute(self, query):
        print("Query being executed: ",query,"\n")
        try:
            self.cursor.execute(query)
            try:
                return [a for a in self.cursor]
                self.connection.commit()
            except:
                self.connection.commit()
            
        except:
            #self.connection.rollback()
            raise
    
    def get(self, fields = "*", table = "WEATHER_MEASUREMENT_TEST",search=None):
        
        query = "SELECT %s FROM %s "%(fields,table)
        if search:
            query += "WHERE %s"%search
        query +=";"
        
        results = self.execute(query)          
        parsed = []
        
        for result in results:
            parsedresult = []
            for value in result:
                try:                    
                    v = float(value)
                except:
                    v = value
                
                if isinstance(v,datetime.datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                
                #if result.index(value) == 0:
                #    v = value
                
                parsedresult.append(v)    
            parsed.append(parsedresult)
        return parsed
    
    def __del__(self):
        self.connection.close()

class weather_database:
    def __init__(self, debug = False):
        
        self.debug = debug
        self.db = mysql_database()            
        self.insert_template = "INSERT INTO %s (AMBIENT_TEMPERATURE, GROUND_TEMPERATURE, AIR_QUALITY, AIR_PRESSURE, HUMIDITY, WIND_DIRECTION, WIND_SPEED, WIND_GUST_SPEED, RAINFALL, CREATED) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        self.query_template = "SELECT CREATED, %s FROM %s WHERE CREATED >= NOW() - INTERVAL %s HOUR;"
        self.latest_template = "SELECT %s FROM `WEATHER_MEASUREMENT_TEST` ORDER BY `ID` DESC LIMIT 1;"

    def get_latest(self):
        response = self.db.execute(self.latest_template%"*")
        
        PARAMS = ("ambient_temperature",
                    "humidity",
                    "air_pressure",
                    "air_quality",          
                    "wind_speed",
                    "wind_direction",
                    "wind_gust_speed",
                    "ground_temperature",
                    "rainfall")
        
        data = {}
        data["timestamp"] = response[0][-1]
                
        for i in range(len(PARAMS)):
            measurement = float(response[0][i+1])
            if measurement == -1:
                data[PARAMS[i]] = None
            elif PARAMS[i] in ("ambient_temperature","ground_temperature"):
                data[PARAMS[i]] = measurement - 273.15
            else:
                data[PARAMS[i]] = measurement
        
        return data  
        
    def get_weather(self, param="air_pressure", table="WEATHER_MEASUREMENT_TEST", duration=48):
        """Returns weather data as a dictionary. Argument param 
        determines what parameter is returned, and duration is measured
        in hours."""
        
      
        response = self.db.execute(self.query_template%(param,table,duration))
        
        times = [x[0] for x in response]
        data = [x[1] for x in response]
        
        if param == "ambient_temperature" or param == "ground_temperature":
            data = [float(x) - 273.15 for x in data] # return degrees C
            
        print(times,data)
        return times, data
        
    def is_none(self, val):
        return val if val != None else "NULL"

    def insert(self, table, input_values = []):
        """ Inserts input_values into table on SQL db. """
                
        PARAMS = ("ambient_temperature",
                  "ground_temperature",
                "air_quality",
                "air_pressure",
                "humidity",
                "wind_direction",
                "wind_speed",
                "wind_gust_speed",
                "rainfall")
        params = []
        
        # insert table
        
        if self.debug:
            table += "_TEST" # all test tables are appended with "_TEST" in SQL
        params.append(table)
        
        # insert params
        
        for i in PARAMS:
            if i in input_values:
                params.append(input_values[i])
            else:
                params.append(-1)
            
        # insert timestamp
        params.append("'%s'"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    
        self.db.execute(self.insert_template%tuple(params))
        
    def get_tables(self):
        result = self.db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'weather'")
        
        return [x[0] for x in result]
        
class remote_weather_database:
    def __init__(self):
        
        self.remotedb = mysql_database(user=REMOTE_USER,
                            password=REMOTE_PASSWORD,
                            host=REMOTE_HOST,
                            port=REMOTE_PORT,
                            database=REMOTE_DB)
        self.localdb = weather_database()
        
    def update(self):
        tables = self.localdb.get_tables()

        for table in tables:
            latest_ids = {}
            try:               
                # does table exist on db?
                count = self.remotedb.execute("SELECT COUNT(*) FROM %s"%table)[0][0]
                print(count)
                if count == 0:
                    latest_ids[table] = 0
                else:                
                    latest_ids[table] = self.remotedb.execute("SELECT ID FROM %s ORDER BY ID DESC LIMIT 1"%table)[0]
                
            except:
                print("Table not found. Creating")
                # if above fails, create table on server
                query = "CREATE TABLE " + table + "("
                
                for (dbparam, paramformat) in DBPARAMETERS:
                    query += dbparam + " " + paramformat + ",\n"
                
                query += "PRIMARY KEY (ID));"
                
                self.remotedb.execute(query)
                print("Table Created!")
            
            try:
                # now push data to server
                records_to_push = self.localdb.db.get(fields = "*",
                                                        table = table,
                                                        search ="ID > %s"%latest_ids[table])
                                                        
                num_to_push = len(records_to_push)
                print("In table %s there are %s records to push"%(table,num_to_push))
                
                if records_to_push:   
                    values = ""                 
                    for record in records_to_push:
                        values += "("
                        values += str(record)[1:-1]
                        values += "), "
                        
                        
                    
                    self.remotedb.execute("INSERT INTO %s (%s) VALUES %s;"%(table,", ".join(COLUMN_HEADINGS),values[:-2]))
                        
            except Exception as e:
                print("Exception occured! ", e)
                traceback.print_exc()
                

if __name__ == "__main__":
    #test db
    db = weather_database(debug = True)
    
    #db.insert(table = "WEATHER_MEASUREMENT")
    #print(db.get_weather())
    #print(db.get_latest())
 
    #print(db.db.get(fields="*",search = "ID < 5"))
          
    remotedb = remote_weather_database()
    remotedb.update()


