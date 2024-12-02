from flask import Flask, send_file, abort, request, render_template, jsonify
import os
import mimetypes
import zipfile
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from functools import lru_cache
import argparse
import sys

# 配置日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__, static_url_path='/static', static_folder='static')

# 存储根目录的全局变量
ROOT_DIR = None

@app.route('/favicon.ico')
def favicon():
    """处理favicon.ico请求"""
    return '', 204  # 返回空内容，状态码204

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def create_zip_file(directory):
    """创建目录的zip文件"""
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, directory)
                zf.write(file_path, arc_name)
    memory_file.seek(0)
    return memory_file

def normalize_path(path):
    """规范化路径，确保使用/作为分隔符且以/开头"""
    # 使用 pathlib 处理路径，自动处理分隔符
    normalized = str(Path(path)).replace('\\', '/')
    # 去除开头的斜杠
    normalized = normalized.lstrip('/')
    return normalized

def get_safe_path(path):
    """获取安全的绝对路径，确保在ROOT_DIR范围内"""
    # 规范化并移除开头的斜杠
    clean_path = normalize_path(path)
    # 使用 pathlib 构建绝对路径
    abs_path = str(Path(ROOT_DIR).joinpath(clean_path).resolve())
    # 确保路径在ROOT_DIR内
    if not abs_path.startswith(ROOT_DIR):
        return None
    return abs_path

@lru_cache(maxsize=100)
def get_directory_size(path):
    """递归计算目录大小（带缓存）"""
    total_size = 0
    try:
        # 使用os.scandir代替os.walk来提高性能
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total_size += get_directory_size(entry.path)
                except (OSError, IOError):
                    continue
    except Exception as e:
        logging.error(f"Error calculating directory size for {path}: {str(e)}")
        return 0
    return total_size

def get_directory_info(target_path, base_dir):
    """获取目录信息"""
    files = []
    for item in os.listdir(target_path):
        item_path = os.path.join(target_path, item)
        rel_item_path = os.path.relpath(item_path, base_dir)
        is_dir = os.path.isdir(item_path)
        
        stat = os.stat(item_path)
        mime_type = None if is_dir else mimetypes.guess_type(item)[0]
        
        # 对文件直接计算大小，目录则显示占位符
        size = stat.st_size if not is_dir else None
        
        # 修复：使用当前路径和item名称拼接生成正确的href路径
        current_path = request.path.rstrip('/')
        href_path = f"{current_path}/{item}" if current_path != '/' else f"/{item}"
        
        files.append({
            'name': item,
            'path': href_path,  # 使用正确的href路径
            'type': 'directory' if is_dir else 'file',
            'size': format_size(size) if size is not None else '----',
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'mime_type': mime_type
        })

    # 排序：目录在前，文件在后
    files.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
    return files

def get_breadcrumbs(target_path, base_dir):
    """获取面包屑导航信息"""
    # 使用 pathlib 处理相对路径
    rel_path = str(Path(target_path).relative_to(Path(base_dir)))
    breadcrumbs = []
    current = ''
    
    # 如果不是根目录，添加面包屑
    if rel_path != '.':
        # 使用 / 分割路径，确保跨平台兼容性
        for part in rel_path.replace('\\', '/').split('/'):
            current = str(Path(current).joinpath(part))
            breadcrumbs.append({
                'name': part,
                'path': '/' + normalize_path(current)  # 添加前导斜杠，确保是绝对路径
            })
    
    return [{'name': 'Home', 'path': '/'}] + breadcrumbs

@app.route('/_api_/directory-size/', defaults={'dir_path': ''})
@app.route('/_api_/directory-size/<path:dir_path>')
def get_dir_size(dir_path):
    """异步获取目录大小的API"""
    try:
        # 获取安全的目标路径
        target_path = get_safe_path(dir_path)
        if target_path is None:
            logging.warning(f"Attempted to access directory outside root: {dir_path}")
            abort(403)
            
        # 检查路径是否存在且是目录
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            logging.warning(f"Directory not found: {target_path}")
            abort(404)
            
        # 计算目录大小
        total_size = get_directory_size(target_path)
        
        # 返回格式化的大小
        return jsonify({
            'size': format_size(total_size)
        })
        
    except Exception as e:
        logging.error(f"Error calculating directory size: {str(e)}")
        return jsonify({
            'error': 'Failed to calculate directory size'
        }), 500

@app.route('/', defaults={'file_path': ''})
@app.route('/<path:file_path>')
def serve_file(file_path):
    """统一的文件服务处理函数"""
    try:
        # 获取安全的目标路径
        target_path = get_safe_path(file_path)
        if target_path is None:
            abort(403)

        if not os.path.exists(target_path):
            abort(404)

        # 如果是目录
        if os.path.isdir(target_path):
            # 检查是否需要下载
            download = request.args.get('download', '').lower() == 'true'
            
            # 如果请求下载，返回zip文件
            if download:
                memory_file = create_zip_file(target_path)
                return send_file(
                    memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"{os.path.basename(target_path)}.zip"
                )
            
            # 否则渲染目录内容
            files = get_directory_info(target_path, ROOT_DIR)
            breadcrumbs = get_breadcrumbs(target_path, ROOT_DIR)
            return render_template(
                'index.html',
                files=files,
                breadcrumbs=breadcrumbs,
                current_path=normalize_path(file_path)
            )

        # 如果是文件，直接返回文件内容
        else:
            download = request.args.get('download', '').lower() == 'true'
            return send_file(
                target_path,
                as_attachment=download,
                download_name=os.path.basename(target_path)
            )

    except Exception as e:
        logging.error(f"Error serving file: {str(e)}")
        abort(500)

if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='File Server with custom root directory')
    parser.add_argument('--dir', '-d', type=str, default=os.getcwd(),
                      help='Root directory to serve (default: current working directory)')
    
    args = parser.parse_args()
    
    # 确保路径是绝对路径
    ROOT_DIR = os.path.abspath(args.dir)
    
    if not os.path.exists(ROOT_DIR):
        print(f"Error: Directory '{ROOT_DIR}' does not exist!")
        sys.exit(1)
    
    if not os.path.isdir(ROOT_DIR):
        print(f"Error: '{ROOT_DIR}' is not a directory!")
        sys.exit(1)
    
    print(f"File Server started at http://127.0.0.1:5000")
    print(f"Serving files from: {ROOT_DIR}")
    
    # 使用 waitress 作为生产级服务器
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000,
          threads=16,  # 增加线程数
          channel_timeout=300,  # 增加超时时间
          ident='FileServer')  # 设置服务器标识
