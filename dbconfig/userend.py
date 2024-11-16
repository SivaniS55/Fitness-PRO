from flask import jsonify
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
def get_disabilities_hel(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f""" SELECT ds_id, ds_name FROM disability WHERE userid = '{userid}' """
    )
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{"ds_id": row[0], "ds_name": row[1]} for row in disabilities])
def get_exercises_hel(ds_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT exercise_id, exercise_name, description, day FROM fitness_pro.warm_up_exercises WHERE ds_id = %s",
        (ds_id,),
    )
    exercises = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "exercise_id": row[0],
                "exercise_name": row[1],
                "description": row[2],
                "day": row[3],
            }
            for row in exercises
        ]
    )
def get_health_assessment(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT assessment_id, user_id, height_cm, weight_kg, blood_pressure, heart_rate, notes 
        FROM health_assessments 
        WHERE user_id = %s
    """,
        (userid,),
    )
    health_detail = cursor.fetchone()
    cursor.close()
    conn.close()
    if health_detail:
        return jsonify(
            {
                "assessment_id": health_detail[0],
                "user_id": health_detail[1],
                "height_cm": health_detail[2],
                "weight_kg": health_detail[3],
                "blood_pressure": health_detail[4],
                "heart_rate": health_detail[5],
                "notes": health_detail[6],
            }
        )
    else:
        return jsonify({}), 404
def getheal_check(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f""" SELECT 
a.userid,
    CASE 
        WHEN a.userid = b.user_id THEN 1 
        ELSE NULL 
    END AS user_id
FROM fitness_pro.user_details a
JOIN fitness_pro.health_assessments b ON a.userid = b.user_id WHERE  a.userid = '{userid}' """
    )
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return disabilities
def trainer_info(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        WITH cte1 AS (
            SELECT userid, first_name, last_name, phone_number, email, age, gender, dob, trainer_info
            FROM fitness_pro.trainer_details
        ), cte2 AS (
            SELECT userid, first_name, last_name, phone_number, email, age, gender, dob
            FROM fitness_pro.user_details
        ), cte3 AS (
            SELECT userid, trainer_id
            FROM fitness_pro.subscription
        )
        SELECT b.userid AS trainer_userid, b.first_name AS trainer_first_name, b.last_name AS trainer_last_name,
               b.phone_number AS trainer_phone, b.email AS trainer_email, b.age AS trainer_age,
               b.gender AS trainer_gender, b.dob AS trainer_dob, b.trainer_info
        FROM cte3 a
        LEFT JOIN cte1 b ON a.trainer_id = b.userid
        WHERE a.userid = %s
    """,
        (userid,),
    )
    trainer_info = cursor.fetchall()
    cursor.execute("SELECT * FROM disability WHERE userid = %s", (userid,))
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return [trainer_info, disabilities]
def fetch_exercises(ds_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT exercise_id, ds_id, trainer_id, exercise_name, description, day
        FROM fitness_pro.warm_up_exercises
        WHERE ds_id = %s
    """,
        (ds_id,),
    )
    exercises = cursor.fetchall()
    exercises_list = [
        {
            "exercise_id": exercise[0],
            "ds_id": exercise[1],
            "trainer_id": exercise[2],
            "exercise_name": exercise[3],
            "description": exercise[4],
            "day": exercise[5],
        }
        for exercise in exercises
    ]
    cursor.close()
    conn.close()
    return jsonify(exercises_list)
def fetch_exercises_and_meals(day, userid):
    print(userid)
    if not day:
        return jsonify({"exercises": [], "meals": []})
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT exercise_id, ds_id, trainer_id, exercise_name, description, day
        FROM fitness_pro.warm_up_exercises
        WHERE day = %s and trainer_id = %s
    """,
        (
            day,
            userid,
        ),
    )
    exercises = cursor.fetchall()
    cursor.execute(
        """
        SELECT meal_id, day, trainer_id, meal_name, weight, time_of_day
        FROM fitness_pro.meal_plans
        WHERE day = %s and trainer_id = %s
    """,
        (
            day,
            userid,
        ),
    )
    meals = cursor.fetchall()
    exercises_list = [
        {
            "exercise_id": exercise[0],
            "exercise_name": exercise[3],
            "description": exercise[4],
            "day": exercise[5],
        }
        for exercise in exercises
    ]
    meals_list = [
        {
            "meal_id": meal[0],
            "meal_name": meal[3],
            "weight": meal[4],
            "time_of_day": meal[5],
        }
        for meal in meals
    ]
    cursor.close()
    conn.close()
    return jsonify({"exercises": exercises_list, "meals": meals_list})




def get_clients_with_disabilities(trainer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for clients assigned to the trainer
    cursor.execute("""
        SELECT ud.userid, ud.first_name, ud.last_name, ud.phone_number, ud.email, 
               ud.age, ud.gender, ud.dob
        FROM fitness_pro.user_details ud
        JOIN fitness_pro.subscription s ON s.userid = ud.userid
        WHERE s.trainer_id = %s
    """, (trainer_id,))
    clients = cursor.fetchall()

    # Structure clients data with disabilities
    client_data = []
    for client in clients:
        client_info = {
            "userid": client[0],
            "first_name": client[1],
            "last_name": client[2],
            "phone_number": client[3],
            "email": client[4],
            "age": client[5],
            "gender": client[6],
            "dob": client[7],
            "disabilities": []
        }

        # Query for disabilities of each client
        cursor.execute("""
            SELECT ds_id, ds_name, description, days_suffering, severity
            FROM fitness_pro.disability
            WHERE userid = %s
        """, (client[0],))
        disabilities = cursor.fetchall()

        # Add disabilities to the client
        for disability in disabilities:
            client_info["disabilities"].append({
                "ds_id": disability[0],
                "ds_name": disability[1],
                "description": disability[2],
                "days_suffering": disability[3],
                "severity": disability[4]
            })

        client_data.append(client_info)

    cursor.close()
    conn.close()

    return client_data

