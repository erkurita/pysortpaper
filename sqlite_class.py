# SQLite class to abstract the connection to a SQLite database.
from sqlite3 import *
from os import stat

SQL_FILE = 'sql/sql_schema.sql'			


class SQLite(object):
	cursor = None
	connection = None
	sqlite_db_path = ''

	def __new__(clsObject,path):
		base = super(SQLite,clsObject).__new__(clsObject)
		try:
			base.connection = connect(path)
			base.cursor = base.connection.cursor()
		except OperationalError:
			base = None
		return base

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()
	
	def populate_database(self,sql_script_path):
		try:
			sql_file = open(sql_script_path)
		except IOError:
			raise ValueError('populate_database(): SQL file used to populate the DDBB does not exists')
			
		sql_script = ' '.join(sql_file.readlines())	
		try:
			self.connection.executescript(sql_script)
		except ProgrammingError:
			raise ValueError('populate_database(): SQL file has incorrect SQL queries, please check the queries')
		self.connection.commit()
