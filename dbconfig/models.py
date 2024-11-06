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



def add_user(
          userid,
            first_name,
            last_name,
            email,
            password,
            dob,
            age,
            phone_number,
            gender,
            is_trainer,
            trainer_info
    
):
    if is_trainer:
        print(trainer_info)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO trainer_details (userid, first_name, last_name, email, password, dob, age, phone_number, gender,trainer_info)
            VALUES (%s,%s, %s, %s, %s, %s,%s, %s, %s,%s)
        """,
            (
                userid,
                first_name,
                last_name,
                email,
                password,
                dob,
                age,
                phone_number,
                gender,
                trainer_info
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "success"
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_details (userid, first_name, last_name, email, password, dob, age, phone_number, gender)
            VALUES (%s,%s, %s, %s, %s, %s,%s, %s, %s)
        """,
            (
                userid,
                first_name,
                last_name,
                email,
                password,
                dob,
                age,
                phone_number,
                gender,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "success"


def validate_user(e_mail, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""WITH cte1 AS (
    SELECT userid, first_name, last_name, phone_number, email, age, gender, dob, password,"I'm User" AS trainer_info FROM fitness_pro.user_details
),
cte2 AS (
    SELECT * FROM fitness_pro.trainer_details
)
,login as (
SELECT * FROM cte1
UNION
SELECT * FROM cte2 )
select * from login 
 WHERE email = '{e_mail}' AND password = '{password}' """
    )
    result = cursor.fetchone()
    print(result)
    return ["success", result] if result else ["failure", 0]


"userid", "first_name", "last_name", "phone_number", "email", "age", "gender", "dob", "password", "trainer_info"


def trainer_deatls():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""select * from trainer_details """)
    get_exer = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "userid": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "phone_number": row[3],
                "email": row[4],
                "age": row[5],
                "gender": row[6],
                "dob": row[7],
                "password": row[8],
                "trainer_info": row[9],
            }
            for row in get_exer
        ]
    )


def addtrainuser(userid, trainerid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO subscription (userid,trainer_id)
        VALUES (%s, %s)
    """,
        (userid, trainerid),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Exercise added successfully"})


def add_health_assessment(data, user_id):
    
    height_cm = data.get("height_cm")
    weight_kg = data.get("weight_kg")
    blood_pressure = data.get("blood_pressure")
    heart_rate = data.get("heart_rate")
    notes = data.get("notes")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO health_assessments (user_id, height_cm, weight_kg, blood_pressure, heart_rate, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        (user_id, height_cm, weight_kg, blood_pressure, heart_rate, notes),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Health assessment added successfully"})
