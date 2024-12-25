import pandas as pd
import pymysql
from config import MYSQL_CONFIG

def create_database():
    """创建数据库"""
    # 创建数据库连接（不指定数据库）
    config = MYSQL_CONFIG.copy()
    del config['database']  # 删除database配置项
    
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 创建数据库
        database = MYSQL_CONFIG['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {database} 创建成功")
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")
    finally:
        cursor.close()
        conn.close()

def create_table():
    """创建数据表"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # 创建表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schools (
            school_name VARCHAR(100) PRIMARY KEY COMMENT '学校名称',
            location VARCHAR(50) COMMENT '所在地',
            department VARCHAR(100) COMMENT '主管部门',
            education_level VARCHAR(50) COMMENT '办学层次',
            school_type VARCHAR(100) COMMENT '学校特性',
            satisfaction VARCHAR(20) COMMENT '满意度',
            introduction TEXT COMMENT '学校简介',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_location (location),
            INDEX idx_department (department),
            INDEX idx_education_level (education_level)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高校信息表';
        """
        cursor.execute(create_table_sql)
        print("数据表 schools 创建成功")
        
    except Exception as e:
        print(f"创建数据表时出错: {e}")
    finally:
        cursor.close()
        conn.close()

def import_data():
    """导入CSV数据到数据库"""
    try:
        # 读取CSV文件
        df = pd.read_csv('schools_info.csv', encoding='utf-8-sig')
        
        # 将NaN值转换为None
        df = df.fillna('')  # 将所有NaN值替换为空字符串
        
        # 连接数据库
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # 插入数据
        for _, row in df.iterrows():
            sql = """
            INSERT INTO schools (
                school_name, location, department, education_level,
                school_type, satisfaction, introduction
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                location = VALUES(location),
                department = VALUES(department),
                education_level = VALUES(education_level),
                school_type = VALUES(school_type),
                satisfaction = VALUES(satisfaction),
                introduction = VALUES(introduction)
            """
            values = (
                row['学校名称'] or None,  # 如果是空字符串则转换为None
                row['所在地'] or None,
                row['主管部门'] or None,
                row['办学层次'] or None,
                row['学校特性'] or None,
                row['满意度'] or None,
                row['学校简介'] or None
            )
            cursor.execute(sql, values)
        
        # 提交事务
        conn.commit()
        print(f"成功导入 {len(df)} 条数据到数据库")
        
    except Exception as e:
        print(f"导入数据时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    # 1. 创建数据库
    create_database()
    
    # 2. 创建数据表
    create_table()
    
    # 3. 导入数据
    import_data()

if __name__ == "__main__":
    main() 