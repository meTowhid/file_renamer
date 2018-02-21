import sys
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem as tItem, QFileDialog, QHeaderView
import qdarkstyle
from os.path import isfile, join, basename, exists
import os

Ui_MainWindow, QtBaseClass = uic.loadUiType('renamer_main.ui')


class MyApp(QMainWindow, Ui_MainWindow):
    preview = []
    original = []
    current_path = ''

    def rename(self, frm_txt, to_txt):
        count = 0
        for i, name in enumerate(self.preview.copy()):
            if frm_txt in name:
                self.preview[i] = name.replace(frm_txt, to_txt, 1)
                count += 1
        print(self.original)
        print(self.preview)
        return count

    def replace(self):
        frm_txt = self.line_replace_from.text()
        to_txt = self.line_replace_to.text()
        # self.preview = [n.replace(frm_txt, to_txt, 1) for n in self.preview]
        return self.rename(frm_txt, to_txt)

    def delete(self):
        txt = self.line_delete_key.text()
        # self.preview = [n.replace(txt, '', 1) for n in self.preview]
        return self.rename(txt, '')

    def insert(self):
        idx = self.line_insert_position.text()
        txt = self.line_insert_info.text()
        if idx.isdigit():
            i = int(idx) + 1
            self.preview = [n[:i] + txt + n[i:] for n in self.preview]
        else:
            self.statusbar.showMessage('Invalid digit')
            return -1  # failed
        return len(self.original)

    operations = {0: replace, 1: delete, 2: insert}
    cb = {'case': False, 'ext': False, 'regex': False}

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.btn_load.clicked.connect(self.onclick_load)
        self.btn_preview.clicked.connect(self.onclick_preview)
        self.btn_rename.clicked.connect(self.onclick_rename)
        self.btn_reset.clicked.connect(self.onclick_reset)

        self.cb_case.stateChanged.connect(self.cb_state_changed)
        self.cb_ext.stateChanged.connect(self.ext_state_changed)
        self.cb_regex.stateChanged.connect(self.regex_state_changed)

    def cb_state_changed(self):
        b = self.cb['case'] = self.cb_case.isChecked()
        print(b)

    def ext_state_changed(self):
        b = self.cb['ext'] = self.cb_ext.isChecked()
        print(b)

    def regex_state_changed(self):
        b = self.cb['regex'] = self.cb_regex.isChecked()
        print(b)

    def onclick_preview(self):
        if not self.original: return
        tab = self.tabWidget.currentIndex()
        count = self.operations[tab](self)
        self.update_table()
        if count != -1:
            self.statusbar.showMessage('{} of {} Files renamed'.format(count, len(self.original)))

    def onclick_reset(self):
        if not self.original: return
        self.preview = self.original
        self.update_table()
        self.statusbar.showMessage('Reset to original name')

    def onclick_rename(self):
        count = 0
        for old, new in zip(self.original, self.preview):
            if new != old:
                count += 1
                o = os.path.join(self.current_path, old)
                n = os.path.join(self.current_path, new)
                os.rename(o, n)
        self.original = self.preview
        self.statusbar.showMessage('{} of {} Files renamed'.format(count, len(self.original)))

    def onclick_load(self):
        path = self.line_path.text()
        if path is None or path == '':
            path = QFileDialog.getExistingDirectory(self, 'Choose Folder')
            self.line_path.setText(path)

        if path and exists(path):
            self.original = [f for f in os.listdir(path) if isfile(join(path, f))]
            self.preview = self.original
            self.current_path = path
            self.update_table()
            self.statusbar.showMessage('{} files loaded'.format(len(self.original)))

            # header = self.table.horizontalHeader()
            # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        else:
            self.current_path = ''
            self.statusbar.showMessage('"{}" - Invalid path'.format(path))

    def update_table(self):
        self.table.setRowCount(0)
        for i, name in enumerate(self.preview):
            self.table.insertRow(i)
            self.table.setItem(i, 0, tItem(name))
            self.table.setItem(i, 1, tItem(self.current_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
