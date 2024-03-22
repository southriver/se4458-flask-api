from functools import wraps
import sqlite3 as sql
from flask import Config, Flask, jsonify, render_template, request
import requests
app = Flask(__name__)

def initDB():
    conn = sql.connect('database.db')
    print( "Opened database successfully")   
    
    conn.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, addr TEXT, city TEXT, pin TEXT)')
    print ("Table created successfully")
    conn.close()

@app.route('/addStudent',methods = ['POST'])
def addrec():
    response = {
        'status': 'SUCCESS'
    }      
    try:
        nm = request.json.get('name')
        addr = request.json.get('address')
        city = request.json.get('city')
        pin = request.json.get('pin')
        
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO students (name,addr,city,pin) VALUES (?,?,?,?)",(nm,addr,city,pin) )
            
            con.commit()
            msg = "Record successfully added"
    except Exception as error:
        # con.rollback()
        msg = "error in insert operation"
        response = {
            'status': 'ERROR',
            'msg' : str(error)
        }        
    finally:
        return jsonify(response)
        con.close()   
    
@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from students")
   
    rows = cur.fetchall();
    result = []
    for row in rows:
        result.append({ 'name': row[0], 'address': row[1] })  # Add more columns as needed

    # Return JSON response
    return jsonify(result)    


@app.route('/')
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Decorator for verifying bearer token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            # Extract the token from the "Authorization" header
            auth_header = request.headers['Authorization']
            bearer_token = auth_header.split(' ')
            if len(bearer_token) == 2 and bearer_token[0] == 'Bearer':
                token = bearer_token[1]

        # Replace 'your_bearer_token' with the actual expected bearer token value
        expected_token = Config.BEARER_TOKEN

        if not token or token != expected_token:
            # Token is missing or invalid
            return jsonify({'message': 'Missing or invalid token'}), 401

        # Perform additional token validation if needed
        # ...

        return f(*args, **kwargs)

    return decorated


@app.route('/ping',methods = ['GET'])
@token_required
def ping():
    return "Ping API with token authentication"

@app.route('/get_movie_data', methods=['POST'])
def get_movie_data():
    # Get the city from the form data
    searchText = request.form['searchText']

    # Replace 'your_api_key' with your actual OpenWeatherMap API key
    api_key = 'your_api_key'
    api_url = f'https://api.themoviedb.org/3/search/movie?api_key=ab166ff82684910ae3565621aea04d62&language=en-US&query=${searchText}&page=1&include_adult=false'
    response = requests.get(api_url)

    # Return JSON response
    return jsonify(response.json())

if __name__ == "__main__":
    initDB()
    app.run(debug=True)