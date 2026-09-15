from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import func
from models import db, Student, Skill, AssessmentQuestion, AssessmentResult, CareerSkill
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for sessions
app.config["SECRET_KEY"] = "smart-career-portal-secret-key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///career_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        course = request.form["course"]
        career_goal = request.form["career_goal"]

        # Check whether email already exists
        existing_student = Student.query.filter_by(email=email).first()

        if existing_student:
            return "Email already registered. Please use another email."

        # Securely hash the password
        hashed_password = generate_password_hash(password)

        # Create new student
        new_student = Student(
            name=name,
            email=email,
            password=hashed_password,
            course=course,
            career_goal=career_goal
        )

        # Save student to database
        db.session.add(new_student)
        db.session.commit()

        return "Registration successful!"

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find student by email
        student = Student.query.filter_by(email=email).first()

        # Check email and password
        if student and check_password_hash(student.password, password):

            # Store student information in session
            session["student_id"] = student.id
            session["student_name"] = student.name

            return redirect(url_for("dashboard"))

        return "Invalid email or password."

    return render_template("login.html")


# ---------------- STUDENT DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get the logged-in student's information
    student = Student.query.get(session["student_id"])

    return render_template("dashboard.html", student=student)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    # Clear login session
    session.clear()

    return redirect(url_for("login"))
# ---------------- EDIT PROFILE ----------------

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student
    student = Student.query.get(session["student_id"])

    if request.method == "POST":

        student.name = request.form["name"]
        student.course = request.form["course"]
        student.career_goal = request.form["career_goal"]

        db.session.commit()

        # Update name stored in session
        session["student_name"] = student.name

        return redirect(url_for("dashboard"))

    return render_template("edit_profile.html", student=student)

# ---------------- SKILLS MANAGEMENT ----------------

@app.route("/skills", methods=["GET", "POST"])
def skills():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student's ID
    student_id = session["student_id"]

    if request.method == "POST":

        skill_name = request.form["skill_name"]
        skill_level = request.form["skill_level"]

        # Create new skill
        new_skill = Skill(
            skill_name=skill_name,
            skill_level=skill_level,
            student_id=student_id
        )

        # Save skill to database
        db.session.add(new_skill)
        db.session.commit()

    # Get all skills of the logged-in student
    student_skills = Skill.query.filter_by(
        student_id=student_id
    ).all()

    return render_template(
        "skills.html",
        skills=student_skills
    )
# ---------------- DELETE SKILL ----------------

@app.route("/delete-skill/<int:skill_id>")
def delete_skill(skill_id):

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Find the skill
    skill = Skill.query.get_or_404(skill_id)

    # Make sure the skill belongs to the logged-in student
    if skill.student_id != session["student_id"]:
        return "Unauthorized access."

    # Delete the skill
    db.session.delete(skill)
    db.session.commit()

    return redirect(url_for("skills"))
# ---------------- EDIT SKILL ----------------

@app.route("/edit-skill/<int:skill_id>", methods=["GET", "POST"])
def edit_skill(skill_id):

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Find the skill
    skill = Skill.query.get_or_404(skill_id)

    # Make sure the skill belongs to the logged-in student
    if skill.student_id != session["student_id"]:
        return "Unauthorized access."

    if request.method == "POST":

        skill.skill_name = request.form["skill_name"]
        skill.skill_level = request.form["skill_level"]

        # Save changes
        db.session.commit()

        return redirect(url_for("skills"))

    return render_template(
        "edit_skill.html",
        skill=skill
    )
# ---------------- SKILL GAP ANALYSIS ----------------

@app.route("/skill-gap")
def skill_gap():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student = Student.query.get(session["student_id"])

    required_skills = CareerSkill.query.filter_by(
        career_name=student.career_goal
    ).all()

    student_skills = Skill.query.filter_by(
        student_id=student.id
    ).all()

    skill_levels = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3
    }

    analysis = []

    for required in required_skills:

        current_skill = None

        # Find the student's matching skill
        for skill in student_skills:
            if skill.skill_name.lower() == required.skill_name.lower():
                current_skill = skill
                break

        # Missing skill
        if current_skill is None:

            analysis.append({
                "skill_name": required.skill_name,
                "current_level": "Not Added",
                "required_level": required.required_level,
                "status": "Missing"
            })

        # Skill needs improvement
        elif skill_levels[current_skill.skill_level] < skill_levels[required.required_level]:

            analysis.append({
                "skill_name": required.skill_name,
                "current_level": current_skill.skill_level,
                "required_level": required.required_level,
                "status": "Needs Improvement"
            })

        # Skill requirement is satisfied
        else:

            analysis.append({
                "skill_name": required.skill_name,
                "current_level": current_skill.skill_level,
                "required_level": required.required_level,
                "status": "Available"
            })

    return render_template(
        "skill_gap.html",
        student=student,
        analysis=analysis,
        required_skills=required_skills
    )
# ---------------- CAREER RECOMMENDATIONS ----------------

@app.route("/career-recommendation")
def career_recommendation():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student
    student = Student.query.get(session["student_id"])

    # Get student skills
    student_skills = Skill.query.filter_by(
        student_id=student.id
    ).all()

    # Skill level values
    skill_levels = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3
    }

    # Get all career skills
    career_skills = CareerSkill.query.all()

    # Get unique career names
    careers = []

    for item in career_skills:
        if item.career_name not in careers:
            careers.append(item.career_name)

    recommendations = []

    # Check each career
    for career in careers:

        required_skills = CareerSkill.query.filter_by(
            career_name=career
        ).all()

        matched_skills = 0

        # Compare required skills with student skills
        for required in required_skills:

            for student_skill in student_skills:

                if (
                    student_skill.skill_name.lower()
                    == required.skill_name.lower()
                ):

                    if (
                        skill_levels[student_skill.skill_level]
                        >= skill_levels[required.required_level]
                    ):
                        matched_skills += 1

                    break

        # Calculate match percentage
        if len(required_skills) > 0:

            match_percentage = round(
                (matched_skills / len(required_skills)) * 100
            )

        else:
            match_percentage = 0

        recommendations.append({
            "career_name": career,
            "matched_skills": matched_skills,
            "total_skills": len(required_skills),
            "match_percentage": match_percentage
        })

    # Sort careers by best match
    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return render_template(
        "career_recommendation.html",
        student=student,
        recommendations=recommendations
    )
# ---------------- LEARNING RECOMMENDATIONS ----------------

@app.route("/learning-recommendation")
def learning_recommendation():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student
    student = Student.query.get(session["student_id"])

    # Get required skills for student's career goal
    required_skills = CareerSkill.query.filter_by(
        career_name=student.career_goal
    ).all()

    # Get student's current skills
    student_skills = Skill.query.filter_by(
        student_id=student.id
    ).all()

    skill_levels = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3
    }

    recommendations = []

    for required in required_skills:

        current_skill = None

        # Find matching student skill
        for skill in student_skills:

            if skill.skill_name.lower() == required.skill_name.lower():
                current_skill = skill
                break

        # Missing skill
        if current_skill is None:

            recommendations.append({
                "skill_name": required.skill_name,
                "current_level": "Not Added",
                "recommendation":
                f"Learn {required.skill_name} fundamentals and practice regularly."
            })

        # Skill needs improvement
        elif (
            skill_levels[current_skill.skill_level]
            < skill_levels[required.required_level]
        ):

            recommendations.append({
                "skill_name": required.skill_name,
                "current_level": current_skill.skill_level,
                "recommendation":
                f"Improve your {required.skill_name} skills through practice and projects."
            })

    return render_template(
        "learning_recommendation.html",
        student=student,
        recommendations=recommendations
    )
# ---------------- PROGRESS TRACKING ----------------

@app.route("/progress-tracking")
def progress_tracking():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student
    student = Student.query.get(session["student_id"])

    # Get student skills
    student_skills = Skill.query.filter_by(
        student_id=student.id
    ).all()

    # Get latest assessment result
    latest_result = AssessmentResult.query.filter_by(
        student_id=student.id
    ).order_by(
        AssessmentResult.id.desc()
    ).first()

    # Get required skills for career goal
    required_skills = CareerSkill.query.filter_by(
        career_name=student.career_goal
    ).all()

    # Skill level values
    skill_levels = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3
    }

    available_skills = 0
    improvement_skills = 0
    missing_skills = 0

    # Analyze skills
    for required in required_skills:

        current_skill = None

        for skill in student_skills:

            if skill.skill_name.lower() == required.skill_name.lower():
                current_skill = skill
                break

        if current_skill is None:

            missing_skills += 1

        elif (
            skill_levels[current_skill.skill_level]
            < skill_levels[required.required_level]
        ):

            improvement_skills += 1

        else:

            available_skills += 1

    return render_template(
        "progress_tracking.html",
        student=student,
        total_skills=len(student_skills),
        available_skills=available_skills,
        improvement_skills=improvement_skills,
        missing_skills=missing_skills,
        assessment_result=latest_result
    )
# ---------------- SKILL ASSESSMENT ----------------

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student = Student.query.get(session["student_id"])

    # ---------------- SUBMIT ASSESSMENT ----------------

    if request.method == "POST":

        question_ids = session.get("assessment_question_ids", [])

        questions = AssessmentQuestion.query.filter(
            AssessmentQuestion.id.in_(question_ids)
        ).all()

        score = 0

        for question in questions:

            selected_answer = request.form.get(
                f"question_{question.id}"
            )

            if selected_answer == question.correct_answer:
                score += 1

        result = AssessmentResult(
            score=score,
            total_questions=len(questions),
            student_id=student.id
        )

        db.session.add(result)
        db.session.commit()

        session.pop("assessment_question_ids", None)

        return render_template(
            "assessment_result.html",
            score=score,
            total_questions=len(questions)
        )

    # ---------------- CREATE NEW ASSESSMENT ----------------

    # Get only the skills required for the student's career
    career_skills = CareerSkill.query.filter_by(
        career_name=student.career_goal
    ).all()

    relevant_skills = []

    for career_skill in career_skills:

        if career_skill.skill_name not in relevant_skills:
            relevant_skills.append(career_skill.skill_name)

    # Get questions only for the selected career's required skills
    questions = AssessmentQuestion.query.filter(
        AssessmentQuestion.skill_name.in_(relevant_skills)
    ).order_by(
        func.random()
    ).limit(10).all()

    # Store question IDs for submission
    session["assessment_question_ids"] = [
        question.id for question in questions
    ]

    return render_template(
        "assessment.html",
        questions=questions,
        career_goal=student.career_goal
    )
# ---------------- CAREER READINESS ----------------

@app.route("/career-readiness")
def career_readiness():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in student
    student = Student.query.get(session["student_id"])

    # Get student skills
    student_skills = Skill.query.filter_by(
        student_id=student.id
    ).all()

    # Get required skills for career goal
    required_skills = CareerSkill.query.filter_by(
        career_name=student.career_goal
    ).all()

    # Get latest assessment result
    latest_result = AssessmentResult.query.filter_by(
        student_id=student.id
    ).order_by(
        AssessmentResult.id.desc()
    ).first()

    # Skill level values
    skill_levels = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3
    }

    # Count matching skills
    matched_skills = 0

    for required in required_skills:

        for skill in student_skills:

            if skill.skill_name.lower() == required.skill_name.lower():

                if (
                    skill_levels[skill.skill_level]
                    >= skill_levels[required.required_level]
                ):
                    matched_skills += 1

                break

    # Calculate skill readiness percentage
    if len(required_skills) > 0:

        skill_readiness = (
            matched_skills / len(required_skills)
        ) * 100

    else:
        skill_readiness = 0

    # Calculate assessment percentage
    if latest_result and latest_result.total_questions > 0:

        assessment_percentage = (
            latest_result.score
            / latest_result.total_questions
        ) * 100

    else:
        assessment_percentage = 0

    # Final readiness score
    readiness_score = round(
        (skill_readiness * 0.6)
        +
        (assessment_percentage * 0.4)
    )

    # Determine readiness status
    if readiness_score >= 75:
        readiness_status = "Highly Ready"

    elif readiness_score >= 50:
        readiness_status = "Moderately Ready"

    else:
        readiness_status = "Needs Improvement"

    return render_template(
        "career_readiness.html",
        student=student,
        readiness_score=readiness_score,
        readiness_status=readiness_status,
        matched_skills=matched_skills,
        total_required_skills=len(required_skills),
        assessment_result=latest_result
    )
# ---------------- CREATE DATABASE TABLES ----------------
with app.app_context():
    db.create_all()

# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
    