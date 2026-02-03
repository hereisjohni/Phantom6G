from flask import Flask, render_template, jsonify
import sqlite3

DB_NAME = 'projekt_phantom_6g.db'
app = Flask(__name__)

def get_recent_temperature_data():
    limit = 100
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, temperature
        FROM pomiary_phantom
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    data = cursor.fetchall()
    conn.close()

    return data[::-1]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    raw_data = get_recent_temperature_data()

    labels = [row[0] for row in raw_data]
    temperatures = [row[1] for row in raw_data]

    return jsonify(labels=labels, temperatures=temperatures)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
