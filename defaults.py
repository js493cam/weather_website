# Defaults configuration file

# general settings
VERSION = 0.02

# general DB settings
DBPARAMETERS = (  ("ID",                  "BIGINT NOT NULL"),
                  ("AMBIENT_TEMPERATURE", "DECIMAL(6,2) NOT NULL"),
                  ("GROUND_TEMPERATURE",  "DECIMAL(6,2) NOT NULL"),
                  ("AIR_QUALITY",         "DECIMAL(6,2) NOT NULL"),
                  ("AIR_PRESSURE",        "DECIMAL(6,2) NOT NULL"),
                  ("HUMIDITY",            "DECIMAL(6,2) NOT NULL"),
                  ("WIND_DIRECTION",      "DECIMAL(6,2) NOT NULL"),
                  ("WIND_SPEED",          "DECIMAL(6,2) NOT NULL"),
                  ("WIND_GUST_SPEED",     "DECIMAL(6,2) NOT NULL"),
                  ("RAINFALL",            "DECIMAL(6,2) NOT NULL"),
                  ("CREATED",             "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
            )

COLUMN_HEADINGS = [x[0] for x in DBPARAMETERS]

# local DB settings
HOST = "localhost"
USERNAME = "john"
PASSWORD = "db1n2hq7TIBI"
DATABASE = "weather"
PORT = 3306

READING_PARAMS = [
			"ambient_temperature",
           "ground_temperature",
            "air_quality",
            "air_pressure",
            "humidity",
            "wind_direction",
            "wind_speed",
            "wind_gust_speed",
            "rainfall"
            ]
            

# remote DB settings
REMOTE_HOST = "3.10.228.48"
REMOTE_PASSWORD = "1n2hq7TIBI"
REMOTE_PORT = 3306
REMOTE_USER ="john"
REMOTE_DB = "weather"
                   

