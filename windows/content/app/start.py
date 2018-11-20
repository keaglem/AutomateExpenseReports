import os
import sys

basedir = os.path.dirname(os.path.dirname(__file__))

sys.path.append(os.path.join(basedir, 'app'))
sys.path.append(os.path.join(basedir, 'app_packages'))

from automateExpenseReports.app import main
if __name__ == '__main__':
    main()
