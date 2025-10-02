# 学生管理系统

一个基于Python和PyQt5开发的学生管理系统，支持管理员、教师和学生三种角色，实现了用户管理、学生信息管理、课程管理和成绩管理等功能。系统采用客户端-服务器架构，支持多用户同时访问和数据共享。同时提供了Web前端界面，方便用户通过浏览器访问系统。

## 系统架构

- **PyQt5前端**：桌面应用GUI界面
- **Web前端**：HTML/CSS/JavaScript实现的浏览器界面
- **后端**：Python网络服务器
- **数据库**：MySQL
- **通信**：基于Socket的客户端-服务器通信
- **数据备份**：支持Docker环境下的数据库备份和恢复

## 功能特点

### 管理员功能
- 用户管理（查看、添加、删除、修改用户）
- 系统统计信息查看
- 数据库备份与恢复

### 教师功能
- 课程管理
- 成绩录入与管理
- 成绩统计分析

### 学生功能
- 个人信息查看与修改
- 课程表查看
- 成绩查询与GPA计算

## 安装指南

### 1. 安装依赖

```powershell
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置数据库

#### 方式一：使用Docker（推荐）

```powershell
# 启动MySQL容器
docker-compose up -d
```

#### 方式二：使用本地MySQL

- 确保已安装MySQL数据库
- 修改`config/config.py`中的数据库配置

#### 数据库共享配置

系统支持数据库共享，允许团队成员通过网络访问同一数据库。详见`database_sharing_guide.md`文件了解详细配置方法。

### 3. 初始化数据库

```powershell
# 运行初始化脚本
python init_database.py
```

## 使用方法

### 1. 启动服务器

```powershell
# 启动服务器
python main.py --server
```

### 2. 启动客户端

```powershell
# 在另一个终端启动客户端
python main.py
```

### 3. 使用Web前端

```powershell
# 在项目根目录启动HTTP服务器
python -m http.server 8000
```

然后在浏览器中访问：http://localhost:8000/frontend/index.html

### 4. 登录系统

使用以下测试账号登录：
- **管理员**：用户名`admin`，密码`admin123`
- **教师**：用户名`teacher1`或`teacher2`，密码`teacher123`
- **学生**：用户名`student1`、`student2`或`student3`，密码`student123`

## 项目结构

```
student_management_system/
├── .gitignore         # Git忽略文件规则
├── README.md          # 项目说明文档
├── backups/           # 数据库备份文件目录
├── cache/             # 缓存文件目录
├── config/            # 配置文件
│   └── config.py      # 系统配置（数据库连接等）
├── database/          # 数据库管理模块
│   └── db_manager.py  # 数据库操作类
├── database_sharing_guide.md  # 数据库共享配置指南
├── docker-compose.yml # Docker配置文件
├── frontend/          # Web前端文件
│   ├── admin_dashboard.html  # 管理员Web界面
│   ├── admin_dashboard.js    # 管理员Web功能脚本
│   ├── dashboard.js   # 通用仪表盘脚本
│   ├── index.html     # Web登录页面
│   ├── script.js      # 通用Web脚本
│   ├── student_dashboard.html  # 学生Web界面
│   ├── styles.css     # Web样式表
│   ├── teacher_dashboard.html  # 教师Web界面
│   └── teacher_dashboard.js    # 教师Web功能脚本
├── init_database.py   # 数据库初始化脚本
├── main.py            # 主程序入口
├── models/            # 数据模型和业务逻辑
│   ├── courses.py     # 课程相关模型
│   ├── enrollment.py  # 选课相关模型
│   ├── scores.py      # 成绩相关模型
│   ├── student.py     # 学生相关模型
│   ├── teacher.py     # 教师相关模型
│   └── user.py        # 用户相关模型
├── network/           # 网络通信模块
│   ├── client.py      # 客户端通信
│   └── server.py      # 服务器通信
├── requirements.txt   # 项目依赖
├── todo_list.md       # 待办事项列表
├── ui/                # 用户界面模块
│   ├── admin_dashboard.py   # 管理员界面
│   ├── login_window.py      # 登录界面
│   ├── main_window.py       # 主窗口
│   ├── register_dialog.py   # 注册对话框
│   ├── student_dashboard.py # 学生界面
│   ├── teacher_dashboard.py # 教师界面
│   └── user_profile.py      # 用户信息界面
├── use_guide.md       # 使用指南
└── utils/             # 工具函数
    ├── __init__.py
    ├── common_utils.py      # 通用工具函数
    └── data_visualization.py # 数据可视化工具
```

## 开发说明

- 系统使用PyQt5开发GUI界面
- 采用客户端-服务器架构，通过Socket进行通信
- 数据持久化存储在MySQL数据库中
- 支持三种角色的不同权限和功能

## 注意事项

1. 确保在启动客户端前先启动服务器
2. 首次使用前必须运行`init_database.py`初始化数据库
3. 使用Docker方式时，确保Docker服务已启动
4. 如需修改数据库配置，请编辑`config/config.py`文件
5. 系统日志会输出到控制台，便于排查问题
6. 数据库备份文件默认保存在`backups/`目录下

## 更新日志

### 最近更新
- 开发Web前端界面，包含管理员、教师和学生三种角色的仪表盘
- 实现Web前端的用户登录、角色验证和页面跳转功能
- 优化Web界面的标签页导航，统一导航样式
- 修复JavaScript变量重复声明错误
- 解决登录后跳回登录界面的问题
- 添加Docker环境下的数据库备份和恢复功能支持
- 修复登录界面无响应问题，使用线程处理登录请求
- 添加Docker支持，便于快速部署开发环境
- 完善数据库初始化脚本，确保测试数据正确插入
- 优化错误处理和日志记录机制
- 创建共享数据库用户，支持多用户协作开发
- 项目已上传至GitHub仓库，方便团队协作和版本管理
- 优化README.md文档结构，添加更详细的项目结构说明
- 新增数据库共享配置指南文件

## 联系方式

如有任何问题或建议，请联系项目维护人员。