from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

def get_db_connection():
    """ Connect to the MySQL database and return the connection object"""
    # Database connection parameters
    db_name = "e_commerce_db"
    user = "root"
    password = ""
    host = "localhost"

    try:
        #Attempting to establish a connection
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )

        #Check if the connection is successful
        print("Connected to MySQL database successfully")
        return conn
    
    except Error as e:
        #Handling any connection errors
        print(f"Error: {e}")
        return None
    
class MemberSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

class WorkoutSessionsSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSessionsSchema()
workouts_schema = WorkoutSessionsSchema(many=True)
    

@app.route('/members', methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try: 
        cursor = conn.cursor()
        
        new_member = (member_data['name'], member_data['age'])

        query = "INSERT INTO Members (name, age) VALUES (%s, %s)"
        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members', methods=['GET'])
def get_all_members():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM Members"
        cursor.execute(query)
        members = cursor.fetchall()

        result = members_schema.dump(
            [{"id": member[0], "name": member[1], "age": member[2]} for member in members]
        )

        return jsonify(result), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM Members WHERE id = %s"
        cursor.execute(query, (id,))
        member = cursor.fetchone()
        
        if member is None:
            return jsonify({"error": "Member not found"}), 404
        
        result = member_schema.dump({"id": member[0], "name": member[1], "age": member[2]})

        return jsonify(result), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Members SET age = %s, name = %s WHERE id = %s"
        cursor.execute(query, (member_data['age'], member_data['name'], id))
        conn.commit()
        return jsonify({"message": "Order updated successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        member_to_remove = (id,)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM WorkoutSessions where member_id = %s", member_to_remove)
        cursor.execute("DELETE FROM Members WHERE id = %s", member_to_remove)
        conn.commit()
        return jsonify({"message": "Order deleted successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    

@app.route("/workoutsessions", methods=["POST"])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_workout = (workout_data['member_id'], workout_data['session_date'], workout_data['session_time'], workout_data['activity'])

        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, new_workout)
        conn.commit()

        return jsonify({"message": "New workout added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/workoutsessions', methods=['GET'])
def get_all_workouts():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM WorkoutSessions"
        cursor.execute(query)
        workouts = cursor.fetchall()

        result = workouts_schema.dump(
            [{"session_id": workout[0], "member_id": workout[1], "session_date": workout[2], "session_time": workout[3], "activity": workout[4]} for workout in workouts]
        )
        return jsonify(result), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/workoutsessions/<int:session_id>', methods=['GET'])
def get_one_workout(session_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM WorkoutSessions WHERE session_id = %s"
        cursor.execute(query, (session_id,))
        workout = cursor.fetchone()
        
        if workout is None:
            return jsonify({"error": "Member not found"}), 404
        
        result = workout_schema.dump({"session_id": workout[0], "member_id": workout[1], "session_date": workout[2], "session_time": workout[3], "activity": workout[4]}
        )
        return jsonify(result), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_workout(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE WorkoutSessions SET session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"
        cursor.execute(query, (workout_data['session_date'], workout_data['session_time'], workout_data['activity'], id))
        conn.commit()
        return jsonify({"message": "Order updated successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)