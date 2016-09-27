from app.routes import RUN
from app.utils import (
    Blueprint,
    render,
)


blueprint = Blueprint('run', __name__)


@blueprint.route(RUN)
def run():
    return render('run.html')
