import app.routes as routes


def test_routes():
    all_routes = []
    for name in dir(routes):
        if name.startswith('__'):
            continue
        all_routes.append(getattr(routes, name))

    assert len(all_routes) > 0 and len(all_routes) == len(set(all_routes))
    for route in all_routes:
        assert route.startswith('/')
