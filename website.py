from flask import Flask, render_template

import database



app = Flask(__name__)

@app.route('/')
def index():
	db = database.weather_database()
	latest_observations = db.get_latest().items()
	
	return render_template('index.html', observations = latest_observations)

		
if __name__ == '__main__':
	app.run(debug=True, port = 3000)

