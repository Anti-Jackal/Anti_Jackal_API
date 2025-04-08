from flask import Flask
from models import db, User  # Убедитесь, что User импортирован
from auth import auth_bp
from Settings import Config
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    create_admin(app)  # Передаем app в функцию create_admin
    return app


def create_admin(app):
    admin_username = "admin@admin"
    admin_password = "adminpass"

    with app.app_context():  # Используем контекст приложения
        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(username=admin_username, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Откат транзакции в случае ошибки
                print(f"Ошибка при создании администратора: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
