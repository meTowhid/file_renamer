import sys
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem as tItem, QFileDialog, QHeaderView
import qdarkstyle
from os.path import isfile, join, basename, exists
import os
from functools import partial

Ui_MainWindow, QtBaseClass = uic.loadUiType('app.ui')


class MyApp(QMainWindow, Ui_MainWindow):
    preview = []
    original = []
    current_path = ''

    def rename(self, frm_txt, to_txt):
        count = 0
        frm_txt = frm_txt if self.cb_case.isChecked() else frm_txt.lower()
        for i, name in enumerate(self.preview):
            name = name if self.cb_case.isChecked() else name.lower()
            if frm_txt in name:
                self.preview[i] = name.replace(frm_txt, to_txt, 1)
                count += 1
        return count

    def replace(self):
        frm_txt = self.line_replace_from.text()
        to_txt = self.line_replace_to.text()
        if frm_txt is None or frm_txt == '':
            self.statusbar.showMessage('Text is empty')
            return -1
        return self.rename(frm_txt, to_txt)

    def delete(self):
        txt = self.line_delete_key.text()
        # self.preview = [n.replace(txt, '', 1) for n in self.preview]
        return self.rename(txt, '')

    def insert(self):
        txt = self.line_insert_info.text()
        if txt is None or txt == '':
            self.statusbar.showMessage('Text is empty')
            return -1

        if self.rb_start.isChecked():
            idx = 0
        elif self.rb_end.isChecked():
            idx = -1
        else:
            idx = self.spinBox.value()

        tmp = []
        for n in self.preview:
            i = idx if idx >= 0 else len(n)
            tmp.append(n[:i] + txt + n[i:])
        self.preview = tmp

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

        self.cb_case.stateChanged.connect(partial(self.cb_options_changed, 'case', self.cb_case.isChecked()))
        self.cb_ext.stateChanged.connect(partial(self.cb_options_changed, 'ext', self.cb_ext.isChecked()))
        self.cb_regex.stateChanged.connect(partial(self.cb_options_changed, 'regex', self.cb_regex.isChecked()))

    def cb_options_changed(self, cb, val):
        self.cb[cb] = val

    def onclick_preview(self):
        if not self.original: return
        tab = self.tabWidget.currentIndex()
        count = self.operations[tab](self)
        self.update_table()
        if count != -1:
            self.statusbar.showMessage('{} of {} Files renamed'.format(count, len(self.original)))

    def onclick_reset(self):
        if not self.original: return
        self.preview = self.original.copy()
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
            self.preview = self.original.copy()
            self.current_path = path
            self.update_table()
            self.statusbar.showMessage('{} files loaded'.format(len(self.original)))

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
