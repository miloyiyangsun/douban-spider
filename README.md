# 📚 豆瓣书评采集器

⚡ 快速获取豆瓣图书短评数据 

<img width="191" alt="image" src="https://github.com/user-attachments/assets/d24e3291-a160-4cc5-92f7-e2b7e7dcf2c3" />

<img width="575" alt="image" src="https://github.com/user-attachments/assets/6c5bfe29-e4c6-4a6e-8771-31b718d0c6b1" />


## 🌟 核心功能

🔍 智能书籍 ID 搜索 → 支持书名模糊匹配
📊 多维度数据采集 → 用户/评分/内容/点赞/时间
💾 自动生成 CSV → 兼容 Excel 中文显示
⏱️ 智能反爬策略 → 随机延迟+请求头模拟

## 🚀 快速开始

```bash
# 安装依赖
pip install requests beautifulsoup4

# 运行脚本（使用相对路径）
python3 ./douban_spider.py
```

## 📂 文件结构

```
.
├── douban_spider.py    # 主程序
├── data/               # 自动创建的存储目录
└── README.md
```

## 🛠️ 技术亮点

▸ 双引擎 ID 搜索：直接匹配 + 跳转链接解析

▸ 智能分页控制：默认 10 页（约 200 条）

▸ 抗封禁策略：2-5 秒随机请求间隔

## ⚠️ 注意事项

首次使用需安装上述两个依赖
豆瓣限制未登录用户查看评论页数
高频访问可能导致 IP 暂时封禁



