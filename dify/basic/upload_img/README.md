# Markdown Image Manager (Markdown 图片管理工具)

[English](#english) | [中文](#chinese)

<a name="english"></a>
## English

### Introduction
This tool helps manage images in Markdown files by providing two main functions:
1. Upload local images to a remote server and update markdown links (POST mode)
2. Download remote images to local storage and update markdown links (PULL mode)

### System Requirements
- Python 3.9+
- Docker
- Docker Compose

### Installation

#### 1. Server Setup

1. Clone the repository and navigate to the upload_server directory:
```bash
cd upload_server
```

2. Build the Docker image:
```bash
# If you need to use a proxy
./build.sh
# Or without proxy
docker build -t flask-file-upload-app .
```

3. Start the server using Docker Compose:
```bash
docker-compose up -d
```

The server will be running on `http://localhost:8089`.

#### 2. Client Setup

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

2. Install the required Python packages:
```bash
pip3 install -r requirements.txt
```

### Usage

#### Client Tool (down_load_md.py)

First, make sure your virtual environment is activated. Then:

The client tool supports two modes of operation:

1. POST mode - Upload local images to server:
```bash
# Process a single file
python3 down_load_md.py -f path/to/your.md -m post -s http://your-server:8089/upload

# Process all markdown files in a directory
python3 down_load_md.py -d path/to/directory -m post -s http://your-server:8089/upload
```

2. PULL mode - Download remote images to local:
```bash
# Process a single file
python3 down_load_md.py -f path/to/your.md -m pull

# Process all markdown files in a directory
python3 down_load_md.py -d path/to/directory -m pull
```

Parameters:
- `-f, --file`: Path to a single Markdown file
- `-d, --directory`: Directory containing Markdown files
- `-m, --mode`: Operation mode ('post' or 'pull')
- `-s, --server`: URL of the upload server (default: http://localhost:8089/upload)

### Server API Endpoints

- `POST /upload`: Upload files
- `GET /img/<file_id>`: Retrieve uploaded images
- `GET /doc/<file_id>`: Retrieve uploaded documents

---

<a name="chinese"></a>
## 中文

### 简介
这是一个 Markdown 图片管理工具，提供两个主要功能：
1. 将本地图片上传至远程服务器并更新 Markdown 链接（POST 模式）
2. 将远程图片下载到本地并更新 Markdown 链接（PULL 模式）

### 系统要求
- Python 3.9+
- Docker
- Docker Compose

### 安装部署

#### 1. 服务器部署

1. 克隆仓库并进入 upload_server 目录：
```bash
cd upload_server
```

2. 构建 Docker 镜像：
```bash
# 如果需要使用代理
./build.sh
# 或者不使用代理
docker build -t flask-file-upload-app .
```

3. 使用 Docker Compose 启动服务：
```bash
docker-compose up -d
```

服务器将在 `http://localhost:8089` 运行。

#### 2. 客户端安装

1. 创建并激活虚拟环境：
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows系统
venv\Scripts\activate
# Unix或MacOS系统
source venv/bin/activate
```

2. 安装所需的 Python 包：
```bash
pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple/
```

### 使用说明

#### 客户端工具 (down_load_md.py)

首先确保您的虚拟环境已经激活，然后：

客户端工具支持两种运行模式：

1. POST 模式 - 上传本地图片到服务器：
```bash
# 处理单个文件
python3 down_load_md.py -f 文件路径/your.md -m post -s http://your-server:8089/upload

# 处理目录下所有 markdown 文件
python3 down_load_md.py -d 目录路径 -m post -s http://your-server:8089/upload
```

2. PULL 模式 - 下载远程图片到本地：
```bash
# 处理单个文件
python3 down_load_md.py -f 文件路径/your.md -m pull

# 处理目录下所有 markdown 文件
python3 down_load_md.py -d 目录路径 -m pull
```

参数说明：
- `-f, --file`: 单个 Markdown 文件的路径
- `-d, --directory`: 包含 Markdown 文件的目录路径
- `-m, --mode`: 运行模式 ('post' 或 'pull')
- `-s, --server`: 上传服务器的 URL (默认: http://localhost:8089/upload)

### 服务器 API 接口

- `POST /upload`: 上传文件
- `GET /img/<file_id>`: 获取已上传的图片
- `GET /doc/<file_id>`: 获取已上传的文档

