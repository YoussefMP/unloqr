try:
    from .Website import create_app
except ModuleNotFoundError:
    from Website import create_app

print("_______ CALLING CREATE_APP ____________")
app, socketio = create_app()

if __name__ == "__main__":
    print("_______RUNNNING APP_________")
    socketio.run(app, debug=False, use_reloader=False)
