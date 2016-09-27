from app.secrets import (
    APP_SECRET_KEY,
    FACEBOOK_APP_ID,
    FACEBOOK_APP_SECRET,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)


def test_secrets():
    assert APP_SECRET_KEY != ''
    assert FACEBOOK_APP_ID != ''
    assert FACEBOOK_APP_SECRET != ''
    assert GITHUB_CLIENT_ID != ''
    assert GITHUB_CLIENT_SECRET != ''
    assert GOOGLE_CLIENT_ID != ''
    assert GOOGLE_CLIENT_SECRET != ''
    assert TWITTER_CONSUMER_KEY != ''
    assert TWITTER_CONSUMER_SECRET != ''
