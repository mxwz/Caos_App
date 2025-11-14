import os
import shutil
import signal
import sys
from app import create_app
# import multiprocessing

app = create_app()

def save_data(signum, frame):
    print("程序正在关闭，执行删除操作...")
    file_path = app.config['CAPTCHA_PATH']
    print(f"文件路径: {file_path}")
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        print("删除成功")
    else:
        print("无此文件夹")
    try:
        os.makedirs(file_path, exist_ok=True)
        print('已经重新创建')
    except Exception as e:
        print(f"创建文件夹失败: {e}")
    sys.exit(0)

# signal.signal(signal.SIGINT, save_data)  # 捕获 Ctrl+C
# signal.signal(signal.SIGTERM, save_data)  # 捕获终止信号

def run_flask():
    signal.signal(signal.SIGINT, save_data)  # 捕获 Ctrl+C
    signal.signal(signal.SIGTERM, save_data)  # 捕获终止信号
    app.run(debug=True, threaded=True, port=5000)


if '__main__' == __name__:
    signal.signal(signal.SIGINT, save_data)  # 捕获 Ctrl+C
    signal.signal(signal.SIGTERM, save_data)  # 捕获终止信号

    context = (r'C:\Users\yang\localhost.pem', r'C:\Users\yang\localhost-key.pem')
    # app.run(debug=True, host='0.0.0.0', port=5034, threaded=True, ssl_context='adhoc')
    app.run(debug=True, ssl_context=context, threaded=True, port=5036, host='0.0.0.0')
    # app.run(debug=True, threaded=True, port=5000)