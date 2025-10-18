def test_do_init_no_db():
    # calling do_init when DB not enabled should be a no-op (no exception)
    import importlib.util, sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    module_path = root / "init_db.py"
    spec = importlib.util.spec_from_file_location("auth_init_db", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.do_init()
    mod.do_seed()
    assert True
