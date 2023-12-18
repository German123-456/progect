#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создает и запускает графический пользовательский интерфейс (оконное приложение).
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import numpy as np
import PIL
import sys
import cv2
import os
import glob
import shutil
from db_req import *

def del_stud(idx):
    """
    Удаляет из таблицы students базы данных запись о студенте с указанным id.
    После чего отображает в окне обновленные данные группы.
    
    :param idx: id студента (int).
    """

    if win.approve_del(idx):
        req_del_stud(idx)
        win.show_table(win.gr)
    return

class MyWindow(QMainWindow):
    """Класс окна"""

    def __init__(self):
        """
        Инициализирует окно.
        """

        super(MyWindow,self).__init__()
        self.user_id = -1
        self.initUI()
    
    def login(self):
        """
        Проверяет данные входа, введеные пользователем.
        """

        res = check_login(self.le_login.text(), self.le_pass.text())
        if res != None:
            self.user_id = res[0]
            self.l_login.setText(res[1])
            self.b_show_gr.show()
        else:
            self.l_login.setText('Пользователь не найден')
        return

    def show_select_gr(self):
        """
        Отображает элемент для выбора группы.
        """

        self.comb_gr.show()
        self.gr_list = get_gr_list()
        self.comb_gr.clear()
        self.comb_gr.addItem('')
        for gr in self.gr_list:
            self.comb_gr.addItem(gr)
        return
        
        
    def show_table(self, gr, mode='db', filename=None):
        """
        Показывает таблицу с данными всех студентов группы.
        
        :param gr: название группы (str).
        """
        
        if gr == '':
            return
        self.gr = gr
        self.gr_id = get_gr_id(self.gr)
        
        if mode=='db':
            self.stud_dict = get_stud_dict(gr)
        elif mode=='xls':
            self.stud_dict = get_stud_dict_xls(filename, gr)
        
        self.stud_ids = self.stud_dict['id']
        self.n_stud = len(self.stud_dict['name'])
        self.n_cols = len(self.stud_dict.keys())
        self.n_rows = self.n_stud
        self.gr_table.setColumnCount(self.n_cols)
        self.gr_table.setRowCount(self.n_rows)
        self.gr_table.setHorizontalHeaderLabels(list(self.stud_dict.keys())[1:] + [''])
        self.gr_table.setVerticalHeaderLabels(list(map(str, self.stud_dict['id'])))

        for col, key in enumerate(list(self.stud_dict.keys())):
            for row, item in enumerate(self.stud_dict[key]):
                if key != 'id':
                    newitem = QtWidgets.QTableWidgetItem(str(item))
                    self.gr_table.setItem(row, col - 1, newitem)
        
        path = os.getcwd()
        pic = QtGui.QPixmap("del.png")
        for i in range(self.n_rows):
            coms = []
            coms.append('self.b{} = QtWidgets.QPushButton(self)'.format(i))
            coms.append('self.b{}.setStyleSheet("background-image: url(del.png);")'.format(i))
            idx = self.stud_dict['id'][i]
            #coms.append('self.b{}.clicked.connect(lambda :del_stud({}))'.format(i, idx))
            coms.append('self.gr_table.setCellWidget({}, 4, self.b{})'.format(i, i))
            for com in coms:
                exec(com)
        self.gr_table.resizeColumnsToContents()
        self.gr_table.setColumnWidth(0, 183)
        self.gr_table.setColumnWidth(3, 210)
        self.gr_table.setColumnWidth(4, 5)
        self.gr_table.resizeRowsToContents()
        self.gr_table.setGeometry(30, 170, self.winw - 200, min((self.n_stud) * 26 + 24, self.winh - 200))
        self.gr_table.show()
        self.b_to_db.show()
        self.b_from_db.show()
        self.b_to_xls.show()
        self.b_from_xls.show()
        return

    def approve_del(self, s_id):
        """
        Вызывает диалоговое окно для подтверждения удаления записи студента с указанным id.
        
        :param s_id: id студента (int).
        :return: ответ пользователя (True/False).
        """

        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Удаление записи")
        idx = self.stud_dict['id'].index(s_id)
        name = self.stud_dict['name'][idx]
        dlg.setText("Точно удалить студента {}?".format(name))
        dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dlg.setIcon(QtWidgets.QMessageBox.Question)
        button = dlg.exec()
        if button == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    '''
    def change_student(self, row, col):
        """
        Вызывает диалоговое окно для подтверждения удаления записи студента с указанным id.

        :param s_id: id студента (int).
        :return: ответ пользователя (True/False).
        """

        cols = ['name', 'points', 'phone', 'notes']
        field = cols[col-1]
        stud_id = self.stud_dict['id'][row-1]
        return
    '''

    def to_db(self):
        """
        Посылает запрос на обновление записей в базе данных используя текущие значения в таблице.
        """

        d = {}
        keys = ['id', 'name', 'points', 'phone', 'notes']
        self.n_cols = len(self.stud_dict.keys())
        self.n_rows = self.n_stud
        d['id'] = self.stud_ids
        for col in range(self.n_cols - 1):
            for row in range(self.n_rows):
                k = keys[col + 1]
                v = self.gr_table.item(row, col).text()
                if k in d.keys():
                    d[k].append(v)
                else:
                    d[k] = [v]
        gr_id =  get_gr_id(self.gr)
        req_to_db(d, gr_id)
        self.show_table(d)

        return
    
    def from_db(self):
        """
        Обновляет содержимое таблицы записями из базы данных.
        """        

        self.gr_table.hide()
        self.gr_table = None
        self.gr_table = QtWidgets.QTableWidget(self)
        t_font = self.font()
        t_font.setPointSize(10)
        self.gr_table.setFont(t_font)
        self.show_table(self.gr, mode='db')
        return

    def to_xls(self):
        """
        Выгружает текущую таблицу в Excel файл.
        """

        d = {}
        keys = ['id', 'name', 'points', 'phone', 'notes']
        self.n_cols = len(self.stud_dict.keys())
        self.n_rows = self.n_stud
        d['id'] = self.stud_ids
        for col in range(self.n_cols - 1):
            for row in range(self.n_rows):
                k = keys[col + 1]
                v = self.gr_table.item(row, col).text()
                if k in d.keys():
                    d[k].append(v)
                else:
                    d[k] = [v]
        gr_id =  get_gr_id(self.gr)
        req_to_xls(d, gr_id)
        return
    
    def from_xls(self):
        """
        Обновляет содержимое таблицы записями из Excel файла.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fname, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*)", options=options)
        if fname:
            self.gr_table.hide()
            self.gr_table = None
            self.gr_table = QtWidgets.QTableWidget(self)
            t_font = self.font()
            t_font.setPointSize(10)
            self.gr_table.setFont(t_font)
            self.show_table(self.gr, mode='xls', filename=fname)
        return



    def initUI(self):
        """
        Инициализирует пользовательский интерфейс.
        """

        self.winw = 800
        self.winh = 800
        self.setGeometry(100, 100, self.winw, self.winh)
        self.setWindowTitle("Преподаватели")
        
        self.b_login = QtWidgets.QPushButton(self)
        self.b_login.setText("Войти")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_login.setFont(b_font)
        self.b_login.setGeometry(300, 30, 80, 30)
        self.b_login.clicked.connect(self.login)

        self.l_login = QtWidgets.QLabel(self)
        self.l_login.setText("")
        l_font = self.font()
        l_font.setPointSize(12)
        self.l_login.setFont(l_font)
        self.l_login.setGeometry(300, 55, 250, 60)
        self.l_login.setWordWrap(True)
        
        self.le_login = QtWidgets.QLineEdit(self)
        self.le_login.setGeometry(30, 30, 200, 30)
        self.le_login.setMaxLength(20)
        self.le_login.setPlaceholderText("Логин")

        self.le_pass = QtWidgets.QLineEdit(self)
        self.le_pass.setGeometry(30, 70, 200, 30)
        self.le_pass.setMaxLength(20)
        self.le_pass.setPlaceholderText("Пароль")
        
        self.b_show_gr = QtWidgets.QPushButton(self)
        self.b_show_gr.setText("Показать группу")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_show_gr.setFont(b_font)
        self.b_show_gr.setGeometry(30, 120, 150, 30)
        self.b_show_gr.hide()
        self.b_show_gr.clicked.connect(self.show_select_gr)
        
        self.comb_gr = QtWidgets.QComboBox(self)
        self.comb_gr.setGeometry(200, 120, 150, 30)
        self.comb_gr.hide()
        self.comb_gr.currentTextChanged.connect(self.show_table)
        
        self.gr_table = QtWidgets.QTableWidget(self)
        t_font = self.font()
        t_font.setPointSize(10)
        self.gr_table.setFont(t_font)
        self.gr_table.hide()
        #self.gr_table.cellChanged.connect(self.change_student)

        self.b_to_db = QtWidgets.QPushButton(self)
        self.b_to_db.setText("В базу")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_to_db.setFont(b_font)
        self.b_to_db.setGeometry(670, 170, 80, 30)
        self.b_to_db.hide()
        self.b_to_db.clicked.connect(self.to_db)

        self.b_from_db = QtWidgets.QPushButton(self)
        self.b_from_db.setText("Из базы")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_from_db.setFont(b_font)
        self.b_from_db.setGeometry(670, 220, 80, 30)
        self.b_from_db.hide()
        self.b_from_db.clicked.connect(self.from_db)

        self.b_to_xls = QtWidgets.QPushButton(self)
        self.b_to_xls.setText("В Excel")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_to_xls.setFont(b_font)
        self.b_to_xls.setGeometry(670, 270, 80, 30)
        self.b_to_xls.hide()
        self.b_to_xls.clicked.connect(self.to_xls)

        self.b_from_xls = QtWidgets.QPushButton(self)
        self.b_from_xls.setText("Из Excel")
        b_font = self.font()
        b_font.setPointSize(12)
        self.b_from_xls.setFont(b_font)
        self.b_from_xls.setGeometry(670, 320, 80, 30)
        self.b_from_xls.hide()
        self.b_from_xls.clicked.connect(self.from_xls)

def window():
    """
    Инициализирует приложение.
    """

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    app.exec_()
    return win
    

win = window()














