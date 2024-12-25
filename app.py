from flask import Flask, render_template, request
import pymysql
from config import MYSQL_CONFIG

app = Flask(__name__)

def get_db():
    """获取数据库连接"""
    return pymysql.connect(**MYSQL_CONFIG)

@app.route('/')
def index():
    """首页 - 显示学校列表"""
    # 获取查询参数
    location = request.args.get('location', '')
    department = request.args.get('department', '')
    keyword = request.args.get('keyword', '')  # 获取搜索关键词
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取筛选条件
        cursor.execute("SELECT DISTINCT location FROM schools ORDER BY location")
        locations = [row['location'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT department FROM schools ORDER BY department")
        departments = [row['department'] for row in cursor.fetchall()]
        
        # 构建查询SQL
        sql = "SELECT * FROM schools WHERE 1=1"
        params = []
        
        if keyword:  # 添加关键词搜索条件
            sql += " AND school_name LIKE %s"
            params.append(f"%{keyword}%")
        
        if location:
            sql += " AND location = %s"
            params.append(location)
        if department:
            sql += " AND department = %s"
            params.append(department)
            
        sql += " ORDER BY school_name"
        
        # 获取学校列表
        cursor.execute(sql, params)
        schools = cursor.fetchall()
        
        return render_template('index.html', 
                             schools=schools,
                             locations=locations,
                             departments=departments,
                             selected_location=location,
                             selected_department=department,
                             selected_keyword=keyword)  # 传递关键词到模板
    finally:
        cursor.close()
        conn.close()

@app.route('/school/<school_name>')
def school_detail(school_name):
    """学校详情页"""
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取学校详细信息
        cursor.execute("SELECT * FROM schools WHERE school_name = %s", (school_name,))
        school = cursor.fetchone()
        if school:
            return render_template('detail.html', school=school)
        return "学校不存在", 404
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 