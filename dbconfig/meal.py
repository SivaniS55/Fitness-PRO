from flask import jsonify, request
import mysql.connector
from dbconfig.config import Config
def get_db_connection():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )
    return conn
def add_meal(data, userid):
    day = data["day"]
    meal_name = data["meal_name"]
    weight = data["weight"]
    time_of_day = data["time_of_day"]
    trainer_id = userid
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO meal_plans (day, trainer_id, meal_name, weight, time_of_day)
        VALUES (%s, %s, %s, %s, %s)  -- Include time_of_day
    """,
        (day, trainer_id, meal_name, weight, time_of_day),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Meal added successfully"})
def update_meal(meal_id, data):
    meal_name = data["meal_name"]
    weight = data["weight"]
    day = data["day"]
    time_of_day = data["time_of_day"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE meal_plans
        SET meal_name = %s, weight = %s, day = %s, time_of_day = %s  -- Update time_of_day
        WHERE meal_id = %s
    """,
        (meal_name, weight, day, time_of_day, meal_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Meal updated successfully"})
def delete_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meal_plans WHERE meal_id = %s", (meal_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Meal deleted successfully"})
def get_meals(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT
        a.meal_id,
        a.day,
        a.meal_name,
        a.weight,
        a.time_of_day,  -- Include time_of_day in the select query
        b.first_name,
        b.last_name
    FROM 
        gym_train.meal_plans a
    LEFT JOIN 
        gym_train.user_details b ON a.trainer_id = b.userid where b.userid = '{userid}';"""
    )
    meals = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "meal_id": row[0],
                "day": row[1],
                "meal_name": row[2],
                "weight": row[3],
                "time_of_day": row[4],
                "trainer_name": f"{row[5]} {row[6]}",
            }
            for row in meals
        ]
    )
def get_meals_by_day(day, userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT meal_name, weight, time_of_day
        FROM meal_plans
        WHERE day = %s and trainer_id = '{userid}'
    """,
        (day,),
    )
    meals = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {"meal_name": row[0], "weight": row[1], "time_of_day": row[2]}
            for row in meals
        ]
    )
