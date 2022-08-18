import os
try:
    from .Website import create_app
    __local__ = False
except ModuleNotFoundError:
    from Website import create_app
    __local__ = True
except ImportError:
    from Website import create_app
    __local__ = True


if __name__ == "__main__":

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print("_______ CALLING CREATE_APP ____________")
        app, socketio = create_app(__local__)
        
        print("_______RUNNNING APP_________")
        if __local__:
            socketio.run(app, debug=True)
        else:
            socketio.run(app, debug=False, use_reloader=False)
