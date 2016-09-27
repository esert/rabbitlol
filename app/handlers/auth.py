from app.oauth import (
    oauth_services,
    set_oauth_state,
    verify_oauth_state,
)
from app.commands import Commands
from app.routes import (
    COMMANDS,
    HOME,
    OAUTH_CALLBACK,
    OAUTH_INITIATE,
    PICK_COMMANDS,
    SIGN_IN,
    SIGN_OUT,
)
from app.user import User
from app.utils import (
    Blueprint,
    assert_user_signed_in,
    assert_user_signed_out,
    generate_random_bytes,
    redirect,
    render,
    request,
    set_current_user_key,
)


blueprint = Blueprint('auth', __name__)


@blueprint.route(SIGN_IN)
def sign_in():
    assert_user_signed_out()

    services = [
        'Facebook',
        'GitHub',
        'Google',
        'Twitter',
    ]

    return render('sign_in.html', services=services)


@blueprint.route(OAUTH_INITIATE)
def oauth_initiate(service):
    assert_user_signed_out()

    s = oauth_services.get(service)
    if s == None:
        return redirect(SIGN_IN)

    state = set_oauth_state()
    return redirect(s.getInitiateRedirectURL(state))


@blueprint.route(OAUTH_CALLBACK)
def oauth_callback(service):
    assert_user_signed_out()

    s = oauth_services.get(service)
    if s == None:
        return redirect(SIGN_IN)

    token = None
    if s.name == 'twitter':
        oauth_token = request.args.get('oauth_token', '')
        oauth_verifier = request.args.get('oauth_verifier', '')
        token = s.getAccessToken(oauth_token, oauth_verifier)
        if token == None:
            return redirect(SIGN_IN)
    else:
        state = request.args.get('state', '')
        code = request.args.get('code', '')
        if not verify_oauth_state(state):
            return redirect(SIGN_IN)
        token = s.getAccessToken(state, code)
        if token == None:
            return redirect(SIGN_IN)

    user_id = s.getUserID(token)
    if user_id == None:
        return redirect(SIGN_IN)

    username = '%s:%s' % (service, user_id)
    user = User.fromUsername(username)
    if user == None:
        user = User(
            service=service,
            username=username,
            commands=Commands(),
        )
        user.put()
    user_key = user.key.urlsafe()

    route = COMMANDS
    if user.commands.size() == 0:
        route = PICK_COMMANDS

    set_current_user_key(user_key)
    return redirect(route)


@blueprint.route(SIGN_OUT)
def sign_out():
    assert_user_signed_in()

    set_current_user_key(None)
    return redirect(HOME)
