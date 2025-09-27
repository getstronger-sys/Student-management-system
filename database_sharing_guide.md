# 数据库共享配置指南

本指南将帮助你配置系统，让其他同学能够连接到你的数据库，一起添加和管理数据。

## 一、服务器端（你的电脑）配置

### 步骤1：确保Docker数据库已正确配置

当前的<mcfile name="docker-compose.yml" path="e:\OneDrive\Desktop\大三上\python\大作业\student_management_system\docker-compose.yml"></mcfile>配置已经正确设置了端口映射，允许外部访问：

```yaml
ports:
  - "3306:3306"
```

### 步骤2：启动Docker数据库

在项目根目录下执行以下命令：

```powershell
# 进入项目目录
cd e:\OneDrive\Desktop\大三上\python\大作业\student_management_system

# 启动MySQL容器
docker-compose up -d

# 查看容器运行状态
docker-compose ps
```

### 步骤3：为远程访问配置MySQL用户

进入Docker容器，创建一个允许远程连接的用户：

```powershell
# 进入MySQL容器
docker exec -it student_management_mysql mysql -uroot -p123456

# 在MySQL命令行中执行以下SQL语句

# 创建一个新用户，允许从任何IP地址连接
CREATE USER 'shared_user'@'%' IDENTIFIED BY 'shared_password';

# 授予该用户对student_management数据库的全部权限
GRANT ALL PRIVILEGES ON student_management.* TO 'shared_user'@'%';

# 刷新权限
FLUSH PRIVILEGES;

# 退出MySQL命令行
exit
```

### 步骤4：修改系统配置以使用新用户

更新<mcfile name="config.py" path="e:\OneDrive\Desktop\大三上\python\大作业\student_management_system\config\config.py"></mcfile>文件中的数据库配置：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'shared_user',  # 修改为刚才创建的用户
    'password': 'shared_password',  # 修改为设置的密码
    'database': 'student_management',
    'port': 3306
}
```

### 步骤5：初始化数据库（如果你还没有数据）

```powershell
python init_database.py
```

这将创建所有必要的表并插入测试数据。

### 步骤6：启动服务器

```powershell
python main.py --server
```

服务器将使用你的配置连接到Docker数据库，并监听所有IP地址的8888端口。

## 二、客户端（其他同学的电脑）配置

### 步骤1：获取项目代码

确保其他同学拥有与你相同版本的项目代码。

### 步骤2：修改客户端连接配置

他们需要修改<mcfile name="client.py" path="e:\OneDrive\Desktop\大三上\python\大作业\student_management_system\network\client.py"></mcfile>中的连接地址为你的校园网IP：

```python
# 修改为服务器的IP地址
self.host = '10.29.108.168'  # 替换为你的实际校园网IP
```

### 步骤3：启动客户端

```powershell
python main.py
```

**注意**：不需要使用`--server`参数，只启动客户端模式。

## 三、验证连接

1. 其他同学启动客户端后，尝试登录系统
2. 你可以在服务器端看到连接日志
3. 尝试添加或修改数据，确认所有同学都能看到相同的数据

## 四、常见问题解决

### 1. 连接被拒绝

- 确保你的防火墙允许8888端口的入站连接
- 确认你的校园网IP地址正确
- 检查Docker容器是否正在运行：`docker-compose ps`

### 2. 权限问题

- 确认在MySQL中正确创建了允许远程连接的用户
- 验证用户权限：在MySQL命令行中执行`SHOW GRANTS FOR 'shared_user'@'%';`

### 3. 数据不同步

- 确保所有同学都连接到同一个服务器
- 检查客户端配置中的IP地址是否正确

## 五、安全建议

1. **不要在生产环境使用此配置**：这是为开发环境设计的配置
2. **定期备份数据**：使用`docker exec student_management_mysql mysqldump -u root -p123456 student_management > backup.sql`命令备份数据
3. **使用后更改密码**：项目完成后，修改MySQL用户的密码

通过以上配置，你和组内其他同学就能共享同一个数据库，实时协作添加和管理数据。