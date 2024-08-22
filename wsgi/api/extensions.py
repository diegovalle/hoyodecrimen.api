from flask_sqlalchemy import SQLAlchemy

SESSION_OPTIONS = {
    'autocommit': True,
    'autoflush': True,
    'pool_pre_ping': True
}
db = SQLAlchemy(session_options=SESSION_OPTIONS)
