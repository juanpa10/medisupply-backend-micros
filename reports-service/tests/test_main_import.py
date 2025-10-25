def test_main_import():
    # importing main should create the app variable
    import importlib
    m = importlib.import_module('main')
    assert hasattr(m, 'app')
