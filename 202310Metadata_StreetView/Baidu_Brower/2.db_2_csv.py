import csv
import sqlite3

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

def fetch_all_records_from_db(_database_root):
    """从record表中获取所有记录"""
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM record")
        records = cursor.fetchall()
    return records

def save_to_csv(records, csv_filename):
    """将记录保存到CSV文件中"""
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入列名
        writer.writerow(["svid", "lon", "lat", "date", "count_timeline", "north_angle"])
        # 写入数据
        writer.writerows(records)

if __name__ == "__main__":
    database_root = './baidu_hongkong_cycle100.db'
    csv_filename = './baidu_hongkong_cycle100.csv'

    records = fetch_all_records_from_db(database_root)
    save_to_csv(records, csv_filename)
    print(f"Data exported to {csv_filename}")
