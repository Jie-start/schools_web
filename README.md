# 高校信息库网站

## 1、修改数据库配置信息

打开 `config.py`

```python
# MySQL数据库配置
MYSQL_CONFIG = {
    'host': 'localhost',      # 数据库主机地址
    'port': 3306,            # 数据库端口
    'user': 'root',          # 数据库用户名
    'password': 'your_passward',    # 数据库密码
    'database': 'schools',   # 数据库名称
    'charset': 'utf8mb4'     # 字符集
}
```

将 `your_password` 修改成你的数据库密码

## 2、导入数据

```bash
python save_to_mysql.py
```

## 3、安装所需要的第三方库

```bash
pip install -r requirements.txt
```

## 4、运行flask

```bash
python app.py
```

访问 http://localhost:5000