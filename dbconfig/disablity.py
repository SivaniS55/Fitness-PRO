import mysql.connector
from flask import jsonify
from dbconfig.config import Config


def get_db_connection():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )
    return conn


def add_disability(userid, name, description, days_suffering, severity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fitness_pro.disability (ds_id, userid, ds_name, description, days_suffering, severity) "
            "VALUES (UUID(), %s, %s, %s, %s, %s)",
            (userid, name, description, days_suffering, severity),
        )
        conn.commit()
        data_insert = {
            "ds_id": cursor.lastrowid,
            "userid": userid,
            "name": name,
            "description": description,
            "days_suffering": days_suffering,
            "severity": severity,
        }
        cursor.close()
        conn.close()
        return data_insert
    except Exception as e:
        print(f"Error in add_disability function: {e}")
        raise


def get_disabilities(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(userid)
    cursor.execute(f""" SELECT * FROM disability where userid = '{userid}' """)
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "id": row[0],
                "name": row[2],
                "description": row[3],
                "days_suffering": row[4],
                "severity": row[5],
            }
            for row in disabilities
        ]
    )


def get_disabilities_all():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM disability ")
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "id": row[0],
                "name": row[2],
                "description": row[3],
                "days_suffering": row[4],
                "severity": row[5],
            }
            for row in disabilities
        ]
    )


def get_disabilities_all_user(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f""" SELECT * FROM disability where userid ='{userid}' """)
    disabilities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(
        [
            {
                "id": row[0],
                "name": row[2],
                "description": row[3],
                "days_suffering": row[4],
                "severity": row[5],
            }
            for row in disabilities
        ]
    )


def delete_disability(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fitness_pro.disability WHERE ds_id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return (
            jsonify(
                {"status": "success", "message": "Disability deleted successfully"}
            ),
            200,
        )
    except Exception as e:
        print(f"Error deleting disability: {e}")
        return jsonify({"error": "Failed to delete disability"}), 500


def update_disability(id, updated_data):
    """
    Update a disability record in the database.
    Parameters:
    - id: The ID of the disability to update
    - updated_data: A dictionary containing the updated fields and their new values
    Returns:
    - JSON response indicating success or failure
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE fitness_pro.disability SET "
        sql += ", ".join([f"{key} = %s" for key in updated_data.keys()])
        sql += " WHERE ds_id = %s"
        values = list(updated_data.values()) + [id]
        cursor.execute(sql, values)
        conn.commit()
        if cursor.rowcount > 0:
            return (
                jsonify(
                    {"status": "success", "message": "Disability updated successfully"}
                ),
                200,
            )
        else:
            return jsonify({"error": "Disability not found"}), 404
    except Exception as e:
        print(f"Error updating disability: {e}")
        return jsonify({"error": "Failed to update disability"}), 500
    finally:
        cursor.close()
        conn.close()
