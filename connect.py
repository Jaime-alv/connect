# Copyright (C) 2021 Jaime Alvarez Fernandez
import sys
from connect import app, db
from connect.models import User, Posts


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Posts': Posts}


if __name__ == "__main__":
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=False, port=8080)
    else:
        app.run(debug=False, port=80)