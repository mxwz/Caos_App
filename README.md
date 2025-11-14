# Chaos App (混沌新城)

一个基于 Flask 的综合 Web 应用平台，集成了用户管理、GPT聊天、地理位置服务等功能。

## 项目简介

混沌新城（Chaos App）是一个功能丰富的Web应用平台，致力于打造高效、便捷、多元化的智能生态系统。该项目使用 Flask 框架构建，包含了用户认证、权限管理、GPT聊天机器人、地理位置服务等模块。

### 主要特性

- **用户管理系统**：
  - 用户注册、登录、登出
  - 密码重置功能
  - 邮箱验证机制
  - 图形验证码保护
  - 角色权限控制（普通用户/管理员）

- **GPT聊天功能**：
  - 集成DeepSeek API
  - 支持流式响应
  - 对话历史记录保存
  - 支持深度思考模式（R1模型）

- **地理位置服务**：
  - 用户登录位置追踪
  - 高德地图API集成
  - 3D地图展示功能

- **内容管理**：
  - 评论系统（支持回复功能）
  - 个人信息管理
  - 后台管理系统

- **安全特性**：
  - Argon2/BCrypt密码加密
  - JWT Token认证
  - Session管理
  - XSS防护

## 技术栈

- **后端框架**：Flask
- **数据库**：SQLAlchemy (支持MySQL)
- **前端技术**：HTML/CSS/JavaScript, Jinja2模板
- **地图服务**：高德地图API
- **AI服务**：DeepSeek API
- **安全组件**：JWT, Argon2, Flask-Security
- **部署**：Docker支持

## 功能模块

### 1. 用户系统
- 用户注册、登录、登出
- 多种登录方式（用户名/邮箱）
- 密码找回功能
- 个人资料管理
- 用户角色权限控制

### 2. GPT聊天
- 实时聊天交互
- 流式消息显示
- 对话历史保存
- 支持深度推理模式

### 3. 地理位置服务
- 用户登录位置记录
- 经纬度坐标解析
- 地址逆向解析
- 3D地图可视化

### 4. 内容管理
- 评论与回复系统
- 信息发布
- 内容审核机制

### 5. 管理后台
- 用户管理
- 权限分配
- 活动监控
- 数据统计

## 安装与配置

### 环境要求
- Python 3.7+
- MySQL数据库
- 高德地图API密钥
- DeepSeek API密钥

### 安装步骤

1. 克隆项目代码：
```
bash
git clone <repository-url>
cd Caos_App
```
2. 安装依赖：
```
bash
pip install -r requirement.txt
```
3. 配置环境变量：
创建 `.env` 文件并配置以下参数：
```

MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
DEEPSEEK_KEY=your_deepseek_api_key
AMAP_KEY=your_amap_api_key
```
4. 数据库配置：
在 [config.py](file://Caos_App\app\Admin_config.py) 中配置数据库连接信息

5. 初始化数据库：
```
bash
flask db upgrade
```
6. 运行应用：
```
bash
python flasky.py
```

Caos_App/
├── app/                    # 主应用目录
│   ├── main/              # 主要业务逻辑
│   ├── chat/              # 聊天相关功能
│   ├── manage/            # 管理后台
│   ├── page/              # 页面相关
│   ├── static/            # 静态资源文件
│   ├── templates/         # HTML模板
│   ├── Models.py          # 数据模型
│   └── __init__.py        # 应用工厂
├── config/                # 配置文件
├── migrations/            # 数据库迁移文件
├── tests/                 # 测试文件
├── flasky.py             # 应用入口
├── requirement.txt       # 依赖包列表
└── docker-compose.yml    # Docker配置
```
## 安全说明

1. 密码使用 Argon2 或 BCrypt 进行哈希处理
2. 敏感操作需要邮箱验证码验证
3. Session 和 JWT Token 双重认证机制
4. 图形验证码防止自动化攻击
5. CORS 和 CSRF 保护

## 开发注意事项

1. 所有新功能应通过蓝图(Blueprint)方式进行模块化开发
2. 数据库模型变更需使用 Flask-Migrate 进行迁移
3. 敏感配置信息应通过环境变量或 .env 文件管理
4. 前端静态资源放置在 static 目录下对应子目录中
5. 模板文件应放在 templates 目录下的相应子目录中

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT

## 联系方式

项目维护者：深圳信息职业技术大学 hakanyang

## 致谢

- Flask框架
- DeepSeek AI
- 高德地图API
- 所有使用的开源库和工具
