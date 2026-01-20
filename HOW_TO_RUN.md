# 如何运行 PL-DSS

## 三种启动方式

### 方式 1：使用启动脚本（推荐）✅

```bash
python run_gui.py
```

**优点：**
- 最简单
- 自动处理路径问题
- 有错误提示

---

### 方式 2：使用模块方式

```bash
python -m pl_dss.gui
```

**优点：**
- 标准 Python 模块调用
- 适合脚本集成

---

### 方式 3：命令行模式

```bash
python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
```

**优点：**
- 快速评估
- 适合自动化
- 可脚本化

---

## 重要提示 ⚠️

### ✅ 正确的做法

```bash
# 1. 进入项目根目录
cd /path/to/life-planner

# 2. 运行启动脚本
python run_gui.py
```

### ❌ 错误的做法

```bash
# 不要直接运行 gui.py 文件
python pl_dss/gui.py  # ❌ 会报错

# 不要在其他目录运行
cd /some/other/directory
python /path/to/life-planner/run_gui.py  # ❌ 可能出问题
```

---

## 故障排除

### 问题 1：ModuleNotFoundError: No module named 'pl_dss'

**原因：** 不在项目根目录

**解决：**
```bash
cd /path/to/life-planner
python run_gui.py
```

---

### 问题 2：GUI 窗口不显示

**原因：** Tkinter 未安装

**解决：**
```bash
# 测试 Tkinter
python -c "import tkinter"

# macOS 安装
brew install python-tk

# Ubuntu 安装
sudo apt-get install python3-tk
```

---

### 问题 3：配置文件错误

**原因：** config.yaml 格式错误或缺失

**解决：**
```bash
# 检查配置文件是否存在
ls config.yaml

# 验证配置
python -c "from pl_dss.config import load_config; load_config()"
```

---

## 快速测试

运行以下命令测试系统是否正常：

```bash
# 测试 CLI
python -m pl_dss.main --deadlines 1 --domains 1 --energy 4 5 4

# 测试 GUI 导入
python -c "from pl_dss.gui import main; print('GUI OK')"

# 运行测试套件
pytest -v
```

---

## 目录结构检查

确保你的目录结构如下：

```
life-planner/          ← 你应该在这里
├── pl_dss/
│   ├── __init__.py
│   ├── gui.py
│   ├── main.py
│   ├── config.py
│   ├── evaluator.py
│   ├── rules.py
│   └── recovery.py
├── config.yaml
├── run_gui.py         ← 运行这个文件
└── README.md
```

---

## 环境要求

- Python 3.8+
- PyYAML
- Tkinter（通常随 Python 安装）

安装依赖：
```bash
pip install pyyaml
```

---

## 成功启动的标志

当你运行 `python run_gui.py` 后，应该看到：

1. 一个窗口弹出
2. 标题显示"个人决策支持系统 (PL-DSS)"
3. 有输入框和评估按钮
4. 没有错误消息

如果看到以上内容，恭喜！系统运行正常。

---

## 需要更多帮助？

- [QUICKSTART_CN.md](QUICKSTART_CN.md) - 快速启动指南
- [GUI_GUIDE.md](GUI_GUIDE.md) - GUI 详细使用说明
- [README_CN.md](README_CN.md) - 完整项目文档
