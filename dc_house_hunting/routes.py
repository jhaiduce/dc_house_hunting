def includeme(config):
    config.add_static_view('deform_static', 'deform:static/')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('import','/import')
    config.add_route('score_weights','/score_weights')
    config.add_route('residence_details','/residence/{residence_id}/details')
