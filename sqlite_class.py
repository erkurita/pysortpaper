# SQLite class to abstract the connection to a SQLite database.
from sqlite3 import *
from os import stat

SQL_FILE = 'sql/sql_schema.sql'			

def populate_database(path,sql_script_path):
	try:
		sql_file = open(sql_script_path)
	except IOError:
		raise ValueError('populate_database(): SQL file used to populate the DDBB does not exists')
		
	sql_script = ' '.join(sql_file.readlines())	
	conn = connect(path)
	try:
		cursor = conn.executescript(sql_script)
	except ProgrammingError:
		raise ValueError('populate_database(): SQL file has incorrect SQL queries, please check the queries')
	conn.commit()
	cursor.close()

class SQLite(object):
	cursor = None
	connection = None

	def __new__(clsObject,path):
		base = super(SQLite,clsObject).__new__(clsObject)
		try:
			try:
				# Testing wether the database exists already
				stat(path)
			except OSError:
				# In case not, we need to create one with the tables needed
				try:
					populate_database(path,SQL_FILE)
				except ValueError,msg:
					raise ValueError('SQLite constructor: '+msg)
			base.connection = connect(path)
			base.cursor = base.connection.cursor()
		except OperationalError:
		
			base = None
		return base

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()
