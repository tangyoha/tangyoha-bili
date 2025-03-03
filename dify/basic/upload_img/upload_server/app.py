# /app.py

import os
import hashlib
import uuid
import duckdb
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置文件上传路径
UPLOAD_FOLDER = 'uploads'
IMG_FOLDER = 'img'
DOC_FOLDER = 'doc'

for folder in [IMG_FOLDER, DOC_FOLDER]:
    full_path = os.path.join(UPLOAD_FOLDER, folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

API_HOST = os.environ.get('API_HOST', 'localhost')
API_PORT = int(os.environ.get('API_PORT', 8089))

# 配置DuckDB数据库
db_path = 'file_mapping.db'
conn = duckdb.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS file_mappings (
        file_hash VARCHAR PRIMARY KEY,
        file_uuid VARCHAR,
        file_type VARCHAR,
        relative_path VARCHAR
    )
''')

def generate_unique_id():
    return uuid.uuid4().hex[:8]

def get_file_hash(file):
    file.seek(0)
    file_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    return file_hash

def is_image(filename):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return os.path.splitext(filename)[1].lower() in image_extensions

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')
    file_urls = []

    for file in files:
        file_hash = get_file_hash(file)
        original_filename = secure_filename(file.filename)
        file_ext = os.path.splitext(original_filename)[1]

        # 检查文件是否已经存在于数据库中
        query = "SELECT file_uuid, file_type, relative_path FROM file_mappings WHERE file_hash = ?"
        cursor = conn.cursor()
        result = cursor.execute(query, (file_hash,)).fetchone()

        if result:
            # 文件已经存在，使用现有的UUID和类型
            file_id, file_type, relative_path = result
        else:
            # 生成唯一的文件id并存储到数据库
            file_id = generate_unique_id()
            file_type = 'img' if is_image(original_filename) else 'doc'
            folder = IMG_FOLDER if file_type == 'img' else DOC_FOLDER
            
            # 使用原始文件名和UUID创建新的文件名
            new_filename = f"{file_id}_{original_filename}"
            relative_path = os.path.join(folder, new_filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
            
            file.save(full_path)
            cursor.execute("INSERT INTO file_mappings (file_hash, file_uuid, file_type, relative_path) VALUES (?, ?, ?, ?)", 
                           (file_hash, file_id, file_type, relative_path))

        file_url = f"https://{API_HOST}:{API_PORT}/{file_type}/{file_id}"
        file_urls.append(file_url)

    return jsonify(file_urls), 200

def get_file_path(file_id, file_type):
    query = "SELECT relative_path FROM file_mappings WHERE file_uuid = ? AND file_type = ?"
    cursor = conn.cursor()
    result = cursor.execute(query, (file_id, file_type)).fetchone()
    return result[0] if result else None

@app.route('/img/<file_id>', methods=['GET'])
@app.route('/doc/<file_id>', methods=['GET'])
def get_file(file_id):
    file_type = 'img' if request.path.startswith('/img/') else 'doc'
    relative_path = get_file_path(file_id, file_type)

    if relative_path:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
        if os.path.exists(full_path):
            return send_file(full_path)

    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=8089, ssl_context='adhoc')
    app.run(host="0.0.0.0", port=8089)