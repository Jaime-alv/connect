# Connect
Your own social net.

# Work in Progress
You can create the server and toy with it, but it's not ready and there is no encryption, yet, for data.

![under construction](doc/under_construction.jpg)

# Set up
- Install python from https://www.python.org/ (_built under python 3.9_)
- Download repository [connect.git](https://github.com/Jaime-alv/connect)

- Create a new virtual environment following the instructions in https://docs.python.org/3/library/venv.html

    `python3 -m venv /path/to/new/virtual/environment`
- Activate venv: $ `venv\Scripts\activate`
- Install requirements.txt

   (venv) $ `pip install -r /path/to/requirements.txt`
- Script is ready!
- Run server with connect.py
- Or change directory to  connect top level folder.
- set the FLASK_APP environment variable:  (venv) $ `set FLASK_APP=connect.py`
- Run flask app: (venv) $ `flask run`

# What it does

Chat with only those you know, either in groups or one to one. Create your own virtual and private social net.
