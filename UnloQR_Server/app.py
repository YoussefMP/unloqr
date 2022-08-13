try:
    from .Website import create_app
    __local__ = False
except ModuleNotFoundError:
    from Website import create_app
    __local__ = True
except ImportError:
    from Website import create_app
    __local__ = True

print("_______ CALLING CREATE_APP ____________")
app, socketio = create_app()

if __name__ == "__main__":
    print("_______RUNNNING APP_________")
    if __local__:
        socketio.run(app, debug=True)
    else:
        socketio.run(app, debug=False, use_reloader=False)
