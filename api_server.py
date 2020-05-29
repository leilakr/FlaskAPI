import flask
from flask import request, jsonify
import psycopg2
import os

connection_to_docker_postgres = psycopg2.connect(host=os.environ.get('DB_HOST', 'localhost'), database=os.environ.get('DB_NAME', 'Friends'), user=os.environ.get('DB_USER','postgres'), password=os.environ.get('DB_PASS','password'), port = os.environ.get('DB_PORT', 5405))

#code needs to read the connection information from the environment variable, not just default from my local computer ON FLASK
#figure out flask and python how to consume environment variables. No more local host
#make all the strings dynamic, this will make your code portable
#run docker image with preset environment variables, pass from local code to portable code

#Creates Flask app object and starts the debugger so we can know what goes wrong.
app = flask.Flask(__name__)

app.secret_key ='1234'

@app.route('/', methods=['GET'])
def home():
    return "<h1>Post Quarantine Party List</h1><p>As soon as we get out lets have a day when we go on a hike and get out of Tunis then have a big party.</p>"

@app.route('/api/v1/resources/quarantine_party_list/all', methods=['GET'])

#Returns all of the available entries in the party catalogue.
def api_all():
    # Print PostgreSQL version, test
    cursor = connection_to_docker_postgres.cursor()
    cursor.execute("SELECT * FROM quarantine_party_list")
    record = cursor.fetchall()
    cursor.close()

    return jsonify({"List" : record})

#Checks if the ID was provided as part of the URL, assigns to var, else displays error
@app.route('/api/v1/resources/quarantine_party_list/<key>', methods=['GET'])
def api_id(key):
    cursor = connection_to_docker_postgres.cursor()

    cursor.execute("SELECT * FROM quarantine_party_list WHERE id = %s", (key))
    record = cursor.fetchone()

    cursor.close()
    return jsonify(record)

@app.route('/api/v1/resources/quarantine_party_list', methods=['POST'])
def create_member():
    #figure out how to take the body in flask, validate the body with name id hometown,
    # use it to create sql query to inject into cursor
    cursor = connection_to_docker_postgres.cursor()

    if not request.json:
        abort(400)

    new_id = request.json.get("id")
    new_name = request.json.get("name")
    new_hometown = request.json.get("hometown")


    #create sql query to inject into the cursor
    try:
        test = cursor.execute("INSERT INTO quarantine_party_list (id, name, hometown) VALUES (%s, %s, %s)",
                              (new_id, new_name, new_hometown))
        print("HELP")
    except:
        print("Oops! An exception has occured:")
        print("Exception TYPE:")

    connection_to_docker_postgres.commit()
    cursor.close()

    return jsonify({'name':new_name}), 201

# Updates an existing user entry
@app.route('/api/v1/resources/quarantine_party_list/update', methods=['PUT'])
def update_member():
    cursor = connection_to_docker_postgres.cursor()
    if not request.json:
        abort(400)

    key_id = request.json.get("id")
    new_name = request.json.get("name")
    new_hometown = request.json.get("hometown")

    #validate input

    updated_member = {
        "id": key_id,
        "name": new_name,
        "hometown": new_hometown
    }

    #SQL query to actually update in the database based on the id as a key

    cursor.execute("Update quarantine_party_list SET name = %s, hometown = %s WHERE id = %s",(new_name, new_hometown,key_id))
    connection_to_docker_postgres.commit()

    cursor.close()
    return jsonify({'updated name': new_name}), 201

@app.route('/api/v1/resources/quarantine_party_list/<key>', methods=['DELETE'])
def delete_member(key):
    #delete a member
    cursor = connection_to_docker_postgres.cursor()


    cursor.execute("DELETE FROM quarantine_party_list WHERE id = %s", (key))
    connection_to_docker_postgres.commit()

    cursor.close()

    return jsonify({'name': key}), 201
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000 )
