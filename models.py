from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    course = db.Column(db.String(100))
    career_goal = db.Column(db.String(100))

    def __repr__(self):
        return f"<Student {self.name}>"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    skill_name = db.Column(db.String(100), nullable=False)
    skill_level = db.Column(db.String(50), nullable=False)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Skill {self.skill_name}>"


class AssessmentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    skill_name = db.Column(db.String(100), nullable=False)

    question = db.Column(db.String(255), nullable=False)

    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)

    correct_answer = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return f"<AssessmentQuestion {self.id}>"


class AssessmentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<AssessmentResult {self.score}>"


class CareerSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    career_name = db.Column(db.String(100), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    required_level = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<CareerSkill {self.career_name} - {self.skill_name}>"