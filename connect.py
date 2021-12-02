from connect import app
import sys

if __name__ == '__main__':
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(port=8080)
    else:
        app.run(port=80)
