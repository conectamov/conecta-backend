import pytest
from playground import create_app, db
from flask_jwt_extended import create_access_token
from models.role import Role
from sqlalchemy import select


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(app):
    name = "etst_user"
    from models.user import User

    user = db.session.scalars(select(User).filter_by(username=name)).first()
    if user is None:
        role = db.session.scalars(select(Role).filter_by(name="user")).first()
        user = User(
            username=name,
            email=name,
            public_title="Anuncio oficial CONECTA",
            role=role,
        )
        user.password = "12345678"
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=user.username)

    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
