from app.commands import (
    Command,
    Commands,
)
from app.builtin_commands import (
    builtin_command_groups,
    builtin_commands,
)
from app.modifiers import modifiers
from app.routes import (
    COMMANDS,
    DELETE_COMMAND,
    EDIT_COMMAND,
    EDIT_COMMAND_ONLY,
    NEW_COMMAND,
    NEW_COMMAND_ONLY,
    PICK_COMMANDS,
    SAVE_COMMAND,
    SET_DEFAULT_COMMAND,
)
from app.user import get_current_user
from app.utils import (
    Blueprint,
    assert_user_signed_in,
    get_csrf_token,
    get_params,
    redirect,
    render,
    request,
    user_signed_in,
)
from app.validators import ParamException


blueprint = Blueprint('commands', __name__)


@blueprint.route(COMMANDS)
def commands():
    if user_signed_in():
        user = get_current_user()
        return render(
            'commands.html',
            commands=user.commands.asSortedList(),
            default_command=user.getDefaultCommand(),
            command_limit=Commands.limit,
            csrf_token=get_csrf_token(),
        )

    return render(
        'builtin_commands.html',
        builtin_command_groups=builtin_command_groups,
    )


@blueprint.route(PICK_COMMANDS, methods=['GET', 'POST'])
def pick_commands():
    assert_user_signed_in()

    checkbox_prefix = 'checkbox_'
    checked = {}
    error = None
    if request.method == 'POST':
        try:
            params = get_params(request.form)

            user = get_current_user()
            for k in params.iterkeys():
                if k.startswith(checkbox_prefix):
                    command = builtin_commands.get(k[len(checkbox_prefix):])
                    if command != None:
                        checked[command.name] = True
            for k in sorted(checked.keys()):
                user.commands.add(builtin_commands.get(k))
            user.put()
            return redirect(COMMANDS)
        except ParamException as e:
            error = e.message

    return render(
        'pick_commands.html',
        builtin_command_groups=builtin_command_groups,
        checkbox_prefix=checkbox_prefix,
        checked=checked,
        error=error,
        csrf_token=get_csrf_token(),
    )


@blueprint.route(EDIT_COMMAND_ONLY, methods=['GET', 'POST'])
@blueprint.route(EDIT_COMMAND, methods=['GET', 'POST'])
def edit_command(command_name=None):
    assert_user_signed_in()

    if command_name == None:
        return redirect(NEW_COMMAND_ONLY)

    user = get_current_user()
    command = user.commands.get(command_name)
    if command == None:
        return redirect(NEW_COMMAND_ONLY + command_name)

    params = None
    if request.method == 'POST':
        # remove command, it might be renamed
        user.commands.remove(command.name)
        params = get_params(request.form)
        try:
            save_command(**params)
            return redirect(COMMANDS)
        except ParamException as e:
            params['error'] = e.message
            # add the command back, some other code might use it
            # before response is finalized
            user.commands.add(command)
    else:
        params = {
            'name': command.name,
            'description': command.description,
            'url_pattern': command.url_pattern,
            'default_url': command.default_url,
        }

    params['action'] = EDIT_COMMAND_ONLY + command_name
    params['original_command'] = command_name
    params['csrf_token'] = get_csrf_token()
    params['modifiers'] = modifiers

    return render('new_command.html', **params)

@blueprint.route(NEW_COMMAND_ONLY, methods=['GET', 'POST'])
@blueprint.route(NEW_COMMAND, methods=['GET', 'POST'])
def new_command(command_name=None):
    assert_user_signed_in()

    params = {}
    if command_name != None:
        user = get_current_user()
        if user.commands.get(command_name) != None:
            return redirect(EDIT_COMMAND_ONLY + command_name)
        params['name'] = command_name

    if request.method == 'POST':
        params = get_params(request.form)
        try:
            save_command(**params)
            return redirect(COMMANDS)
        except ParamException as e:
            params['error'] = e.message

    params['action'] = NEW_COMMAND_ONLY
    params['csrf_token'] = get_csrf_token()
    params['modifiers'] = modifiers

    return render('new_command.html', **params)


def save_command(
        name=None,
        description=None,
        url_pattern=None,
        default_url=None,
        **kwargs
):
    command = Command(
        name=name,
        description=description,
        url_pattern=url_pattern,
        default_url=default_url,
    )

    user = get_current_user()
    user.commands.add(command)
    user.put()


@blueprint.route(DELETE_COMMAND, methods=['POST'])
def delete_command():
    assert_user_signed_in()

    params = get_params(request.form)

    user = get_current_user()
    command = user.commands.get(params.get('delete'))
    if command != None:
        user.commands.remove(command.name)
        user.put()

    return redirect(COMMANDS)


@blueprint.route(SET_DEFAULT_COMMAND, methods=['POST'])
def set_default_command():
    assert_user_signed_in()

    params = get_params(request.form)
    default_command = params.get('default_command')

    user = get_current_user()
    user.setDefaultCommand(default_command)
    user.put()

    return redirect(COMMANDS)
