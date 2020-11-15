from apps import create_app  # 创建app
from flask_script import Manager  # 给app套壳: 执行类似命令python app.py runserver。。。
from flask_migrate import Migrate, MigrateCommand  # 数据库命令
from exts import db
from apps.main_app.models import *


app = create_app()
manager = Manager(app=app)

# 数据库迁移命令等
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)  # 数据库迁移的命令

if __name__ == '__main__':
    manager.run()  # 这是开发环境使用的
    # app.run(debug=False)  # 上线部署后使用python app.py 启动