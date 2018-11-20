from PyQt5 import QtWidgets
import sys
from . import design
import json
import os
from . import webentry


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.exit_button.clicked.connect(self.close_application)
        self.pushButton_chooseReport.clicked.connect(self.browse_folder)
        self.pushButton_startApp.clicked.connect(self.start_application)

        with open(webentry.CONFIG_FILE_NAME) as config_file:
            self.report_info = json.load(config_file)

        self.lineEdit_StartDate.setText(self.report_info['start_date'])
        self.lineEdit_StopDate.setText(self.report_info['end_date'])
        self.lineEdit_email.setText(self.report_info['email_address'])
        self.lineEdit_ReconReport.setText(self.report_info['reconciliation_report_location'])

    def browse_folder(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose Recon Report', '',
                                                          'Excel File (*.xlsx *.xls *.csv)')

        if directory:
            self.lineEdit_ReconReport.setText(directory[0])

    def close_application(self):
        self.close()

    def start_application(self):
        recon_report_name = self.lineEdit_ReconReport.text()
        end_date = self.lineEdit_StopDate.text()
        start_date = self.lineEdit_StartDate.text()
        email_address = self.lineEdit_email.text()
        password = self.lineEdit_password.text()

        print('Recon report: {}, Start Date: {}, End Date: {}'.format(recon_report_name,
                                                                      start_date,
                                                                      end_date))

        self.report_info['email_address'] = email_address
        self.report_info['start_date'] = start_date
        self.report_info['password'] = password
        self.report_info['end_date'] = end_date
        self.report_info['reconciliation_report_location'] = recon_report_name
        try:
            with open(webentry.CONFIG_FILE_NAME, 'w') as config_file:
                saved_version = dict(self.report_info)
                saved_version['password'] = ''
                json.dump(saved_version, config_file, indent=4)
        except PermissionError:
            pass

        try:
            webentry.execute_expense_report('', self.report_info)
        except Exception as e:
            print('Caught an exception: {}'.format(e))


def main():

    sys.path.append(os.path.dirname(__file__))
    app = QtWidgets.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec()


if __name__ == '__main__':
    main()