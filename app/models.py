from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy=True)


class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    main_emotion = db.Column(db.String(50))
    main_emotion_percentage = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    emotion_reports = db.relationship('EmotionReport', backref='diary_entry', lazy=True)


class EmotionReport(db.Model):
    __tablename__ = 'emotion_reports'
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)
    emotion_name = db.Column(db.String(50))
    emotion_percentage = db.Column(db.Float)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
