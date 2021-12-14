# microblog

## Server
### Run server

- Open cmd
- change directory to source folder: 

  $ `cd "Path\to\connect"`
- Activate venv: 

  $ `venv\Scripts\activate`
- Set the FLASK_APP environment variable: 

    - **CMD**: (venv) $ `set FLASK_APP=connect.py`
    - **PowerShell**: `$env:FLASK_APP = '.\connect.py'`
    - **Unix Bash**: `$ export FLASK_APP=connect.py`
- Run flask app: 

    (venv) $ `flask run`
 
### Access python shell

- Set the FLASK_APP environment variable
- (venv) $ `flask shell`
- You can use powershell as Python Console

### Debug Mode

- (venv) $ `set FLASK_ENV=development`

## SQL Database

### Creating The Migration Repository

- (venv) $ `flask db init`

### Update Database

- If I have updates to the application models, a new database migration needs to be generated with:

  (venv) $ `flask db migrate -m "comments"`
- And the migration needs to be applied to the database: 

  (venv) $`flask db upgrade`



### Clear database through python console

```
from connect import db
from connect.models import User

users = User.query.all()

for u in users:
  db.session.delete(u)

db.session.commit()
```

