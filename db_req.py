#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Данный модуль содержит функции для обращения к базе данных.
Является связующим звеном (интерфейсом) базы данных и основного приложения.
Использует sqlite3.
"""

import sqlite3
import pandas as pd
import os

def check_login(log, pas):
    """
    Проверяет правильность данных учетной записи преподавателя.
    
    :param log: введеный преподавателем логин (str).
    :param pas: введеный преподавателем пароль (str).
    :return: если данные входа верны - [id, name] преподавателя из базы данных. Иначе - None.
    """

    log = log.lower().strip()
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    res = cur.execute("SELECT id, name FROM users WHERE login='{}' AND password='{}'".format(log, pas))
    return res.fetchone()


def get_gr_list():
    """    
    :return: list содержащий названия (str) всех групп из базы данных.
    """  

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM groups")    
    res = [x[0] for x in res.fetchall()]
    return res

def get_stud_dict(gr):
    """
    Запрашивает в базе данных данные всех студентов указанной группы.
    
    :param gr: название группы (str).
    :return: dict содержащий данные всех студентов группы. Имеет ключи 'id', 'name', 'points', 'phone', 'notes'. Значения - list из элементов каждого студента группы.
    """  

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    
    res = cur.execute("SELECT id FROM groups WHERE name='{}'".format(gr))
    gr_id = res.fetchone()
    gr_id = gr_id[0]
    res = cur.execute("SELECT id, name, points, phone, notes FROM students WHERE group_id={}".format(gr_id))
    res_all = res.fetchall()
    d_stud = {}
    ks = ['id', 'name', 'points', 'phone', 'notes']
    for i in range(len(ks)):
        ll = [x[i] for x in res_all]
        d_stud[ks[i]] = ll
    return d_stud


def get_stud_dict_xls(filename, gr):
    """
    Загружает из XLS файла данные всех студентов указанной группы.
    
    :param gr: путь к файлу (str).
    :param gr: название группы (str).
    :return: dict содержащий данные всех студентов группы. Имеет ключи 'id', 'name', 'points', 'phone', 'notes'. Значения - list из элементов каждого студента группы.
    """
    
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM groups WHERE name='{}'".format(gr))
    gr_id = res.fetchone()
    gr_id = gr_id[0]
    
    res_all = pd.read_excel(filename, dtype={'id': int, 'name':str, 'points':int, 'phone':str, 'notes':str, 'group_id':int})
    res_all = res_all.loc[res_all['group_id'] == gr_id]
    
    values = {"id": 0, "name": "", "group_id": 0, "points": 0, "phone": "", "notes": ""}
    res_all.fillna(value=values, inplace=True)
    res_all = res_all[['id', 'name', 'points', 'phone', 'notes']]
    d = res_all.to_dict('list')
    return d


def req_del_stud(id):
    """
    Удаляет из базы данных студента с указанным id.
    
    :param id: id студента (int).
    """     

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("DELETE FROM students WHERE id={}".format(id))
    con.commit()
    return

def get_gr_id(gr):
    """
    Обращаясь к базе данных соотносит название группы и ее id.
    
    :param gr: название группы (str).
    :return: id указанной группы (int).
    """     

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM groups WHERE name='{}'".format(gr))
    return res.fetchone()[0]
    

def req_to_db(d_stud, gr_id):
    """
    Обновляет содержимое таблицы students базы данных - удаляет таблицу, создает новую и заполняет.
    
    :param d_stud: dict содержащий данные всех студентов группы. Имеет ключи 'id', 'name', 'points', 'phone', 'notes'. Значения - list из элементов каждого студента группы.
    :param gr_id: значение id группы (int).
    """    

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    com = "DELETE FROM students WHERE group_id={}".format(gr_id)
    cur.execute(com)
    for i in range(len(d_stud['name'])):
        com = "INSERT INTO students(id, name, group_id, points, phone, notes) VALUES ({}, '{}', {}, {}, '{}', '{}')".format(d_stud['id'][i], d_stud['name'][i], gr_id, d_stud['points'][i], d_stud['phone'][i], d_stud['notes'][i])
        cur.execute(com)
    con.commit()
    return


def req_to_xls(d_stud, gr_id):
    """
    Обновляет содержимое таблицы students базы данных - удаляет таблицу, создает новую и заполняет.
    
    :param d_stud: dict содержащий данные всех студентов группы. Имеет ключи 'id', 'name', 'points', 'phone', 'notes'. Значения - list из элементов каждого студента группы.
    :param gr_id: значение id группы (int).
    """
    fname = 'data.xlsx'
    if os.path.isfile(fname):
        df1 = pd.read_excel(fname)
        df1.drop(df1[df1['group_id'] == gr_id].index, inplace=True)
        df2 = pd.DataFrame.from_dict(d_stud)
        df2['group_id'] = gr_id
        df2 = df2[['id', 'name', 'group_id', 'points', 'phone', 'notes']]
        values = {"id": 0, "name": "", "group_id": 0, "points": 0, "phone": "", "notes": ""}
        df2.fillna(value=values, inplace=True)
        df = pd.concat([df1, df2])
    else:
        df = pd.DataFrame.from_dict(d_stud)
        df['group_id'] = gr_id
        df = df[['id', 'name', 'group_id', 'points', 'phone', 'notes']]
        
    df.to_excel(fname, index=False)
    return












