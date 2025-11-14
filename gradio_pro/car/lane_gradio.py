import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import webbrowser
import zipfile
from datetime import datetime

import appbuilder
import pyttsx3
import requests

import requests as rq
import cv2
import tensorflow as tf
import gradio as gr
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'content-type': 'text/html; charset=utf-8'}

css = """
.gradio-container {
  background-image: url('https://npimg.hellouikit.com/e8/06/e80666f163bd4b151ebc02bdc5c198bf?imageView2/2/w/1000'); 
  border: 1px solid #000000;
  background-size: cover; /* 添加这行 */  
  border-radius: 10px;
  padding: 20px;
  overflow: hidden; /* 防止图片溢出容器 */  
}

.gradio-header {
  color: #000000;
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

.gradio-input {
  width: 100%;
  height: 40px;
  padding: 10px;
  border: 1px solid #000000;
  border-radius: 5px;
}

.gradio-output {
  width: 100%;
  height: 40px;
  padding: 10px;
  border: 1px solid #000000;
  border-radius: 5px;
}

"""


def get_external_ip():
    response = requests.get('https://cn.apihz.cn/api/ip/ipbaidu.php?id=10000996&key=265d85ba1e64b2bde1ba51984bb329d1')

    data = response.json()
    return data  # 返回解析后的字典


file_name = str(datetime.now().timestamp())
file_mkdir = str(datetime.now().strftime("%Y-%m-%d"))

if not os.path.exists(f"./log/{file_mkdir}"):
    os.makedirs(f"./log/{file_mkdir}")

# 创建一个logger对象
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s => %(funcName)s] [%(levelname)s] : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个FileHandler，用于输出到日志文件
file_handler = logging.FileHandler(f'./log/{file_mkdir}/{file_name}.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 设置日志记录的格式
formatter = logging.Formatter('[%(asctime)s] [%(name)s => %(funcName)s] [%(levelname)s] : %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# 将Handler添加到Logger对象中
logger.addHandler(file_handler)


def Json_Data(json_data):
    # 解析JSON字符串
    # data = json.loads(json_data)
    data = json_data

    # 初始化一个空列表来存储所有坐标点
    all_coords = []

    # 直接访问第一个路径
    first_path = data['route']['paths'][0]

    # 遍历第一个路径的步骤，再遍历每个步骤的tmcs
    for step in first_path['steps']:
        for tmc in step.get('tmcs', []):
            # 假设每个tmcs对象都有一个polyline字段
            polyline = tmc.get('polyline', '')
            # 分割polyline字符串，每个坐标点由分号分隔
            coords = polyline.split(';')
            # 将坐标点添加到all_coords列表中
            all_coords.extend(coords)

        # 现在all_coords包含了所有坐标点，每个坐标点是一个包含经度和纬度的字符串

    # 如果需要将这些坐标点进一步分割成包含[经度, 纬度]的小列表，可以这样做：
    coords_list_of_lists = [coord.split(',') for coord in all_coords]

    # 输出结果查看
    # 使用列表推导式来转换所有元素为float
    converted_nested_list = [[float(j) for j in i] for i in coords_list_of_lists]

    print(converted_nested_list)
    return converted_nested_list



def speak_response(response):
    engine = pyttsx3.init()
    # rate = engine.getProperty('rate')  # getting details of current speaking rate
    # print(rate)  # printing current voice rate
    engine.setProperty('rate', 175)  # setting up new voice rate
    engine.say(response)
    engine.runAndWait()

    # saved mp3
    # engine.save_to_file('Hello World', 'test.mp3')
    # engine.runAndWait()


def lane_correct_model(input_shape):
    """
    LaneConrect模型结构

    :param input_shape: 输入维度
    :return: 模型结构model
    """
    inputs = tf.keras.layers.Input(input_shape)

    # 编码器
    c1 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    c1 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c1)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)

    c2 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    c2 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c2)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)

    # 解码器
    u3 = tf.keras.layers.Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same')(p2)
    # 添加上采样层以匹配c1的尺寸
    u3 = tf.keras.layers.Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same', activation='relu')(u3)
    u3 = tf.keras.layers.concatenate([u3, c1])
    # u3 = tf.keras.layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(p2)
    # u3 = tf.keras.layers.concatenate([u3, c1])
    c3 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u3)
    c3 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c3)

    outputs = tf.keras.layers.Conv2D(1, (1, 1), activation='sigmoid')(c3)

    model = tf.keras.models.Model(inputs=[inputs], outputs=[outputs])
    return model


# 加载模型时提供CustomAccuracy类的定义
# model = lane_correct_model((128, 128, 3))
def load_model():
    """
    加载模型，用于模型缓存，加载加速

    :return: 模型结构mode
    """
    model = tf.keras.models.load_model(r'unet_lane_detection.h5')
    return model


# 预处理测试代码
def enhance_contrast(image):
    """
    模型图片预测-预处理单元

    :param image: 输入图片 -> numpy.array
    :return: 处理好的图片
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to the L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Merge the CLAHE enhanced L channel back with A and B channels
    limg = cv2.merge((cl, a, b))

    # Convert back to BGR color space
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img


# # 推理过程中将预测结果叠加在原始图像上
# def overlay_lane_prediction(image_path):
#     print(image_path)
#     model = load_model()
#     image = cv2.imread(image_path)
#     image = enhance_contrast(image)
#     original_size = image.shape[:2]
#
#     img = cv2.resize(image, (128, 128))
#     img = img / 255.0
#     img = np.expand_dims(img, axis=0)
#
#     prediction = model.predict(img)
#     prediction = np.squeeze(prediction)
#     prediction = cv2.resize(prediction, (original_size[1], original_size[0]))
#
#     pred_mask = model.predict(np.expand_dims(img, axis=0))[0]
#     pred_mask_img = pred_mask.squeeze()
#
#     # Threshold the prediction to get binary mask
#     _, binary_mask = cv2.threshold(prediction, 0.5, 1, cv2.THRESH_BINARY)
#     binary_mask = binary_mask.astype(np.uint8)
#
#     # Create a three-channel mask
#     lane_mask = np.zeros_like(image)
#     lane_mask[:, :, 1] = 255 * binary_mask  # Green channel for lane lines
#
#     # Combine lane mask with original image
#     overlay_image = cv2.addWeighted(image, 1, lane_mask, 0.5, 0)
#
#     return pred_mask_img, overlay_image

# file
# def is_night_image(image):
#     # 将图像转换为灰度图
#     gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
#
#     # 计算图像的平均亮度
#     average_brightness = np.mean(gray_image)
#
#     # 设定一个阈值来判断是否为夜间图像
#     night_threshold = 50
#
#     # 如果平均亮度低于阈值，则认为是夜间图像
#     return average_brightness < night_threshold

# pil
def is_night_image(image):
    """
    图像光照度检测

    :param image: 待处理图片矩阵
    :return: (bool, avg_brightness)
    """
    # np_image = np.array(image, dtype=np.uint8)
    # 将图像转换为灰度图
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # 计算图像的平均亮度
    average_brightness = np.mean(gray_image)

    # 设定一个阈值来判断是否为夜间图像
    night_threshold = 50

    # 如果平均亮度低于阈值，则认为是夜间图像
    return (average_brightness < night_threshold, average_brightness)


def overlay_lane_prediction(image_path):
    """
    模块一处理函数：车道线检测

    :param image_path: 输入图片
    :type: PIL
    :return: (预测掩码 -> img，原图掩码合并 -> img，光照感应 -> float，车道偏离 -> str)
    """
    try:
        width, height = image_path.size
        size = (width, height)
    except TypeError as E:
        height, width, channels = image_path.shape
        size = (width, height)

    # print(image_path)
    model = load_model()
    np_image = np.array(image_path)
    # 如果原始图像是 RGB，需要将其转换为 BGR，因为 OpenCV 使用 BGR 通道顺序
    try:
        if image_path.mode == 'RGB':
            np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            # image = cv2.imread(image_path)
    except AttributeError:
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    image = enhance_contrast(np_image)
    original_size = image.shape[:2]

    img = cv2.resize(image, (128, 128))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)[0]  # 直接获取第一个预测结果
    prediction = cv2.resize(prediction, (original_size[1], original_size[0]))

    # pred_mask = model.predict(np.expand_dims(img, axis=0))[0]
    # pred_img = pred_mask.squeeze()

    # 假设 prediction 是单通道的（例如，概率图）
    _, binary_mask = cv2.threshold(prediction, 0.5, 1, cv2.THRESH_BINARY)
    binary_mask = binary_mask.astype(np.uint8)

    # 创建三通道掩码
    lane_mask = np.zeros_like(image)
    lane_mask[:, :, 1] = 255 * binary_mask  # 绿色通道用于车道线

    # 合并车道掩码与原始图像
    overlay_image = cv2.addWeighted(image, 1, lane_mask, 0.5, 0)
    overlay_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2RGB)

    # 直接使用传入的PIL图像对象
    result, avg_light = is_night_image(image_path)
    if result:
        warn = f"视野较暗，缓慢行驶\n(平均亮度：{avg_light})"
    else:
        warn = f'视野正常，行车小心\n(平均亮度：{avg_light})'

    prediction = cv2.resize(prediction, size)
    overlay_image = cv2.resize(overlay_image, size)

    a = detect_lane_departure(np_image)

    # 创建并启动一个新线程来执行语音播报
    thread = threading.Thread(target=speak_response, args=(a,))
    thread.start()

    return prediction, overlay_image, warn, a


def province_num(string):
    if string:
        if string == "":
            return ""
        else:
            if 8 >= len(string) >= 7:
                province = string[0]
                number = string[1:]
            else:
                gr.Error("车牌号输入错误")
                province = ""
                number = ""
    else:
        province = ""
        number = ""
    return province, number


def detect_lane_departure(image):
    """
    车道偏离预警

    :param image: 图片矩阵
    :return: 偏离情况 -> str
    """
    # 将图像转换为灰度图
    # image = np.array(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用Canny边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 使用霍夫变换检测线段
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=100)

    # 初始化底部坐标列表
    bottom_points = []

    # 遍历检测到的线段，找到底部的点
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 假设图像底部附近的线段才是车道线
            if y2 > image.shape[0] - 10:
                bottom_points.append((x1, y1))
                bottom_points.append((x2, y2))

                # 如果找到了两个或更多的底部点
    if len(bottom_points) >= 2:
        # 计算这些点的x坐标的平均值，作为中点A的x坐标
        A_x = sum(point[0] for point in bottom_points) // len(bottom_points)
        A_y = image.shape[0]  # 中点A的y坐标设为图像底部

        # 计算图像宽度中心点的中点B
        B_x = image.shape[1] // 2
        B_y = image.shape[0]  # 中点B的y坐标同样设为图像底部

        # 计算中点A与中点B的水平距离
        distance = abs(A_x - B_x)

        # 判断是否偏离
        if distance <= 10:
            return "未偏离"
        else:
            return "偏离方向：左边" if A_x < B_x else "偏离方向：右边"
    else:
        return "未检测到足够的车道线"


# 用于存储 TensorBoard 进程的变量
tensorboard_process = None


def start_tensorboard(log_dir):
    """
    tensorboard启动线程

    :param log_dir: --logdir参数（设置日志路径）
    :return: 状态
    """
    global tensorboard_process
    if tensorboard_process is not None:
        # 如果 TensorBoard 已经在运行，先停止它
        tensorboard_process.terminate()
        tensorboard_process.wait()

    try:
        if not log_dir or log_dir == "":
            raise FileNotFoundError("路径为空")
        # 启动 TensorBoard
        tensorboard_process = subprocess.Popen(['tensorboard', '--logdir', log_dir])
        time.sleep(5)  # 等待 TensorBoard 启动
        webbrowser.open("http://localhost:6006/")
        return "TensorBoard 已启动：http://localhost:6006/"

    except Exception as f:
        return f"启动失败：{f}"


def stop_tensorboard():
    """
    tensorboard线程关闭

    :return: 状态
    """
    global tensorboard_process
    if tensorboard_process is not None:
        tensorboard_process.terminate()
        tensorboard_process.wait()
        return "TensorBoard 已停止"
    else:
        return "TensorBoard 未在运行"


def button(log_dir, mode):
    """
    模块二：tensorboard启动与关闭（实时）

    :param log_dir: 输入一：训练日志路径
    :param mode: 输入二：模式选择
    :return: 状态
    """
    if mode == '关闭':
        text = stop_tensorboard()
        return text
    elif mode == "启动":
        text = start_tensorboard(log_dir)
        return text
    else:
        text = stop_tensorboard()
        return "程序未启动，请选择启动或关闭"


def routing(start, end, strategy="32", plate="", cartype="0"):
    # 省份＋城市＋区县＋城镇＋乡村＋街道＋门牌号码
    # key因测试使用，调整至每日限额10次
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"

    start_city = None
    end_city = None

    if "市" in start:
        if '省' in start:
            start_city = f"{re.split(r'[省市]', start)[1]}市"
        else:
            start_city = start.split('市')[0]
    if not start_city:
        start_city = ""

    if "市" in end:
        if '省' in end:
            end_city = f"{re.split(r'[省市]', end)[1]}市"
        else:
            end_city = end.split('市')[0]
    if not end_city:
        end_city = ""

    start_params = {
        "key": "71f1bd04afd00969c7b37cbfc8262a2a",
        "address": f"{start}",
        "city": f"{start_city}",
        "output": "JSON"
    }
    end_params = {
        "key": "71f1bd04afd00969c7b37cbfc8262a2a",
        "address": f"{end}",
        "city": f"{end_city}",
        "output": "JSON"
    }
    start_address = rq.get(url, params=start_params)
    end_address = rq.get(url, params=end_params)

    start_text = start_address.json()
    # print(start_text)
    end_text = end_address.json()

    if start_address.status_code == "0" or end_address.status_code == "0":
        return f"起始地点Error：{start_text['info']}，\n终点Error：{end_text['info']}"

    start_BL = start_text['geocodes'][0]['location']
    end_BL = end_text['geocodes'][0]['location']

    if plate:
        plate = plate
    else:
        plate = ''

    if "：" in strategy:
        strategy = strategy.split('：')[0]
    if "：" in cartype:
        cartype = cartype.split('：')[0]


    mode_dict = {
        '0': "0",
        '1': "1",
        '2': "2",
        '32': "10",
        '33': "4",
        '34': "0",
        '35': "6",
        '36': "7",
        '37': "0",
        '38': "0",
        '39': "8",
        '40': "9",
        '41': "8",
        '42': "9",
        '43': "9",
        '44': "10",
        '45': "0",
    }

    data = {
        "key": "71f1bd04afd00969c7b37cbfc8262a2a",
        "origin": f"{start_BL}",
        "destination": f"{end_BL}",
        "strategy": f"{strategy}",
        "plate": f"{plate}",
        "cartype": f"{cartype}"
    }
    rout = rq.post("https://restapi.amap.com/v5/direction/driving?parameters", data=data)
    rout_text = rout.json()

    if rout.status_code == "0":
        return f"Error:{rout_text['info']}"

    rout_data = []
    # print(rout_text['route']['paths'][0]['steps'])
    for id, i in enumerate(rout_text['route']['paths'][0]['steps']):
        # print(i)
        rout_data.append(i['instruction'])

    data_rote = f"从{start}出发\n" + "\n".join(rout_data) + f"最终到达终点"

    html = f"""
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
            <title>位置经纬度 + 驾车规划路线</title>
            <script type="text/javascript">
              window._AMapSecurityConfig = {{
                  securityJsCode:'cff01f015858861e45f2415c25b3fff1',
              }}
            </script>
            <style type="text/css">
            html,
            body,
            #container {{
              width: 100%;
              height: 100%;
            }}
            </style>
            <style type="text/css">
                #panel {{
                    position: fixed;
                    background-color: white;
                    max-height: 90%;
                    overflow-y: auto;
                    top: 10px;
                    right: 10px;
                    width: 280px;
                }}
                #panel .amap-call {{
                    background-color: #009cf9;
                    border-top-left-radius: 4px;
           	        border-top-right-radius: 4px;
                }}
                #panel .amap-lib-driving {{
        	        border-bottom-left-radius: 4px;
           	        border-bottom-right-radius: 4px;
                    overflow: hidden;
                }}
            </style>
            <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css" />
            <script src="https://a.amap.com/jsapi_demos/static/demo-center/js/demoutils.js"></script>
            <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key=969daf5ed11451b3df75146f0d41ba66&plugin=AMap.Driving"></script>
            <script type="text/javascript" src="https://cache.amap.com/lbs/static/addToolbar.js"></script>
        </head>
        <body>
        <div id="container"></div>
        <div id="panel"></div>
        <script type="text/javascript">
            //基本地图加载
            var map = new AMap.Map("container", {{
                resizeEnable: true,
                center: [{start_BL}],//地图中心点
                zoom: 13 //地图显示的缩放级别
            }});
            //构造路线导航类
            var driving = new AMap.Driving({{
                map: map,
                panel: "panel"
            }}); 
            // 根据起终点经纬度规划驾车导航路线
            driving.search(new AMap.LngLat({start_BL}), new AMap.LngLat({end_BL}), function(status, result) {{
                // result 即是对应的驾车导航信息，相关数据结构文档请参考  https://lbs.amap.com/api/javascript-api/reference/route-search#m_DrivingResult
                if (status === 'complete') {{
                    log.success('绘制驾车路线完成')
                    console.log(result)
                }} else {{
                    log.error('获取驾车数据失败：' + result)
                }}
            }});
        </script>
        </body>
        </html>
        """

    with open(f"road.html", 'w', encoding='utf-8') as file:
        file.write(html)
    webbrowser.open(f'file://{os.getcwd()}/road.html', new=2)  # new=2 表示在新标签页中打开

    province, number = province_num(plate)

    driving_params = {
        "key": "71f1bd04afd00969c7b37cbfc8262a2a",
        "origin": f"{start_BL}",
        "destination": f"{end_BL}",
        "strategy": f"{mode_dict[strategy]}",
        "province": f"{province}",
        "number": f"{number}",
        "cartype": f"{cartype}",
        "roadaggregation": "True",
        "extensions": "all"
    }
    driving_rout = rq.get("https://restapi.amap.com/v3/direction/driving?parameters", params=driving_params)
    # with open('1.txt', 'w', encoding='utf-8') as f:
    #     f.write(driving_rout.text)
    # driving_rout_text = json.loads(driving_rout.text)
    driving_rout_text = driving_rout.json()
    driving_data_BL = Json_Data(driving_rout_text)

    driving_html = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <title>轨迹回放</title>
    <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css"/>
    <style>
        html, body, #container {{
            height: 100%;
            width: 100%;
        }}

        .input-card .btn{{
            margin-right: 1.2rem;
            width: 9rem;
        }}

        .input-card .btn:last-child{{
            margin-right: 0;
        }}
    </style>
</head>
<body>
<div id="container"></div>
<div class="input-card">
    <h4>轨迹回放控制</h4>
    <div class="input-item">
        <input type="button" class="btn" value="开始动画" id="start" onclick="startAnimation()"/>
        <input type="button" class="btn" value="暂停动画" id="pause" onclick="pauseAnimation()"/>
    </div>
    <div class="input-item">
        <input type="button" class="btn" value="继续动画" id="resume" onclick="resumeAnimation()"/>
        <input type="button" class="btn" value="停止动画" id="stop" onclick="stopAnimation()"/>
    </div>
</div>
<script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key=969daf5ed11451b3df75146f0d41ba66"></script>
<script>
    // JSAPI2.0 使用覆盖物动画必须先加载动画插件
    AMap.plugin('AMap.MoveAnimation', function(){{
        var marker, lineArr = {driving_data_BL};

        var map = new AMap.Map("container", {{
            resizeEnable: true,
            center: [{start_BL}],
            zoom: 17
        }});

        marker = new AMap.Marker({{
            map: map,
            position: [{start_BL}],
            icon: "https://a.amap.com/jsapi_demos/static/demo-center-v2/car.png",
            offset: new AMap.Pixel(-13, -26),
        }});

        // 绘制轨迹
        var polyline = new AMap.Polyline({{
            map: map,
            path: lineArr,
            showDir:true,
            strokeColor: "#28F",  //线颜色
            // strokeOpacity: 1,     //线透明度
            strokeWeight: 6,      //线宽
            // strokeStyle: "solid"  //线样式
        }});

        var passedPolyline = new AMap.Polyline({{
            map: map,
            strokeColor: "#AF5",  //线颜色
            strokeWeight: 6,      //线宽
        }});


        marker.on('moving', function (e) {{
            passedPolyline.setPath(e.passedPath);
            map.setCenter(e.target.getPosition(),true)
        }});

        map.setFitView();

        window.startAnimation = function startAnimation () {{
            marker.moveAlong(lineArr, {{
                // 每一段的时长
                duration: 500,//可根据实际采集时间间隔设置
                // JSAPI2.0 是否延道路自动设置角度在 moveAlong 里设置
                autoRotation: true,
            }});
        }};

        window.pauseAnimation = function () {{
            marker.pauseMove();
        }};

        window.resumeAnimation = function () {{
            marker.resumeMove();
        }};

        window.stopAnimation = function () {{
            marker.stopMove();
        }};
    }});
</script>
</body>
</html>
"""

    with open(f"driving.html", 'w', encoding='utf-8') as file:
        file.write(driving_html)
    webbrowser.open(f'file://{os.getcwd()}/driving.html', new=2)  # new=2 表示在新标签页中打开

    return data_rote

ip = get_external_ip()

def IP_address(_ip_):
    url = "https://restapi.amap.com/v3/ip?parameters"

    params = {
        "key": "71f1bd04afd00969c7b37cbfc8262a2a",
        "ip": f"{_ip_}"
    }

    if _ip_ == ip['ip']:
        x, y = ip["x"], ip["y"]
    else:
        x, y = "", ""

    address = rq.get(url=url, params=params)

    address_json = address.json()

    province = address_json['province']
    city = address_json['city']

    if not province:
        gr.Error("非法地址，请重新输入！")
        return "非法地址，请重新输入！"

    return province, city, f"{x}, {y}"


# def generate_file(file_obj):
#     global tmpdir
#     print('临时文件夹地址：{}'.format(tmpdir))
#     print('上传文件的地址：{}'.format(file_obj.name))  # 输出上传后的文件在gradio中保存的绝对地址
#
#     # 获取到上传后的文件的绝对路径后，其余的操作就和平常一致了
#
#     # 将文件复制到临时目录中
#     shutil.copy(file_obj.name, tmpdir)
#
#     # 获取上传Gradio的文件名称
#     FileName = os.path.basename(file_obj.name)


# with tempfile.TemporaryDirectory(dir='.') as tmpdir:
#     # 定义输入和输出
#     inputs = gr.components.File(label="上传文件")
#     outputs = gr.components.File(label="下载文件")
#
#     # 创建 Gradio 应用程序g
#     app = gr.Interface(fn=generate_file, inputs=inputs, outputs=outputs, title="文件上传、并生成可下载文件demo",
#                        description="上传任何文件都可以，只要大小别超过你电脑的内存即可"
#                        )
#
#     # 启动应用程序
#     app.launch(share=True)


def generate_file(uploaded_file):
    # 创建一个临时文件夹
    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        # 假设uploaded_file是一个文件路径（这取决于Gradio如何传递上传的文件）
        # 如果uploaded_file不是文件路径，你可能需要将其转换为文件路径或处理为文件流

        # 完整的文件路径，这里假设uploaded_file已经是一个包含文件路径的字符串
        zip_path = uploaded_file
        logger.info('临时文件夹地址：{}'.format(tmpdir))
        logger.info('上传文件的地址：{}'.format(zip_path))  # 输出上传后的文件在gradio中保存的绝对地址

        # 解压ZIP文件到临时文件夹
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

            # 此时，tmpdir包含了解压后的文件
        # 但由于with语句的作用，tmpdir将在这一步之后被删除
        # 如果你需要让用户下载解压后的某个文件或整个文件夹（注意：通常不直接下载文件夹），
        # 你需要在这里处理它。例如，你可以选择解压后的一个文件返回给用户。

        # 假设我们返回解压后的第一个文件（仅作为示例）
        # 注意：这可能需要你根据实际需求调整
        files_in_dir = os.listdir(tmpdir)
        if files_in_dir:
            first_file_path = os.path.join(tmpdir, files_in_dir[0])
            # 返回文件路径作为下载链接（注意：这通常不是最佳实践，因为文件可能已被删除）
            # 但由于Gradio的特定行为，它可能能够处理这种情况
            logger.info(first_file_path)
        else:
            # ZIP文件为空或解压失败
            return "ZIP文件为空或解压失败"


def CampsVideo(image):
    # print(image)
    image = np.array(image)
    image = Image.fromarray(image)

    # 将Gradio传递的图像转换为numpy数组
    prediction, overlay_image, warn, a = overlay_lane_prediction(image)
    return prediction, overlay_image, warn, a




def take_video(video):
    # 读取视频
    global frame, timestamp
    cap = cv2.VideoCapture(video)
    # cap.set(cv2.CAP_PROP_FPS, desired_fps)  # 尝试设置帧率，但可能不适用于所有视频文件

    # 遍历视频的每一帧
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            # 将帧从BGR转换为RGB（因为OpenCV使用BGR格式，但很多模型需要RGB）
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 获取当前帧的毫秒数
        milliseconds = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        # 转换为秒
        seconds = milliseconds // 1000
        # 分离出时、分、秒
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        # 格式化时间戳
        timestamp = "{:02d}:{:02d}:{:02d}".format(hours, minutes, secs)

        prediction, overlay_image, warn, a = overlay_lane_prediction(frame)  # emotion_classes是你在其他地方定义的标签列表

        yield prediction, overlay_image, warn, a

    # 释放视频文件
    cap.release()


# 如若是Text，则去掉history，如果是ChatInterface则加上
def chatbot_response(message, history):
    # bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    # 配置密钥与应用ID
    os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-prxvvKb8NBpeTxYwI4Kpn/3f453af9371e76a8451ef5fb758e78c03be2bcad"
    app_id = "f6932dcb-3edb-4b07-b1e2-ae1483f93ef7"

    # 初始化Agent实例
    builder = appbuilder.AppBuilderClient(app_id)

    # 创建会话ID
    conversation_id = builder.create_conversation()

    # 执行对话
    msg = builder.run(conversation_id, message)
    # print("篮球教练回答内容：", msg.content.answer)

    # 创建并启动一个新线程来执行语音播报
    thread = threading.Thread(target=speak_response, args=(msg.content.answer,))
    thread.start()


    yield msg.content.answer


# def overlay_lane_prediction(image_path):
#     model = load_model()
#     image = cv2.imread(image_path)
#     image = enhance_contrast(image)
#     original_size = image.shape[:2]
#
#     # 预处理图像以匹配模型输入
#     img = cv2.resize(image, (128, 128))
#     img = img / 255.0
#     img = np.expand_dims(img, axis=0)
#
#     # 获取预测结果
#     prediction = model.predict(img)[0]
#     pred_mask = model.predict(np.expand_dims(img, axis=0))[0]
#     pred_img = pred_mask.squeeze()
#
#
#     # 假设 prediction 是单通道的（例如，概率图），我们需要将其二值化
#     _, binary_mask = cv2.threshold(prediction, 0.5, 1, cv2.THRESH_BINARY)
#     binary_mask = binary_mask.astype(np.uint8)
#
#     # 将二值掩码调整回原始图像大小
#     binary_mask = cv2.resize(binary_mask, (original_size[1], original_size[0]))
#
#     # 创建三通道掩码（这里只使用绿色通道）
#     lane_mask = np.zeros_like(image)
#     lane_mask[:, :, 1] = binary_mask * 255  # 绿色通道用于车道线
#
#     # 合并车道掩码与原始图像
#     overlay_image = cv2.addWeighted(image, 1, lane_mask, 0.5, 0)
#
#     # 返回车道掩码和合并后的图像
#     return pred_img, overlay_image


# 创建Gradio接口
iface = gr.Interface(
    fn=overlay_lane_prediction,
    inputs=gr.Image(type="pil", label="输入图像"),  # 输入是一张128x128的PIL图片
    outputs=[gr.Image(label='车道线掩码'), gr.Image(label='预测图片'), gr.Textbox(label='行车视野检测', interactive=False),
             gr.Label(label='偏离预警')],  # 输出是车道线检测的mask图
    title="车道线检测 & 补全",
    description="车道线检测&补全"
)

# 原始预测
# app2 = gr.Interface(
#     fn=overlay_lane_prediction,
#     inputs=gr.Image(type="filepath"),  # 输入是一张128x128的PIL图片
#     outputs=[gr.Image(label='Lane Detection Mask'), gr.Image(label='pred_img')],  # 输出是车道线检测的mask图
#     title="Lane Detection with Gradio",
#     description="Upload an image to see the detected lane lines."
# )

app_video = gr.Interface(fn=take_video,
                    # inputs=gr.Video(sources=["upload", "webcam"], label="上传MP4视频"),
                    inputs=gr.Video(label="上传MP4视频"),
                    # outputs=gr.Markdown(label="Labels"),
                    outputs=[gr.Image(label='车道线掩码'), gr.Image(label='预测图片'), gr.Textbox(label='行车视野检测', interactive=False),
             gr.Label(label='偏离预警')],
                    # output_interface = [gr.Video(label="输出视频",show_download_button=True),gr.Video(label="输出视频",show_download_button=True,format='mp4')],
                    description="可进行视频分析识别",
                    title="视频流检测")


app2 = gr.Interface(
    fn=CampsVideo,
    inputs=[gr.Image(label="摄像头", source="webcam", streaming=True)],  # 输入是一张128x128的PIL图片
    outputs=[gr.Image(label='车道线掩码'), gr.Image(label='预测图片'), gr.Textbox(label='行车视野检测', interactive=False),
             gr.Label(label='偏离预警')],  # 输出是车道线检测的mask图
    title="实时预测",
    description="实时图像分析：默认使用第一摄像头，例如手机前置"
)

# 训练图像展示
app3 = gr.Interface(
    fn=button,
    inputs=[gr.Textbox(value="../model/2024-07-13ALL/logs/fit", info="请输入logdir路径，默认为初始logdir", label="--logdir",
                       show_label=True, show_copy_button=True),
            gr.Radio(type='value', label="模式选择", choices=['关闭', '启动'], value='关闭')],
    outputs=gr.Label(label="状态"),
    examples=[["../model/2024-07-13ALL/logs/fit"]],
    analytics_enabled=True,
    title="TensorBoard",
    description="输出训练日志",
    examples_per_page=1,
    live=True
)

choice = ['0：速度优先（只返回一条路线），此路线不一定距离最短',
          '1：费用优先（只返回一条路线），不走收费路段，且耗时最少的路线',
          '2：距离优先（只返回一条路线），仅走距离最短的路线，但是可能存在穿越小路/小区的情况',
          '32：默认，高德推荐，同高德地图APP默认',
          '33：躲避拥堵',
          '34：高速优先',
          '35：不走高速',
          '36：少收费',
          '37：大路优先',
          '38：速度最快',
          '39：躲避拥堵＋高速优先',
          '40：躲避拥堵＋不走高速',
          '41：躲避拥堵＋少收费',
          '42：少收费＋不走高速',
          '43：躲避拥堵＋少收费＋不走高速',
          '44：躲避拥堵＋大路优先',
          '45：躲避拥堵＋速度最快']

car_type = [
    '0：普通燃油汽车',
    '1：纯电动汽车',
    '2：插电式混动汽车']

app4 = gr.Interface(
    fn=routing,
    inputs=[gr.Textbox(value="深圳信息职业技术学院", info="最好填写 省份＋城市＋区县＋城镇＋乡村＋街道＋门牌号码",
                       label="起始地点",
                       show_label=True, show_copy_button=True),
            gr.Textbox(value="大运中心", info="最好填写 省份＋城市＋区县＋城镇＋乡村＋街道＋门牌号码", label="目的地",
                       show_label=True, show_copy_button=True),
            gr.Dropdown(choices=choice, label="驾车算路策略（可选）", value="32：默认，高德推荐，同高德地图APP默认"),
            gr.Textbox(info="车牌号，如 京AHA322，支持6位传统车牌和7位新能源车牌，用于判断限行相关。",
                       label="车牌号码（可选）",
                       show_label=True, show_copy_button=True),
            gr.Dropdown(choices=car_type, label="车辆类型（可选）", value="0：普通燃油汽车")],
    outputs=[gr.Textbox(label="路线", show_copy_button=True, value="", interactive=False)],
    analytics_enabled=True,
    title="路线规划",
    description="用于规划路线",
    examples_per_page=1,
)

app5 = gr.Interface(
    fn=IP_address,
    inputs=gr.Textbox(value=ip["ip"], info="填写外部IP地址，默认为本地外部IP", label="IP地址", show_label=True, show_copy_button=True),
    outputs=[gr.Label(value="", label="省份"), gr.Label(value="", label="城市"), gr.Label(value="", label='经纬度')],
    examples=[[f"{ip['ip']}"]],
    title="IP模糊定位"
)

# app6 = gr.Interface(
#     fn=chatbot_response,
#     inputs=gr.Textbox(label="请输入问题/随意聊天:"),
#     outputs=gr.Textbox(label="聊天助手的回复:", value=""),
#     description="实时在线的智能管家",
#     title="智行伴侣SmartDriveMate",
#     examples=['在驾驶过程中遇到紧急情况，该如何处理？', '如果我明天早上八点钟前要到达凯丽酒店，并且要在九点半前把我的儿子送去凯丽酒店附近的游泳馆，然后在十点钟准时到达学校参加会议，会议大概需要两个小时，然后晚上九点半需要回家与亲人一起吃饭，请帮我规划行程']
# )

app6 = gr.ChatInterface(
    fn=chatbot_response,
    description="实时在线的智能管家",
    title="智行伴侣SmartDriveMate",
    examples=['在驾驶过程中遇到紧急情况，该如何处理？', '如果我明天早上八点钟前要到达凯丽酒店，并且要在九点半前把我的儿子送去凯丽酒店附近的游泳馆，然后在十点钟准时到达学校参加会议，会议大概需要两个小时，然后晚上九点半需要回家与亲人一起吃饭，请帮我规划行程', "今天龙岗区天气如何？", "深圳信息职业技术学院位于哪里？"],
    submit_btn="发送",
    stop_btn="停止",
    retry_btn="重试",
    undo_btn="撤销",
    clear_btn="清除"
)

# with gr.Blocks(js=js) as app4:
#     with gr.Row():
#         start = gr.Textbox(value="深圳信息职业技术学院", info="最好填写 省份＋城市＋区县＋城镇＋乡村＋街道＋门牌号码",
#                            label="起始地点", show_label=True, show_copy_button=True)
#         destination = gr.Textbox(value="大运中心", info="最好填写 省份＋城市＋区县＋城镇＋乡村＋街道＋门牌号码",
#                                  label="目的地", show_label=True, show_copy_button=True)
#     with gr.Row():
#         strategy = gr.Dropdown(choices=["32：默认，高德推荐，同高德地图APP默认", "其他策略"], label="驾车算路策略（可选）",
#                                value="32：默认，高德推荐，同高德地图APP默认")
#         car_plate = gr.Textbox(info="车牌号，如 京AHA322，支持6位传统车牌和7位新能源车牌，用于判断限行相关。",
#                                label="车牌号码（可选）", show_label=True, show_copy_button=True)
#         car_type = gr.Dropdown(choices=["0：普通燃油汽车", "其他类型"], label="车辆类型（可选）", value="0：普通燃油汽车")
#     submit_button = gr.Button("提交")
#     output = gr.HTML(label="路线")
#
#     # 当提交按钮被点击时，调用routing函数并更新输出
#     submit_button.click(fn=routing, inputs=[start, destination, strategy, car_plate, car_type], outputs=[output])





# 使用gradio创建Web界面
iface_all = gr.TabbedInterface(
    [iface, app_video, app2, app3, app4, app5, app6],
    tab_names=["车道线检测", "视频检测", "实时检测", "tensorboard日志", "路线规划", "ip模糊定位", "智行伴侣"],
    title="智行领航",
    css=css
)
iface_all.queue()  # <-- Sets up a queue with default parameters

"""
`gradio.blocks.Blocks.launch` 方法是 Gradio 库中用于启动一个基于 Blocks 的交互式应用的方法。这个方法提供了大量的参数，允许你高度定制启动的应用。下面是对一些关键参数的解释：

- `inline`: 布尔值，指定是否在 Jupyter Notebook 中以内联方式显示应用。
- `inbrowser`: 布尔值，指定是否在默认的 web 浏览器中打开应用。
- `share`: 布尔值，指定是否生成一个可分享的 URL，以便其他人可以访问你的应用。
- `debug`: 布尔值，指定是否以调试模式启动应用，这通常会在控制台中打印更多的调试信息。
- `enable_queue`: 布尔值，指定是否启用请求队列，这在处理大量并发请求时可能很有用。
- `max_threads`: 整数，指定应用可以处理的最大线程数。
- `auth`: 用于认证的函数或元组列表，用于在应用上设置基本的认证机制。
- `auth_message`: 字符串，指定在认证失败时显示的消息。
- `prevent_thread_lock`: 布尔值，指定是否防止线程锁定，这在某些多线程环境中可能很有用。
- `show_error`: 布尔值，指定是否在应用中显示错误消息。
- `server_name`: 字符串，指定应用的服务器名称。
- `server_port`: 整数，指定应用的服务器端口。
- `show_tips`: 布尔值，指定是否在应用中显示提示信息。
- `height`: 整数，指定应用窗口的高度。
- `width`: 字符串或整数，指定应用窗口的宽度。
- `encrypt`: 布尔值，指定是否对通信进行加密。
- `favicon_path`: 字符串，指定应用图标（favicon）的路径。
- `ssl_keyfile`, `ssl_certfile`, `ssl_keyfile_password`, `ssl_verify`: 这些参数与 SSL 加密相关，用于设置 SSL 密钥文件、证书文件、密钥文件密码和是否验证 SSL 证书。
- `quiet`: 布尔值，指定是否在启动时打印消息。
- `show_api`: 布尔值，指定是否在应用中显示 API 文档。
- `file_directories`, `allowed_paths`, `blocked_paths`, `root_path`: 这些参数与文件访问权限相关，用于设置允许或阻止访问的文件目录和路径。
- `_frontend`: 布尔值，指定是否启动前端界面。
- `app_kwargs`: 字典，包含传递给 FastAPI 应用的其他关键字参数。
- `state_session_capacity`: 整数，指定状态会话的容量。

`launch` 方法返回一个元组，包含 FastAPI 应用实例、应用的 URL 和（如果启用了 SSL）HTTPS URL。这使得你可以进一步定制或操作启动的应用。
"""

