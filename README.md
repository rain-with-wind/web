# 学生信息管理系统

基于 **openGauss/GaussDB + FastAPI + Docker** 的前后端分离 Web 应用，武汉大学《大数据与云计算技术》课程期末实验。

## 技术栈

| 层级 | 技术 |
|------|------|
| 数据库 | PostgreSQL 15 / openGauss 5.0（协议兼容） |
| 后端 | Python + FastAPI + psycopg2 |
| 前端 | 原生 HTML/CSS/JS（SPA 单页应用） |
| Web 服务器 | Nginx (Alpine) |
| 容器化 | Docker + Docker Compose |

## 项目结构

```
web/
├── backend/
│   ├── main.py              # FastAPI 入口，6 个 RESTful 路由
│   ├── database.py          # psycopg2 连接池管理
│   ├── models.py            # Pydantic 数据校验模型
│   ├── requirements.txt     # Python 依赖
│   └── Dockerfile           # 后端镜像构建文件
├── frontend/
│   ├── index.html           # 主页面
│   ├── style.css            # 样式
│   ├── app.js               # 前端交互逻辑（CRUD + 搜索 + 分页）
│   └── Dockerfile           # 前端镜像构建文件
├── sql/
│   └── init.sql             # 数据库建表 + 示例数据
└── docker-compose.yml       # 三服务统一编排
```

## 本地部署（Docker）

**前置条件**：安装 Docker Desktop

```bash
# 1. 启动 Docker Desktop

# 2. 进入项目目录
cd web

# 3. 一键启动
docker compose up -d

# 4. 验证
docker compose ps
```

浏览器访问：
- 前端页面：http://localhost:3000
- 后端 API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

## 镜像部署（只发镜像，离线可用）

**导出：**

```bash
# 1. 构建镜像
docker compose build

# 2. 导出镜像包
docker save postgres:15-alpine web-backend web-frontend -o student-system.tar

# 3. 把两个文件给对方
#    student-system.tar             (镜像包)
#    docker-compose.deploy.yml     (编排文件，不含 build 路径)
```

**导入：**

```bash
# 1. 导入镜像
docker load -i student-system.tar

# 2. 启动（注意用 deploy 版文件）
docker compose -f docker-compose.deploy.yml up -d
```

对方不需要装 Python、不需要拉镜像、不需要任何源码——有 Docker 就行。

## 华为云部署

适用于华为云开发者空间（容器版）或任意云服务器：

```bash
# 1. 安装 PostgreSQL
dnf install -y postgresql-server postgresql
su - postgres -c "/usr/bin/pg_ctl initdb -D /var/lib/pgsql/data"
su - postgres -c "/usr/bin/pg_ctl start -D /var/lib/pgsql/data"

# 2. 创建用户和数据库
su - postgres -c "createuser gaussuser"
su - postgres -c "psql -c \"ALTER USER gaussuser WITH PASSWORD 'GaussDB@123';\""
su - postgres -c "createdb studentdb -O gaussuser"
PGPASSWORD=GaussDB@123 psql -h 127.0.0.1 -U gaussuser -d studentdb -f sql/init.sql

# 3. 安装依赖
pip3 install psycopg2-binary fastapi uvicorn pydantic

# 4. 启动后端
cd backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &

# 5. 启动前端
cd ../frontend
nohup python3 -m http.server 3000 > /var/log/frontend.log 2>&1 &
```

通过 VS Code 端口转发 3000 和 8000 后，本地浏览器即可访问。

## API 接口

| 方法 | 路由 | 功能 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/students` | 查询学生列表（支持 keyword/page/page_size） |
| GET | `/api/students/{id}` | 查询单个学生 |
| POST | `/api/students` | 新增学生 |
| PUT | `/api/students/{id}` | 更新学生 |
| DELETE | `/api/students/{id}` | 删除学生 |

## 常用命令

```bash
# === 启动 ===
docker compose up -d              # 首次启动（构建镜像 + 创建容器 + 启动）
docker compose start              # 再次启动已存在的容器（不会重建）

# === 停止 ===
docker compose stop               # 停止容器（容器还在，数据还在）
docker compose down               # 停止并删除容器（数据还在，volume 保留）

# === 重启容器（不在 compose 管理下的独立容器） ===
docker start gaussdb student-backend student-frontend

# === 查看 ===
docker compose ps                 # 查看运行状态
docker ps -a                      # 查看所有容器（含已停止的）
docker compose logs backend       # 查看后端日志

# === 更新 ===
docker compose up -d --build      # 改代码后重新构建并启动

# === 清理僵尸容器 ===
docker rm -f gaussdb student-backend student-frontend   # 删掉旧容器
docker compose up -d                                      # 重建

# === 数据库 ===
docker exec -it gaussdb psql -U gaussuser -d studentdb -c "SELECT * FROM students;"
```
