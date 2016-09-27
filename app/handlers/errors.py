import logging

from app.utils import (
    RedirectException,
    redirect,
    render,
)


def not_found(e):
    return render('404.html')


def server_error(e):
    if isinstance(e, RedirectException):
        return redirect(e.route)

    # Log the error and stacktrace.
    logging.exception('unhandled exception')
    return render('error.html')
