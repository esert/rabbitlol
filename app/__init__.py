from app.handlers.auth import blueprint as auth_blueprint
from app.handlers.commands import blueprint as commands_blueprint
from app.handlers.errors import (
    not_found,
    server_error,
)
from app.handlers.home import blueprint as home_blueprint
from app.handlers.run import blueprint as run_blueprint
from app.handlers.setup import blueprint as setup_blueprint
from app.secrets import APP_SECRET_KEY
from app.utils import (
    Flask,
    before_request,
    request,
    timedelta,
)


app = Flask(__name__)
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(days=30 * 365),
    SECRET_KEY = APP_SECRET_KEY,
)


app.before_request(before_request)


app.register_blueprint(home_blueprint)
app.register_blueprint(commands_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(setup_blueprint)
app.register_blueprint(run_blueprint)
app.register_error_handler(404, not_found)
app.register_error_handler(Exception, server_error)
