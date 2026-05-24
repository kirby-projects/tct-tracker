from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class TCTContents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_name = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"Coach {self.id} {self.coach_name}"


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        current_coach = request.form.get('coach', '').strip()

        if not current_coach:
            return "Coach name is required", 400

        new_coach = TCTContents(coach_name=current_coach)

        try:
            db.session.add(new_coach)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {e}")
            return f"ERROR: {e}", 500

    coaches = TCTContents.query.order_by(TCTContents.created.desc()).all()
    return render_template('index.html', coaches=coaches)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)