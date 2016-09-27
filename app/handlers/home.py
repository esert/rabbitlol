from app.commands import (
    MalformedQueryException,
    NotEnoughArgumentsException,
    UnknownCommandException,
    UnknownDefaultCommandException,
)
from app.builtin_commands import (
    builtin_commands,
    get_sample_queries,
)
from app.routes import (
    HOME,
    SIGN_OUT,
)
from app.user import get_current_user
from app.utils import (
    Blueprint,
    get_params,
    redirect,
    render,
    request,
    user_signed_in,
)


blueprint = Blueprint('home', __name__)


@blueprint.route(HOME)
def home():
    params = get_params(request.args)

    query = params.get('q')
    if query == None:
        return render('home.html', sample_queries=get_sample_queries())
    default_command = params.get('default')

    try:
        commands = builtin_commands
        if user_signed_in():
            user = get_current_user()
            commands = user.commands
            default_command = user.getDefaultCommand()

        return redirect(commands.getRedirectUrl(query, default_command))
    except (NotEnoughArgumentsException,
            UnknownCommandException,
            UnknownDefaultCommandException) as e:
        return render(
            'command_error.html',
            exception_type=e.__class__.__name__,
            exception=e,
        )
    except MalformedQueryException:
        return redirect(HOME)
