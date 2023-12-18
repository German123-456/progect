#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Данный скрипт предназначен для начальной конфигурации базы данных при помощи sqlite3.

Запускается один раз.

Создает базу данных (файл data.db в корневой папке проекта), в ней - три таблицы:
1. users(id, name, phone, login, password) - содержит данные учетной записи преподавателей.
2. groups(id, name) - содержит список учебных групп.
3. students(id, name, group_id, points, phone, notes) - содержит список студентов и их данные.

После создания и заполнения каждой таблицы отправляет ее в стандартный вывод.
"""

import sqlite3
import os

if not os.path.isfile("data.db"):
    sqlite3.connect('data.db')
    new = True
else:
    new = False

con = sqlite3.connect("data.db")
cur = con.cursor()

if not new:
    cur.execute("DROP TABLE users")
cur.execute("CREATE TABLE users(id, name, phone, login, password)")
cur.execute("INSERT INTO users VALUES (1, 'Бедретдинов Герман', '+79687861349', 'german', '123')")
res = cur.execute("SELECT * FROM users")
print(res.fetchall())

if not new:
    cur.execute("DROP TABLE groups")
cur.execute("CREATE TABLE groups(id, name)")
cur.execute("INSERT INTO groups(id, name) VALUES (1, 'Программисты'), (2, 'Банкиры')")
res = cur.execute("SELECT * FROM groups")
print(res.fetchall())

if not new:
    cur.execute("DROP TABLE students")
cur.execute("CREATE TABLE students(id, name, group_id, points, phone, notes)")
n = 5
for i in range(1, n + 1):
    cur.execute("INSERT INTO students(id, name, group_id, points, phone, notes) VALUES ({}, 'Вася{}', 1, {}, '+79112223344', '')".format(i*2, i, i))
res = cur.execute("SELECT * FROM students")
print(res.fetchall())

con.commit()






