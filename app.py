from Flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
    jsonify,
)
from dbconfig.models import (
    add_health_assessment,
    add_user,
    addtrainuser,
    trainer_deatls,
    validate_user,
)
from dbconfig.config import Config
import random
import time
from dbconfig.disablity import (
    add_disability,
    delete_disability,
    get_disabilities,
    get_disabilities_all,
    get_disabilities_all_user,
    update_disability,
)
import random
from dbconfig.excersie import (
    add_exercise,
    delete_exercise,
    get_exer,
    get_exer_spec,
    get_exer_spec_user,
    update_exercise,
)
from dbconfig.meal import (
    add_meal,
    delete_meal,
    get_meals,
    get_meals_by_day,
    update_meal,
)
from dbconfig.userend import (
    fetch_exercises,
    fetch_exercises_and_meals,
    get_clients_with_disabilities,
    get_disabilities_hel,
    get_exercises_hel,
    get_health_assessment,
    getheal_check,
    trainer_info,
)

app = Flask(__name__)
app.config.from_object(Config)


def create_userid(first_name, last_name, email, is_trainer=False):
    """Generate a userid by combining first_name, last_name, and email."""
    # Set the prefix based on whether the user is a trainer
    if is_trainer:
        prefix = "TRAINER"
    else:
        prefix = "USR"  # Change to "USR" as per your requirement
    combined = f"{prefix}{first_name}{last_name}{random.randint(100,999)}".replace(
        " ", ""
    ).lower()
    userid = combined[:30].upper()
    return userid


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        dob = request.form["dob"]
        age = request.form["age"]
        phone_number = request.form["phone_number"]
        gender = request.form["gender"]

        is_trainer = request.form.get("is_trainer")


        trainer_info = request.form.get("trainer_info") if is_trainer else None
        print("Is checked")
        print(trainer_info)
        userid = create_userid(
            first_name, last_name, email, is_trainer
        )  # Pass is_trainer here
        success = add_user(
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
        )
        if success:
            flash("Registration successful! You can now log in.")
            return redirect(url_for("login"))
        else:
            flash("Registration failed. Please try again.")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/index")
def index():
    return render_template("nav.html")


@app.route("/disability")
def disability_ui():
    return render_template("disablitylist.html")


@app.route("/hire")
def hire_ui():
    return render_template("hime.html")


@app.route("/health_excer")
def health_excer_ui():
    return render_template("health_exer.html")


@app.route("/userselect")
def userselect_ui():
    userid = session.get("userid")
    data = get_exer_spec_user(userid)
    hel_check = getheal_check(userid)
    print("Helcheck")
    hel_indi = 0
    if len(hel_check) > 0:
        hel_indi = hel_check[0][1]
    if len(data) > 0:
        return render_template("user_navigate.html", data=data, indi=hel_indi)
    else:
        return render_template("user_navigate.html", indi=hel_indi)


@app.route("/home")
def home_ui():
    pagetype = session.get("userid")
    return render_template("home.html", pagetype=pagetype)


@app.route("/exermeal")
def warm_up_ui():
    return render_template("exer_meal.html")


@app.route("/exer")
def exer_ui():
    userid = session.get("userid")
    return render_template("excersie.html", pagetype=userid)


@app.route("/exerspec")
def exer_ui_exerspec():
    return render_template("exer_spec.html")


@app.route("/health")
def health_ui():
    return render_template("health.html")


@app.route("/specmealuser")
def speacmeal_ui():
    return render_template("usermeal_spec.html")


@app.route("/meal")
def meal_ui():
    return render_template("nutrition.html")


def verify_user(email, password):
    return email == email and password == password


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]
        validation_result = validate_user(email, password)[0]
        if validation_result == "success":
            session["userid"] = validate_user(email, password)[1][0]
            session["user"] = email
            flash("Login successful!", "success")
            return redirect(url_for("home_ui"))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/disability/add", methods=["POST"])
def add_disability_insert():
    if request.method == "POST":
        try:
            # Get userid from session
            userid = session.get("userid")
            print(userid)
            if not userid:
                return jsonify({"error": "User not logged in"}), 403
            # Retrieve data from request
            data = request.get_json()
            name = data.get("name")
            description = data.get("description")
            days_suffering = data.get("days_suffering")
            severity = data.get("severity")
            # Validate required fields
            if not all([name, description, days_suffering, severity]):
                return jsonify({"error": "All fields are required"}), 400
            # Insert disability data
            data_insert = add_disability(
                userid, name, description, days_suffering, severity
            )
            return jsonify({"status": "success", "data": data_insert}), 201
        except Exception as e:
            print(f"Error adding disability: {e}")
            return jsonify({"error": "Failed to add disability"}), 500
    else:
        return jsonify({"error": "Invalid request method"}), 405


@app.route("/disabilities", methods=["GET"])
def get_disabilities_list():
    userid = session.get("userid")
    data = get_disabilities(userid)
    return data


@app.route("/disabilitiesall", methods=["GET"])
def get_disabilities_list_all():
    data = get_disabilities_all()
    return data


@app.route("/disabilitiesuserall", methods=["GET"])
def get_disabilities_list_all_userid():
    userid = session.get("userid")
    data = get_disabilities_all_user(userid)
    return data


@app.route("/disability/delete/<string:id>", methods=["DELETE"])
def opration_delete_disability(id):
    print(f"Received ID for deletion: {id}")  # Log the received ID
    try:
        # Attempt to delete the disability by ID
        result = delete_disability(str(id))
        if result:  # Assuming result returns something truthy if deletion is successful
            return {"message": "Disability deleted successfully"}, 200
        else:
            return {"error": "Disability not found"}, 404  # Return 404 if not found
    except Exception as e:
        # Log the exception for debugging
        print(f"Error deleting disability: {e}")
        return {"error": "Internal Server Error"}, 500  # Return 500 for internal errors


@app.route("/disability/update/<string:id>", methods=["PUT"])
def operation_update_disability(id):
    try:
        # Get the updated data from the request body
        updated_data = request.json  # Assuming JSON is sent in the request body
        # Implement your update logic here
        print(updated_data)
        result = update_disability(str(id), updated_data)
        if result:  # Assuming result returns something truthy if update is successful
            return {"message": "Disability updated successfully"}, 200
        else:
            return {"error": "Disability not found"}, 404  # Return 404 if not found
    except Exception as e:
        # Log the exception for debugging
        print(f"Error updating disability: {e}")
        return {"error": "Internal Server Error"}, 500  # Return 500 for internal errors


@app.route("/exercise/add", methods=["POST"])
def add_exercise_ui():
    print("Add Exer")
    userid = session.get("userid")
    print(f"User id {userid}")
    data = request.json
    result = add_exercise(data, userid)
    return result


@app.route("/exercise/update/<exercise_id>", methods=["PUT"])
def update_exercise_ui(exercise_id):
    print(exercise_id)
    data = request.json
    print(data)
    ui_request = update_exercise(exercise_id, data)
    return ui_request


@app.route("/exercise/delete/<exercise_id>", methods=["DELETE"])
def delete_exercise_ui(exercise_id):
    data = delete_exercise(exercise_id)
    return data


@app.route("/addtraineruser", methods=["POST"])
def add_trainer_user():
    userid = session.get("userid")
    data = request.json
    trainerid = data["trainer_id"]
    ui_request = addtrainuser(userid, trainerid)
    return ui_request


@app.route("/exercises", methods=["GET"])
def get_exercises():
    data = get_exer()
    return data


@app.route("/exercisespec", methods=["GET"])
def get_exercises_ui_spec():
    userid = session.get("userid")
    data = get_exer_spec(userid)
    return data


@app.route("/trainall", methods=["GET"])
def trainer_deatls_ui():
    data = trainer_deatls()
    return data


@app.route("/health_assessment", methods=["POST"])
def health_assessment_ui():
    userid = session.get("userid")
    data = request.json
    health_data = add_health_assessment(data, userid)
    return health_data


@app.route("/meal/add", methods=["POST"])
def add_meal_route():
    data = request.json
    userid = session.get("userid")
    return add_meal(data, userid)


@app.route("/meal/update/<int:meal_id>", methods=["PUT"])
def update_meal_route(meal_id):
    data = request.json
    return update_meal(meal_id, data)


@app.route("/meal/delete/<int:meal_id>", methods=["DELETE"])
def delete_meal_route(meal_id):
    return delete_meal(meal_id)


@app.route("/mealspec", methods=["GET"])
def get_meals_route():
    userid = session.get("userid")
    return get_meals(userid)


@app.route("/meals/day/<day>", methods=["GET"])
def get_meals_by_day_ui(day):
    userid = session.get("userid")
    result_meal = get_meals_by_day(day, userid)
    return result_meal


@app.route("/health_assessments", methods=["GET"])
def get_health_assessment_ui_de():
    userid = session.get("userid")
    return get_health_assessment(userid)


@app.route("/userdisabilities", methods=["GET"])
def get_disabilities_ui():
    userid = session.get("userid")
    return get_disabilities_hel(userid)


@app.route("/exercises/<ds_id>", methods=["GET"])
def get_exercises_ui_hel(ds_id):
    return get_exercises_hel(ds_id)


@app.route("/trainerinfo")
def trainer_info_uui():
    userid = session.get("userid")
    data = trainer_info(userid)
    print(data[1][0])
    return render_template(
        "trainer_info.html", trainer_info=data[0][0], disabilities=data[1]
    )


@app.route("/fetch-exercises")
def fetch_exercises_ui():
    ds_id = request.args.get("ds_id")
    datar = fetch_exercises(ds_id)
    return datar


@app.route("/fetch-exercises-and-meals")
def fetch_exercises_and_meals_ui():
    day = request.args.get("day")
    userid = session.get("userid")
    return fetch_exercises_and_meals(day, userid)

@app.route('/trainer-clients', methods=["GET"])
def trainer_clients():
    trainer_id = session.get('userid')
    clients = get_clients_with_disabilities(trainer_id)  
    return render_template('train_user.html', clients=clients)


@app.route('/logout')
def logout():
    
    session.clear()
     
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
