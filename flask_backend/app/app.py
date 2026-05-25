from datetime import datetime, timezone

from flask import Flask, render_template, redirect, request, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class TCTContents(db.Model):
    coach_id = db.Column(db.Integer, primary_key=True)
    coach_name = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"Coach {self.coach_id} {self.coach_name}"


with app.app_context():
    db.create_all()


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
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"ERROR: {e}", 500

    coaches = TCTContents.query.order_by(TCTContents.created.desc()).all()
    return render_template('index.html', coaches=coaches)


@app.route('/delete/<int:coach_id>', methods=['POST'])
def delete(coach_id):
    coach = TCTContents.query.get_or_404(coach_id)

    try:
        db.session.delete(coach)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return f"ERROR: {e}", 500


@app.route('/edit/<int:coach_id>', methods=['GET', 'POST'])
def edit(coach_id):
    coach = TCTContents.query.get_or_404(coach_id)

    if request.method == "POST":
        current_name = request.form.get('coach_name', '').strip()

        if not current_name:
            return "Coach name is required", 400

        try:
            coach.coach_name = current_name
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"ERROR: {e}", 500

    return render_template('edit.html', coach=coach)


if __name__ == "__main__":
    app.run(debug=True)
