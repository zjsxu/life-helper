# 快速启动指南

## 第一次使用

### 1. 检查 Python 版本

```bash
python --version
```

应该显示 Python 3.8 或更高版本。

### 2. 安装依赖

```bash
pip install pyyaml
```

### 3. 启动 GUI

**在项目根目录运行：**

```bash
python run_gui.py
```

就这么简单！

---

## 使用 GUI

### 输入数据

1. **未来14天的固定截止日期数量**
   - 例如：4（表示有4个不可移动的截止日期）

2. **当前高负荷生活领域数量**
   - 例如：3（表示有3个需要高认知负荷的领域）
   - 包括：工作项目、家庭危机、健康问题等

3. **最近3天的能量评分**
   - 每天评分 1-5 分
   - 1 = 精疲力竭，5 = 精力充沛
   - 例如：2, 3, 2

### 点击"评估状态"

系统会显示：
- 当前状态（正常/压力/过载）
- 状态原因
- 行为建议（如果需要）
- 恢复状态

---

## 常见问题

### Q: 启动时出现 "ModuleNotFoundError"

**A:** 确保在项目根目录运行：

```bash
# 进入项目目录
cd /path/to/life-planner

# 然后启动
python run_gui.py
```

### Q: GUI 窗口无法打开

**A:** 测试 Tkinter 是否安装：

```bash
python -c "import tkinter; print('OK')"
```

如果出错，安装 Tkinter：
- macOS: `brew install python-tk`
- Ubuntu: `sudo apt-get install python3-tk`

### Q: 多久使用一次？

**A:** 推荐每周使用一次（例如每周日晚上），不是每天。

---

## 命令行模式

如果你更喜欢命令行：

```bash
python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
```

---

## 自定义配置

编辑 `config.yaml` 文件可以修改：
- 状态判断的阈值
- 行为规则
- 恢复条件

---

## 需要帮助？

查看完整文档：
- [README_CN.md](README_CN.md) - 完整项目文档
- [GUI_GUIDE.md](GUI_GUIDE.md) - GUI 详细指南
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - 使用示例

---

## 快速示例

### 示例 1：正常状态

输入：
- 截止日期: 1
- 高负荷领域: 1
- 能量: 4, 5, 4

结果：正常状态 ✅

### 示例 2：过载状态

输入：
- 截止日期: 4
- 高负荷领域: 3
- 能量: 2, 3, 2

结果：过载状态 🔴
建议：严格遵守降级规则

---

开始使用吧！记住：每周评估一次，保持简单。
