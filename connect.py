#  connect. Build your own private social net
#  Copyright (C) 2021 Jaime Alvarez Fernandez
#  Contact info: jaime.af.git@gmail.com
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import sys
from connect import app, db
from connect.models import User, Posts


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Posts': Posts}


if __name__ == "__main__":
    if sys.platform == 'darwin':  # different port if running on MacOsX
        app.run(debug=True, port=8080)
    else:
        app.run(debug=True, port=80)
