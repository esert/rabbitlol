from app.routes import (
    SETUP,
    SETUP_ONLY,
)
from app.utils import (
    Blueprint,
    render,
    request,
)


blueprint = Blueprint('setup', __name__)


supported_platforms = set(['windows', 'linux', 'macos'])


@blueprint.route(SETUP_ONLY)
@blueprint.route(SETUP)
def setup(browser=None):
    no_browser_given = False
    if browser == None:
        browser = request.user_agent.browser
    else:
        no_browser_given = True
    if request.user_agent.platform in supported_platforms or no_browser_given:
        if browser == 'chrome':
            return render('setup_chrome.html')
        if browser == 'firefox':
            return render('setup_firefox.html')
    return render('no_setup.html')
