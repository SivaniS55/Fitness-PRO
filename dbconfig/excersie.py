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


def add_exercise(data, userid):
    ds_id = data["ds_id"]
    trainer_id = userid
    exercise_name = data["exercise_name"]
    description = data["description"]
    day = data["day"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO warm_up_exercises (ds_id, trainer_id, exercise_name,description,day)
        VALUES (%s, %s, %s, %s,%s)
    """,
        (ds_id, trainer_id, exercise_name, description, day),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Exercise added successfully"})


def update_exercise(exercise_id, data):
    exercise_name = data["exercise_name"]
    description = data["description"]
    day = data["day"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE warm_up_exercises
        SET  exercise_name = %s, description = %s ,day = %s
        WHERE exercise_id = %s
    """,
        (exercise_name, description, day, exercise_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Exercise updated successfully"})


def delete_exercise(exercise_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM warm_up_exercises WHERE exercise_id = %s", (exercise_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Exercise deleted successfully"})


def get_exer():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
    d.ds_name,
    a.exercise_id,
    COALESCE(CONCAT(b.first_name, ' ', b.last_name), CONCAT(c.first_name, ' ', c.last_name)) AS full_name,
    a.exercise_name, 
    a.description,
    a.day
FROM 
    gym_train.warm_up_exercises a
LEFT JOIN 
    gym_train.trainer_details b ON a.trainer_id = b.userid
LEFT JOIN 
    gym_train.disability d ON a.ds_id = d.ds_id
LEFT JOIN 
    gym_train.user_details c ON a.trainer_id = c.userid;
"""
    )
    get_exer = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "ds_name": row[0],
                "exercise_id": row[1],
                "full_name": row[2],
                "exercise_name": row[3],
                "description": row[4],
                "day": row[5],
            }
            for row in get_exer
        ]
    )


def get_exer_spec(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""with cte1 as (
SELECT
    d.ds_name,
    a.exercise_id,
    COALESCE(CONCAT(b.first_name, ' ', b.last_name), CONCAT(c.first_name, ' ', c.last_name)) AS full_name,
    a.exercise_name, 
    a.description,
    a.day,
    COALESCE(c.userid, b.userid) AS userid
FROM 
    gym_train.warm_up_exercises a
LEFT JOIN 
    gym_train.trainer_details b ON a.trainer_id = b.userid
LEFT JOIN 
    gym_train.disability d ON a.ds_id = d.ds_id
LEFT JOIN 
    gym_train.user_details c ON a.trainer_id = c.userid)
    select * from cte1 where userid ='{userid}'
"""
    )
    get_exer = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "ds_name": row[0],
                "exercise_id": row[1],
                "full_name": row[2],
                "exercise_name": row[3],
                "description": row[4],
                "day": row[5],
            }
            for row in get_exer
        ]
    )


def get_exer_spec_user(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""with cte1 as (
select userid, first_name, last_name, phone_number, email, age, gender, dob, password, trainer_info from gym_train.trainer_details
),cte2 as (
select userid, first_name, last_name, phone_number, email, age, gender, dob, password from gym_train.user_details ud 
),cte3 as (
select userid, trainer_id from gym_train.subscription
)
select 
*
from 
cte3 a
left join cte1 b on a.trainer_id=b.userid
left join cte2 c on a.userid=c.userid where c.userid='{userid}'
"""
    )
    get_exer = cursor.fetchall()
    cursor.close()
    conn.close()
    return get_exer
