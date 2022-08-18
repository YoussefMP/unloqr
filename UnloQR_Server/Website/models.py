from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(timezone=False), default=func.now())
    activity = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video = db.Column(db.String(200))


user_device = db.Table("user_device",
                       db.Column("uid", db.Integer, db.ForeignKey("user.id")),
                       db.Column("did", db.Integer, db.ForeignKey("device.id"))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    email_confirmed = db.Column(db.Boolean, default=False)

    logs = db.relationship("Log", cascade="all, delete")


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dev_name = db.Column(db.String(20), unique=True)
    online = db.Column(db.Boolean, default=False)
    sid = db.Column(db.String(150))
    allowed_users = db.relationship("User", secondary=user_device, backref="allowed_devices", lazy="dynamic")
