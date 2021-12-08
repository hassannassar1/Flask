#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  2 22:18:37 2021

@author: hassan
"""

from flask import Flask,render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app,db)


class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String(),nullable=False)
    completed = db.Column(db.Boolean,nullable=False,default=False)
    list_id = db.Column(db.Integer,db.ForeignKey('todolists.id'),nullable=True)
    def __repr__(self):
        return f'Todo {self.id} {self.description}'

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(),nullable=False)
    todos = db.relationship('Todo',backref='list')

    def __repr__(self):
        return f'List {self.id} {self.name}'

@app.route('/')
def index():
    return render_template("s.html",data=Todo.query.order_by('id').all())

@app.route('/todo/create', methods=['POST'])
def create_todo():
    error=False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        #abort (400)
        print(error)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    todo = Todo.query.get(todo_id)
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })
"""
def create_todo():
  description = request.form.get('description', '')
  todo = Todo(description=description)
  db.session.add(todo)
  db.session.commit()
  return redirect(url_for('index'))
  
"""