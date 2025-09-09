### 结构

smart_reminder_agent/
├── main.py                  # 命令行入口（语义解析 + 任务记录）
├── modules/
│   ├── nlu.py               # 语义解析模块（调用 Qwen 模型）
│   ├── database.py          # SQLite 数据库操作
│   ├── tools.py             # 天气查询封装（和风天气）
│   └── markdown_logger.py   # Markdown 日志记录
├── .env                     # 环境变量配置
├── requirements.txt         # 项目依赖
└── README.md                # 项目说明

## 🚀 快速开始
1️⃣ 克隆项目
bash
git clone https://github.com/suianwu353/-agent.git
cd smart_reminder_agent
2️⃣ 创建虚拟环境并激活
bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux / WSL
.\venv\Scripts\activate       # Windows PowerShell
3️⃣ 安装依赖
bash
pip install -r requirements.txt