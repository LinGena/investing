from mysql.connector import connect, Error
import time
from config.settings import settings
from utils.logger import Logger


class Db():
    def __init__(self):
        self.logger = Logger().get_logger(__name__)
        self.connecting()
        self.table_tasks = settings.db.table_tasks
        self.table_datas = settings.db.table_datas
        

    def connecting(self, max_retries=10, delay=5) -> None:    
        for attempt in range(max_retries):
            try:
                self.connection = connect(
                    host=settings.db.db_host,
                    port=settings.db.db_port,
                    user=settings.db.db_user,
                    password=settings.db.db_password,
                    database=settings.db.db_database
                )
                self.cursor = self.connection.cursor()
                return 
            except Error as e:
                self.logger.error(f"Connection failed: {e}")
                time.sleep(delay)
        raise Exception("Could not connect to the database after multiple attempts")

    def __del__(self):
        self.close_connection()

    def insert(self, sql: str, params: tuple = None) -> None:
        if not params:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)
        self.connection.commit()

    def select(self, sql: str, with_column_names=False) -> list:
        self.cursor.execute(sql)
        rows = self.cursor.fetchall() 
        if with_column_names:
            column_names = [desc[0] for desc in self.cursor.description]
            return [dict(zip(column_names, row)) for row in rows]
        return rows
        
    def close_connection(self) -> None:
        self.connection.close()


class IsDbCreated():
    def check(self) -> None:
        for attempt in range(5):
            try:
                connection = connect(host=settings.db.db_host, 
                                     port=settings.db.db_port, 
                                     user=settings.db.db_user, 
                                     password=settings.db.db_password)
                cursor = connection.cursor()
                cursor.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''))")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.db.db_database}")
                connection.close()
                IsDbTable().check()
                return
            except Error as e:
                print(f"Connection failed: {e}")
                time.sleep(5)
        raise Exception("Could not connect to MySQL for database creation after multiple attempts.")


class IsDbTable(Db):
    def __init__(self):
        super().__init__()

    def check(self) -> None:
        if self.check_tables(self.table_tasks):
            self.create_tasks()
        if self.check_tables(self.table_datas):
            self.create_datas()
        self.add_missing_fields()

    def add_missing_fields(self) -> None:
        if self.check_row(self.table_tasks, 'from_date'):
            self.insert(f"""ALTER TABLE `{self.table_tasks}` ADD COLUMN `from_date` DATE DEFAULT NULL;""")
        if self.check_row(self.table_tasks, 'to_date'):
            self.insert(f"""ALTER TABLE `{self.table_tasks}` ADD COLUMN `to_date` DATE DEFAULT NULL;""")

    def create_tasks(self) -> None:
        self.insert(f"""
            CREATE TABLE `{self.table_tasks}` (
                `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `symbol` VARCHAR(255),
                `url` VARCHAR(255) NOT NULL UNIQUE,
                `last_update` DATETIME DEFAULT NULL,
                `status` boolean DEFAULT true
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)

    
    def create_datas(self) -> None:
        self.insert(f"""
            CREATE TABLE `{self.table_datas}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL,
                symbol VARCHAR(255),
                key_stats JSON,
                overview JSON,
                profile JSON,
                historical_data JSON,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)
    
    def check_tables(self, table_name: str) -> bool:
        sql = f"SHOW TABLES FROM {settings.db.db_database} LIKE '{table_name}'"
        rows = self.select(sql)
        if len(rows) == 0:
            return True
        return False
    
    def check_row(self, table_name: str, row_name: str) -> bool:
        row_exists = self.select(f"""SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE table_schema = DATABASE()
                                  AND table_name = '{table_name}'
                                  AND column_name = '{row_name}';""")
        if row_exists[0][0] == 0:
            return True
        return False