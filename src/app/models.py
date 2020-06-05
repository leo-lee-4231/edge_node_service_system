# -*- encoding: utf-8 -*-
#
# data models for app
#
# 20-3-30 leo : Init

from datetime import datetime
from . import db


class Book:
    def __init__(self, name, ISBN, author, ID=None):
        self.id = ID
        self.name = name
        self.ISBN = ISBN
        self.author = author

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'ISBN': self.ISBN,
            'author': self.author
        }

    def save(self):
        try:
            with db.connector.cursor() as cursor:
                sql = "INSERT INTO books(name, ISBN, author) " \
                      "VALUES ('%s', '%s', '%s') " \
                      % (self.name, self.ISBN, self.author)
                cursor.execute(sql)
                self.id = cursor.lastrowid
                db.connector.commit()
        except Exception as err:
            db.connector.rollback()
            print('error in save book')
            print(str(err))

    def update(self):
        try:
            with db.connector.cursor() as cursor:
                sql = "UPDATE books SET name = '%s', ISBN = '%s'," \
                      " author = '%s' WHERE id = %s" \
                      % (self.name, self.ISBN, self.author, self.id)
                cursor.execute(sql)
                db.connector.commit()
        except Exception as err:
            db.connector.rollback()
            print('error in update book')
            print(str(err))

    def delete(self):
        try:
            with db.connector.cursor() as cursor:
                sql = "DELETE FROM books WHERE id = %s" % self.id
                cursor.execute(sql)
                db.connector.commit()
        except Exception as err:
            db.connector.rollback()
            print('error in delete book')
            print(str(err))

    @classmethod
    def get_all_books(cls):
        try:
            with db.connector.cursor() as cursor:
                sql = 'SELECT * from books'
                cursor.execute(sql)
                results = cursor.fetchall()
                books = list()
                for book in results:
                    books.append(Book(book[1], book[2], book[3], book[0]))
                return books
        except Exception as err:
            print('error in get all books')
            print(str(err))

    @classmethod
    def get_book_by_id(cls, ID):
        try:
            with db.connector.cursor() as cursor:
                sql = 'SELECT * from books WHERE id = %s' % ID
                cursor.execute(sql)
                result = cursor.fetchone()
                return Book(result[1], result[2], result[3], result[0])
        except Exception as err:
            print('error in get book by id')
            print(str(err))


using_table = db.Table('usings',
    db.Column('application_id', db.Integer, db.ForeignKey('applications.id'), primary_key=True),
    db.Column('device_id', db.Integer, db.ForeignKey('devices.id'), primary_key=True)
)


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ip = db.Column(db.String(32), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    user_info = db.Column(db.String(512))
    status = db.Column(db.String(32), nullable=False)
    parameters = db.Column(db.String(512))
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))

    applications = db.relationship('Application', secondary=using_table,
                                   lazy='subquery',
                                   backref=db.backref('devices', lazy=True))


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(128))
    language = db.Column(db.String(64), nullable=False)
    cpu_priority = db.Column(db.Integer, nullable=False)
    memory = db.Column(db.Integer, nullable=False)
    disk = db.Column(db.Integer, nullable=False)
    bandwidth_priority = db.Column(db.Integer, nullable=False)

    image = db.relationship('Image', backref='application', uselist=False)
    services = db.relationship('Service', backref='application')


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(32), nullable=False)
    image_ref = db.Column(db.String(128), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))


edge_node_relationship = db.Table('edge_node_relationships',
                                  db.Column('main_node_id', db.Integer, db.ForeignKey('edge_nodes.id'), primary_key=True),
                                  db.Column('nearby_node_id', db.Integer, db.ForeignKey('edge_nodes.id'), primary_key=True))


class EdgeNode(db.Model):
    __tablename__ = 'edge_nodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ip = db.Column(db.String(32), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    # power_type = db.Column(db.String(32))
    # console_type = db.Column(db.String(32))
    status = db.Column(db.String(32), nullable=False)
    cpu_capacity = db.Column(db.Integer, nullable=False)
    memory_capacity = db.Column(db.Integer, nullable=False)
    disk_capacity = db.Column(db.Integer, nullable=False)
    bandwidth_capacity = db.Column(db.Integer, nullable=False)
    available_resources = db.relationship('Resource', backref='edge_node')
    services = db.relationship('Service', backref='edge_node')
    records = db.relationship('Record', backref='edge_node')
    logs = db.relationship('Log', backref='edge_node')
    devices = db.relationship('Device', backref='edge_node')
    power_manager = db.relationship('PowerManager', uselist=False, backref='edge_node')
    console_manager = db.relationship('ConsoleManager', uselist=False, backref='edge_node')
    nearby_nodes = db.relationship("EdgeNode", secondary=edge_node_relationship,
                                   primaryjoin=(id == edge_node_relationship.c.main_node_id),
                                   secondaryjoin=(id == edge_node_relationship.c.nearby_node_id))


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    available_value = db.Column(db.Integer, nullable=False)
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    status = db.Column(db.String(32), nullable=False)
    container_ref = db.Column(db.String(128))
    ip = db.Column(db.String(32))
    port = db.Column(db.Integer)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))


class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False, index=True)
    start_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_timestamp = db.Column(db.DateTime, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))

    calls = db.relationship('Call', backref='record')


class Call(db.Model):
    __tablename__ = 'calls'
    id = db.Column(db.Integer, primary_key=True)
    method_name = db.Column(db.String(64), nullable=False)
    start_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_timestamp = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(32), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'))


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    content = db.Column(db.String(512), nullable=False)
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))


class SystemParameter(db.Model):
    __tablename__ = 'system_parameters'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)
    value = db.Column(db.String(512), nullable=False)


class ConsoleManager(db.Model):
    __tablename__ = 'console_managers'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)
    ip = db.Column(db.String(32))
    port = db.Column(db.Integer)
    status = db.Column(db.String(32), nullable=False)
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))

    authorization_keys = db.relationship('AuthorizationKey', backref='console_manager')
    consoles = db.relationship('Console', backref='console_manager')


class AuthorizationKey(db.Model):
    __tablename__ = 'authorization_keys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    key = db.Column(db.String(512))
    console_manager_id = db.Column(db.Integer, db.ForeignKey('console_managers.id'))


class Console(db.Model):
    __tablename__ = 'consoles'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False)
    start_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_timestamp = db.Column(db.DateTime, index=True)
    remote_host_ip = db.Column(db.String(32))
    remote_host_port = db.Column(db.Integer)
    console_manager_id = db.Column(db.Integer, db.ForeignKey('console_managers.id'))


class PowerManager(db.Model):
    __tablename__ = 'power_managers'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False)
    type = db.Column(db.String(32), nullable=False)
    ip = db.Column(db.String(32))
    port = db.Column(db.Integer)
    edge_node_id = db.Column(db.Integer, db.ForeignKey('edge_nodes.id'))
