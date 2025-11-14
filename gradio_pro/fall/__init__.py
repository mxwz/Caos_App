import os
import random
from io import BytesIO

import paddle
import paddle.vision.transforms as T
from paddle.vision.transforms import Compose, Resize, ToTensor, Normalize
from PIL import Image
import numpy as np
import gradio as gr
import cv2
import threading
import webbrowser
import onnxruntime as rt
import appbuilder
from scipy.io.wavfile import write

emo_comfort = {
    "anger": ["我注意到您现在有些生气，是不是有什么事情让您感到不满？我们可以一起谈谈，找到解决问题的方法。",
              "看到您这样，我知道您可能遇到了让人愤怒的事情。请冷静下来，我们一起面对。",
              "愤怒是情绪的一种，但不要让它控制您。如果需要倾诉，我愿意倾听。",
              "有时候，生气也是一种力量，但请记得用它来推动改变，而不是伤害自己。",
              '我明白您的愤怒，但请记住，保持冷静才能更好地解决问题。'],
    "disgust": ["我知道您对这种事物感到反感，但请记住，您的感受是最重要的。",
                "厌恶是您的权利，但请不要让这种情绪影响您的健康。我们可以一起寻找解决之道。",
                "我理解您对这种行为的反感，我会尽力避免类似的事情再次发生。",
                "您的反感是正常的，我们都有不喜欢的东西。如果您需要谈谈，我随时都在。",
                "看到您对这种情况感到厌恶，我明白您的感受。我们一起想办法改善这种情况。"],
    "fear": ["恐惧是人之常情，但请记住，您有能力面对它，并战胜它。", "我知道您此刻可能感到不安，但请相信，一切都会好起来的。",
             "看到您害怕，我很难过。但请记住，恐惧只是暂时的，我们会一起度过难关。",
             "恐惧是一种自然的情绪，但请记住，勇气和恐惧是并存的。您有能力克服它。",
             "我知道您现在可能感到害怕，但请记住，您并不孤单。我会一直在您身边。"],
    "happiness": ["快乐是生活的调味品，愿您每天都充满快乐和幸福。",
                  "看到您笑得这么开心，我知道您一定很幸福。希望这种幸福能够一直延续。",
                  "快乐的时光总是短暂的，但我会珍惜和您一起度过的每一刻。",
                  "您的幸福是我最大的快乐。希望您继续保持这份好心情。",
                  "看到您这么快乐，我也感到很开心。愿您的快乐永远伴随着您。"],
    "neutral": ["有时候，平静也是一种力量。愿您能够保持内心的平静和安宁。",
                "看到您如此平静，我知道您一定能够处理任何情况。如果需要帮助，请随时告诉我。",
                "无情绪也是一种状态，如果您需要一些建议或者支持，我会尽我所能。",
                "我理解您此刻可能没有什么特别的情绪，但请记住，我一直都在这里。",
                "看到您此刻表情平静，我猜测您可能正在沉思。如果需要陪伴或者聊聊，请随时告诉我。"],
    "sadness": ["看到您这样，我知道您一定很难过。但请记住，我会一直陪伴您，直到您再次微笑。",
                "悲伤是生活的一部分，但请记住，您有能力克服它。我会一直支持您。",
                "我知道您现在可能感到心痛，但请相信，美好的未来在等着您。",
                "忧愁是暂时的，但请记住，您并不孤单。我会一直陪伴在您身边。",
                "看到您如此悲伤，我真的很难过。请相信，时间会治愈一切。"],
    "surprise": ["我知道您此刻一定很惊讶，但请记住，无论发生什么，我都会在这里陪伴您。",
                 "惊奇是探索世界的动力，希望这份惊奇能够激发您更多的好奇心。",
                 "看到您惊讶的表情，我也很好奇发生了什么事情。愿意和我分享吗？",
                 "惊讶是生活中的一种乐趣，希望这份惊奇能够给您带来快乐和新的发现。",
                 "看到您这么惊讶，我知道一定有什么特别的事情发生了。愿这份惊奇给您带来好运。"]
}

css = """
.gradio-container {
  background-image: url('https://www.bizhigq.com/pc-img/2023-08/7508.jpg'); 
  border: 1px solid #000000;
  border-radius: 10px;
  padding: 20px;
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


def nms(pred, conf_thres, iou_thres):
    conf = pred[..., 4] > conf_thres
    box = pred[conf == True]
    cls_conf = box[..., 5:]
    cls = []
    for i in range(len(cls_conf)):
        cls.append(int(np.argmax(cls_conf[i])))
    total_cls = list(set(cls))
    output_box = []
    for i in range(len(total_cls)):
        clss = total_cls[i]
        cls_box = []
        for j in range(len(cls)):
            if cls[j] == clss:
                box[j][5] = clss
                cls_box.append(box[j][:6])
        cls_box = np.array(cls_box)
        box_conf = cls_box[..., 4]
        box_conf_sort = np.argsort(box_conf)
        max_conf_box = cls_box[box_conf_sort[len(box_conf) - 1]]
        output_box.append(max_conf_box)
        cls_box = np.delete(cls_box, 0, 0)
        while len(cls_box) > 0:
            max_conf_box = output_box[len(output_box) - 1]
            del_index = []
            for j in range(len(cls_box)):
                current_box = cls_box[j]
                interArea = getInter(max_conf_box, current_box)
                iou = getIou(max_conf_box, current_box, interArea)
                if iou > iou_thres:
                    del_index.append(j)
            cls_box = np.delete(cls_box, del_index, 0)
            if len(cls_box) > 0:
                output_box.append(cls_box[0])
                cls_box = np.delete(cls_box, 0, 0)
    return output_box


def getIou(box1, box2, inter_area):
    box1_area = box1[2] * box1[3]
    box2_area = box2[2] * box2[3]
    union = box1_area + box2_area - inter_area
    iou = inter_area / union
    return iou


def getInter(box1, box2):
    box1_x1, box1_y1, box1_x2, box1_y2 = box1[0] - box1[2] / 2, box1[1] - box1[3] / 2, \
                                         box1[0] + box1[2] / 2, box1[1] + box1[3] / 2
    box2_x1, box2_y1, box2_x2, box2_y2 = box2[0] - box2[2] / 2, box2[1] - box1[3] / 2, \
                                         box2[0] + box2[2] / 2, box2[1] + box2[3] / 2
    if box1_x1 > box2_x2 or box1_x2 < box2_x1:
        return 0
    if box1_y1 > box2_y2 or box1_y2 < box2_y1:
        return 0
    x_list = [box1_x1, box1_x2, box2_x1, box2_x2]
    x_list = np.sort(x_list)
    x_inter = x_list[2] - x_list[1]
    y_list = [box1_y1, box1_y2, box2_y1, box2_y2]
    y_list = np.sort(y_list)
    y_inter = y_list[2] - y_list[1]
    inter = x_inter * y_inter
    return inter


def draw(img, xscale, yscale, pred):
    img_ = img.copy()
    if len(pred):
        for detect in pred:
            detect = [int((detect[0] - detect[2] / 2) * xscale), int((detect[1] - detect[3] / 2) * yscale),
                      int((detect[0] + detect[2] / 2) * xscale), int((detect[1] + detect[3] / 2) * yscale)]
            img_ = cv2.rectangle(img, (detect[0], detect[1]), (detect[2], detect[3]), (0, 255, 0), 1)
    return img_


# 假设你有一个函数可以加载你的模型
def load_model():
    # 加载模型结构和权重
    # 这里只是一个示例，你需要根据你的模型结构来修改
    model = paddle.vision.models.resnet50(pretrained=False, num_classes=7)
    # params = paddle.load('ResNet50.pdparams')
    params = paddle.load("./ResNet50.pdparams")
    model.set_state_dict(params)
    model.eval()
    return model


# 预处理函数
def preprocess_image(image):
    # 假设你的模型需要224x224大小的图片，并且进行了归一化
    transform = T.Compose([
        T.Resize(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0)


# 预测函数
def predict_emotion(image):
    model = load_model()  # 只在第一次调用时加载模型，之后可以缓存
    image_tensor = preprocess_image(image)
    with paddle.no_grad():
        prediction = model(image_tensor)
    emotion_index = np.argmax(prediction.numpy())
    emotion_classes = [
        "anger",
        "disgust",
        "fear",
        "happiness",
        "neutral",
        "sadness",
        "surprise"
    ]

    try:
        chat = random.choice(emo_comfort[emotion_classes[emotion_index]])
        return emotion_classes[emotion_index], chat
    except Exception:
        white_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        return white_image, "无检测到人脸"


def process_emo(image):
    # 将Gradio传递的图像转换为numpy数组
    image_np = np.array(image)
    # 这里可能需要进一步的转换，具体取决于preprocess_image的要求
    transform = T.Compose([
        T.Resize(size=(224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image_tensor = transform(image_np).unsqueeze(0)

    model = load_model()  # 这里应该确保模型只被加载一次
    with paddle.no_grad():
        prediction = model(image_tensor)
    emotion_index = np.argmax(prediction.numpy())
    emotion_classes = [
        "anger",
        "disgust",
        "fear",
        "happiness",
        "neutral",
        "sadness",
        "surprise"
    ]
    return emotion_classes[emotion_index]


def fall_detection(image):
    status = None
    image_np = np.array(image)
    height, width = 640, 640
    # img0 = cv2.imread(image)
    img0 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    img_ = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
    x_scale = img0.shape[1] / width
    y_scale = img0.shape[0] / height
    img = img0 / 255.
    img = cv2.resize(img, (width, height))
    img = np.transpose(img, (2, 0, 1))
    data = np.expand_dims(img, axis=0)
    sess = load_noox()
    # sess = rt.InferenceSession(r'fall_detect.onnx')
    # sess = rt.InferenceSession(r"best.onnx")
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    pred = sess.run([label_name], {input_name: data.astype(np.float32)})[0]
    pred = np.squeeze(pred)
    pred = np.transpose(pred, (1, 0))
    pred_class = pred[..., 4:]
    pred_conf = np.max(pred_class, axis=-1)
    pred = np.insert(pred, 4, pred_conf, axis=-1)
    result = nms(pred, 0.3, 0.45)
    # print(result)
    if not result:
        # print("正常")
        status = "正常"
        ret_img = img_
    else:
        # print("跌倒")
        status = "跌倒"
        ret_img = draw(img0, x_scale, y_scale, result)
        ret_img = ret_img[:, :, ::-1]
    return ret_img, status


def load_noox(seed_dir='./fall_detect.onnx'):
    sess = rt.InferenceSession(seed_dir)
    return sess


def process_image(image, choice=None):
    if choice == '情感守护':
        # 将Gradio传递的图像转换为numpy数组
        image_np = np.array(image)
        # 这里可能需要进一步的转换，具体取决于preprocess_image的要求
        transform = T.Compose([
            T.Resize(size=(224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        image_tensor = transform(image_np).unsqueeze(0)

        model = load_model()  # 这里应该确保模型只被加载一次
        with paddle.no_grad():
            prediction = model(image_tensor)
        emotion_index = np.argmax(prediction.numpy())
        emotion_classes = [
            "anger",
            "disgust",
            "fear",
            "happiness",
            "neutral",
            "sadness",
            "surprise"
        ]
        return image, emotion_classes[emotion_index], random.choice(emo_comfort[emotion_classes[emotion_index]])
    elif choice == '跌倒防护':
        status = None
        image_np = np.array(image)
        height, width = 640, 640
        # img0 = cv2.imread(image)
        img0 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        img_ = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
        x_scale = img0.shape[1] / width
        y_scale = img0.shape[0] / height
        img = img0 / 255.
        img = cv2.resize(img, (width, height))
        img = np.transpose(img, (2, 0, 1))
        data = np.expand_dims(img, axis=0)
        sess = load_noox()
        # sess = rt.InferenceSession(r'fall_detect.onnx')
        # sess = rt.InferenceSession(r"best.onnx")
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        pred = sess.run([label_name], {input_name: data.astype(np.float32)})[0]
        pred = np.squeeze(pred)
        pred = np.transpose(pred, (1, 0))
        pred_class = pred[..., 4:]
        pred_conf = np.max(pred_class, axis=-1)
        pred = np.insert(pred, 4, pred_conf, axis=-1)
        result = nms(pred, 0.3, 0.45)
        # print(result)
        if not result:
            # print("正常")
            status = "无异常"
            word = "注意防护哦"
            ret_img = img_
        else:
            # print("跌倒")
            status = "异常！"
            word = "警告！有人跌倒啦！"
            ret_img = draw(img0, x_scale, y_scale, result)
            ret_img = ret_img[:, :, ::-1]
        return ret_img, status, word

    if not choice:
        white_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
        return white_image, "请选择模式", "再试一次吧"


def pred_label(image_tensor):
    model = load_model()  # 只在第一次调用时加载模型，之后可以缓存
    with paddle.no_grad():
        prediction = model(image_tensor)
    emotion_index = np.argmax(prediction.numpy())
    return emotion_index


def take_video(video):
    try:
        emo = None
        # 读取视频
        global emotion_class, frame, timestamp
        cap = cv2.VideoCapture(video)
        # 初始化标签列表

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

            try:
                emotion_class = process_emo(frame)  # emotion_classes是你在其他地方定义的标签列表
                # break
                # 将标签添加到列表中
                if emotion_class == emo:
                    pass
                else:
                    yield emotion_class
                emo = emotion_class

            except Exception as f:
                pass
    except Exception as f:
        print(f)
        return "线程阻塞，暂停检测"

    # 释放视频文件
    cap.release()

    # 打印所有标签（或者你可以在这里做其他处理）
    # for label in labels:
    #     print(label)

    # 将列表转换为字符串，用逗号分隔
    # label_markdown = '\n'.join(f'- {label}' for label in labels)
    # return label_markdown


def chatbot_response(message):
    # bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    # 配置密钥与应用ID
    os.environ["APPBUILDER_TOKEN"] = "百度云api"
    app_id = "26f52635-7c68-46a8-a83f-ef037a35d91e"

    # 初始化Agent实例
    builder = appbuilder.AppBuilderClient(app_id)

    # 创建会话ID
    conversation_id = builder.create_conversation()

    # 执行对话
    msg = builder.run(conversation_id, message)
    # print("篮球教练回答内容：", msg.content.answer)
    return msg.content.answer


# 示例处理函数，这里只是简单地将接收到的音频数据返回（实际应用中应进行处理）
def process_audio(audio_data: np.ndarray):
    # 假设audio_data_tuple是一个元组，包含采样率和音频数据
    print(audio_data)
    sample_rate, audio_data = audio_data
    print(sample_rate, audio_data)

    try:
        # 确保audio_data是一个NumPy数组
        if not isinstance(audio_data, np.ndarray):
            raise ValueError("audio_data must be a NumPy array")

        # 如果audio_data是多维的，我们可能需要处理它（例如，取第一维）
        if audio_data.ndim > 1:
            # 假设第一个维度是通道数，我们只取第一个通道（如果是多通道的话）
            audio_data = audio_data[0]  # 或者选择其他逻辑来处理多通道音频

        # 创建一个BytesIO对象来存储WAV文件的字节
        byte_arr = BytesIO()

        # 将NumPy数组写入WAV文件（这里假设是单声道，采样率为sample_rate）
        write(byte_arr, sample_rate, audio_data.astype(np.int16))

        print(byte_arr)

        # 将BytesIO对象移动到开始位置，以便可以读取整个内容
        byte_arr.seek(0)

        # 读取WAV文件的字节内容
        raw_audio_bytes = byte_arr.read()
        # print(raw_audio_bytes)

        # 设置环境变量（注意：这通常是在程序开始时设置的，而不是在函数内部）
        os.environ["APPBUILDER_TOKEN"] = "百度云api"

        # 假设asr和Message类已经正确导入和初始化
        asr = appbuilder.ASR()  # 确保正确导入和初始化ASR类

        # 创建Message对象，注意这里我们使用raw_audio_bytes而不是原始的NumPy数组
        content_data = {"audio_format": "wav", "raw_audio": raw_audio_bytes, "rate": sample_rate, "retry": 2}
        msg = appbuilder.Message(content_data)  # 确保正确导入Message类

        # 运行ASR
        out = asr.run(msg)
        print(out.content)

        out = out.content.get('result', None)
        out = ''.join(out)

        if not out:
            return "抱歉，识别失败，暂时无法与您聊天"
        else:
            # mess = chatbot_response(out)
            return out  # 假设out是一个包含'result'键的字典

    except Exception as e:
        print(e)
        return "别着急慢慢来，我反应不过来了"


# yes
# tags1的输入、输出，以及对应处理函数
app1 = gr.Interface(fn=predict_emotion,
                    # inputs=gr.inputs.Image(type="pil", label="上传单张图片"),
                    inputs=gr.components.Image(type="pil", label="上传单张图片"),
                    outputs=[gr.Label(num_top_classes=7, label="输出：表情标签"),
                             gr.Textbox(label='建议', info="多一丝关怀，多一份温暖")],
                    description="传入单图进行检测"
                    )
# tags2的输入、输出，以及对应处理函数
app2 = gr.Interface(fn=fall_detection,
                    # inputs=gr.inputs.Image(type="pil", label="上传单张图片"),
                    inputs=gr.components.Image(type="pil", label="上传单张图片"),
                    outputs=[gr.Image(label='检测照片'), gr.Label(num_top_classes=7, label="输出：判断是否跌倒")],
                    description="本案例适用于监控监管等远距离检测，可多人检测"
                    )
# tags3的输入、输出，以及对应处理函数
app3 = gr.Interface(fn=take_video,
                    # inputs=gr.Video(sources=["upload", "webcam"], label="上传MP4视频"),
                    inputs=gr.Video(label="上传MP4视频"),
                    # outputs=gr.Markdown(label="Labels"),
                    outputs=gr.Label(label="检测结果"),
                    # output_interface = [gr.Video(label="输出视频",show_download_button=True),gr.Video(label="输出视频",show_download_button=True,format='mp4')],
                    description="可进行视频分析识别，自动筛选处理，保障人身安全")
# examples=[["211.jpg"]])
# tags4的输入、输出，以及对应处理函数
app4 = gr.Interface(fn=process_image,
                    inputs=[gr.Image(label="摄像头", source="webcam", streaming=True),
                            gr.Radio(type='value', label="模式选择", choices=['情感守护', '跌倒防护'],
                                     value='情感守护')],
                    outputs=[gr.Image(label='检测照片'), gr.Label(label='检测结果'),
                             gr.Textbox(label='建议', info="一切有我们！")],
                    description="点击提交实时在线检测，点一次检测一次(请授权摄像头)")
# examples 应该是包含实际图像数据的列表，而不是文件名
# 这里省略，因为我们已经使用了streaming webcam
app5 = gr.Interface(
    fn=chatbot_response,
    inputs=gr.Textbox(label="请输入问题/随意聊天:"),
    outputs=gr.Textbox(label="聊天助手的回复:", value=""),
    description="实时在线的心灵慰藉平台",
)

# 创建Gradio界面
app6 = gr.Interface(
    fn=process_audio,  # 处理函数
    inputs=gr.Audio(source="microphone", type="numpy", streaming=True),  # 麦克风输入组件
    outputs="text",  # 输出为文本类型
    title="请说一句话吧！")  # 界面标题

# 使用gradio创建Web界面
iface = gr.TabbedInterface(
    [app1, app2, app3, app4, app5, app6],
    tab_names=["情感守护", "跌倒防护", "视频分析", "实时检测", "关怀树屋", "语音陪伴"],
    title="时光链守护专家",
    css=css
)

iface.queue()  # <-- Sets up a queue with default parameters

# iface.launch(share=False, show_error=True, server_name="127.0.0.1", show_api=False, quiet=True, inbrowser=True, auth=("admin", "pass1234"))
iface.launch(share=False,
             show_error=True,
             show_api=False,
             debug=False,
             server_name='0.0.0.0',
             server_port=5035,
             quiet=True,
             inbrowser=False,
             ssl_keyfile=r'localhost-key.pem',
             ssl_certfile=r'localhost.pem',
             ssl_verify=False)
