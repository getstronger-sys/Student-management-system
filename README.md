# 学生管理系统

一个基于Python和PyQt5开发的学生管理系统，支持管理员、教师和学生三种角色，实现了用户管理、学生信息管理、课程管理和成绩管理等功能。

## 系统架构

- **前端**：PyQt5 GUI界面
- **后端**：Python网络服务器
- **数据库**：MySQL
- **通信**：基于Socket的客户端-服务器通信

## 功能特点

### 管理员功能
- 用户管理（查看、添加、删除、修改用户）
- 系统统计信息查看

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

### 3. 登录系统

使用以下测试账号登录：
- **管理员**：用户名`admin`，密码`admin123`
- **教师**：用户名`teacher1`或`teacher2`，密码`teacher123`
- **学生**：用户名`student1`、`student2`或`student3`，密码`student123`

## 项目结构

```
student_management_system/
├── config/            # 配置文件
├── database/          # 数据库管理模块
├── models/            # 数据模型和业务逻辑
├── network/           # 网络通信模块
├── ui/                # 用户界面模块
├── utils/             # 工具函数
├── docker-compose.yml # Docker配置文件
├── init_database.py   # 数据库初始化脚本
├── main.py            # 主程序入口
├── requirements.txt   # 项目依赖
└── README.md          # 项目说明文档
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

## 更新日志

### 最近更新
- 修复登录界面无响应问题，使用线程处理登录请求
- 添加Docker支持，便于快速部署开发环境
- 完善数据库初始化脚本，确保测试数据正确插入
- 优化错误处理和日志记录机制

## 联系方式

如有任何问题或建议，请联系项目维护人员。