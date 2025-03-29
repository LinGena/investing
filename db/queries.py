from db.core import Db
import json


class Queries(Db):
    def __init__(self):
        super().__init__()

    def get_task(self) -> dict:
        sql = f"""SELECT id, url FROM {self.table_tasks} 
        WHERE status=true AND (last_update IS NULL OR last_update < NOW() - INTERVAL 1 DAY)
        ORDER BY RAND()
        LIMIT 1"""
        row = self.select(sql, with_column_names=True)
        if row:
            return row[0]
        return None
    
    def change_status(self, id: int) -> None:
        sql = f"UPDATE {self.table_tasks} SET status = NOT status WHERE id = %s"
        self.insert(sql, (id,))

    def update_last_date(self, id: int) -> None:
        sql = f"UPDATE {self.table_tasks} SET last_update = NOW() WHERE id = %s"
        self.insert(sql, (id,))

    def update_datas(self, id: int, data: dict) -> None:
        sql = f"""INSERT INTO {self.table_datas} 
        (task_id, symbol, key_stats, overview, profile, historical_data) 
        VALUES (%s, %s, %s, %s, %s, %s)"""
        symbol = data['symbol']
        key_stats = json.dumps(data['key_stats'])
        overview = json.dumps(data['overview'])
        profile = json.dumps(data['profile'])
        historical_data = json.dumps(data['historical_data'])
        self.insert(sql, (id, symbol, key_stats, overview, profile, historical_data))