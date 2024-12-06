# 文件服务器

基于 Flask 构建的简单文件服务器。

## 系统要求

- Python 3.8 或更高版本（小于 3.14）
- PDM (Python 包管理器)

## 安装步骤

1. 如果尚未安装 PDM，请先安装：
```bash
pip install pdm
```

2. 在 Windows 系统中，可以使用以下方式运行 PDM：
```bash
python -m pdm
```

3. 安装项目依赖：
```bash
python -m pdm install
```

如果需要开发环境，请安装开发依赖：
```bash
python -m pdm install -G dev
```

## 命令行参数

程序支持以下命令行参数：

- `--dir` 或 `-d`：指定要服务的根目录（默认：当前工作目录）
  ```bash
  # 示例：指定 D:\files 作为根目录
  python file_server.py --dir D:\files
  
  # 或使用短参数
  python file_server.py -d D:\files
  ```

服务器配置：
- 默认监听所有网络接口（0.0.0.0）
- 端口：5000
- 线程数：16
- 超时时间：300秒

## 使用说明

1. 启动开发服务器：
```bash
# Windows
python -m pdm run dev

# Linux/Mac
pdm run dev
```

2. 访问服务器：
   - 打开浏览器访问 http://localhost:5000
   - 或在局域网内通过 http://<服务器IP>:5000 访问

3. 文件操作：
   - 点击文件夹进行导航
   - 点击文件名下载文件
   - 支持文件预览（取决于浏览器支持的文件类型）

## 开发指南

1. 代码格式化：
```bash
python -m pdm run format
```

2. 运行测试：
```bash
python -m pdm run test
```

3. 构建可执行文件：
```bash
python -m pdm run build
```

## 注意事项

- 请确保服务器端口 5000 未被其他程序占用
- 建议在生产环境中配置适当的访问控制和安全措施
- 大文件传输可能需要较长时间，请耐心等待

## 访问

启动服务器后，可以通过以下地址访问：
- 本地：http://localhost:5000
- 网络：http://[你的 IP 地址]:5000
