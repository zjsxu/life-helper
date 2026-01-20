# 使用示例

## GUI 模式示例

### 启动 GUI

```bash
python run_gui.py
```

### 场景 1：正常状态

**输入：**
- 未来14天的固定截止日期数量: `1`
- 当前高负荷生活领域数量: `1`
- 最近3天的能量评分: `4`, `5`, `4`

**预期输出：**
```
当前状态: 正常 (NORMAL)
原因: 无过载条件满足

恢复状态: 已就绪 ✓
所有恢复条件满足。可以安全返回正常模式。
```

**建议行动：**
- ✅ 可以正常进行活动
- ✅ 有能力接受新项目
- ✅ 保持当前节奏

---

### 场景 2：压力状态

**输入：**
- 未来14天的固定截止日期数量: `3`
- 当前高负荷生活领域数量: `1`
- 最近3天的能量评分: `4`, `4`, `3`

**预期输出：**
```
当前状态: 压力 (STRESSED)
原因: 1 条件满足:
  • 固定截止日期 (3) >= 阈值 (3)

激活的行为规则:
  • 警告: 接近过载
  • 不建议新项目
  • 建议创建时间缓冲

恢复状态: 未就绪 ✗
恢复未就绪。阻塞条件:
  • 固定截止日期 (3) > 恢复阈值 (1)
  • 平均能量 (3.7) < 恢复阈值 (4)
```

**建议行动：**
- ⚠️ 谨慎对待新承诺
- ⚠️ 为现有任务创建时间缓冲
- ⚠️ 注意能量水平
- ⚠️ 考虑推迟非紧急事项

---

### 场景 3：过载状态

**输入：**
- 未来14天的固定截止日期数量: `4`
- 当前高负荷生活领域数量: `3`
- 最近3天的能量评分: `2`, `3`, `2`

**预期输出：**
```
当前状态: 过载 (OVERLOADED)
原因: 2 条件满足:
  • 固定截止日期 (4) >= 阈值 (3)
  • 高负荷领域 (3) >= 阈值 (3)

激活的行为规则:
  • 不接受新承诺
  • 暂停技术工具开发
  • 创意工作减少到最低限度
  • 行政工作：仅处理不可委托的任务

恢复状态: 未就绪 ✗
恢复未就绪。阻塞条件:
  • 固定截止日期 (4) > 恢复阈值 (1)
  • 高负荷领域 (3) > 恢复阈值 (2)
  • 平均能量 (2.3) < 恢复阈值 (4)
```

**建议行动：**
- 🛑 **严格遵守所有降级规则**
- 🛑 对所有新承诺说"不"
- 🛑 暂停非必要项目
- 🛑 只做不可委托的任务
- 🛑 优先休息和恢复

---

## CLI 模式示例

### 场景 1：使用命令行参数

```bash
python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
```

**输出：**
```
=== Personal Decision-Support System ===

Current State: OVERLOADED
Reason: 2 conditions met:
  • Fixed deadlines (4) >= threshold (3)
  • High-load domains (3) >= threshold (3)

Active Rules:
  • No new commitments
  • Pause technical tool development
  • Creative work reduced to minimum viable expression
  • Administrative work: only non-delegable tasks

Recovery Status: Not ready
Recovery not ready. Blocking conditions:
  • Fixed deadlines (4) > recovery threshold (1)
  • High-load domains (3) > recovery threshold (2)
  • Average energy (2.3) < recovery threshold (4)
```

---

### 场景 2：交互式输入

```bash
python -m pl_dss.main
```

**交互过程：**
```
Enter fixed deadlines in next 14 days: 1
Enter active high-load domains: 1
Enter energy scores for last 3 days (space-separated, 1-5): 4 5 4
```

**输出：**
```
=== Personal Decision-Support System ===

Current State: NORMAL
Reason: No overload conditions met

Recovery Status: Ready
All recovery conditions met. Safe to return to NORMAL mode.
```

---

### 场景 3：错误处理

**无效的能量评分：**
```bash
python -m pl_dss.main --deadlines 2 --domains 1 --energy 6 3 2
```

**输出：**
```
ERROR: Energy score out of range
Details: Score at position 0 is 6
Expected: Energy scores must be 3 integers between 1 and 5
```

---

## 自动化脚本示例

### 每周自动评估脚本

创建文件 `weekly_check.sh`:

```bash
#!/bin/bash

# 每周自动评估脚本
# 使用 cron 在每周日 20:00 运行

echo "=== Weekly PL-DSS Check - $(date) ===" >> weekly_log.txt

# 提示用户输入
echo "Please enter your data for this week:"
read -p "Fixed deadlines (0-20): " deadlines
read -p "High-load domains (0-20): " domains
read -p "Energy scores (3 numbers, 1-5): " energy

# 运行评估
python -m pl_dss.main --deadlines $deadlines --domains $domains --energy $energy >> weekly_log.txt

echo "" >> weekly_log.txt
```

使用方法：
```bash
chmod +x weekly_check.sh
./weekly_check.sh
```

---

### Python 自动化示例

```python
#!/usr/bin/env python3
"""
自动化评估示例
"""

from pl_dss.config import load_config
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.recovery import check_recovery

def automated_check(deadlines, domains, energy_scores):
    """执行自动化评估"""
    
    # 加载配置
    config = load_config()
    
    # 创建输入
    inputs = StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=energy_scores
    )
    
    # 评估状态
    state_result = evaluate_state(inputs, config)
    rules_result = get_active_rules(state_result.state, config)
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    # 返回结果
    return {
        'state': state_result.state,
        'explanation': state_result.explanation,
        'rules': rules_result.active_rules,
        'can_recover': recovery_result.can_recover
    }

# 使用示例
if __name__ == "__main__":
    result = automated_check(
        deadlines=4,
        domains=3,
        energy_scores=[2, 3, 2]
    )
    
    print(f"State: {result['state']}")
    print(f"Can recover: {result['can_recover']}")
    
    if result['rules']:
        print("\nActive rules:")
        for rule in result['rules']:
            print(f"  - {rule}")
```

---

## 配置自定义示例

### 修改阈值

编辑 `config.yaml`:

```yaml
thresholds:
  overload:
    fixed_deadlines_14d: 4      # 改为 4（更宽松）
    active_high_load_domains: 4  # 改为 4（更宽松）
    avg_energy_score: 2          # 保持 2
  
  recovery:
    fixed_deadlines_14d: 0       # 改为 0（更严格）
    active_high_load_domains: 1  # 改为 1（更严格）
    avg_energy_score: 4          # 保持 4
```

### 自定义规则

编辑 `config.yaml`:

```yaml
downgrade_rules:
  OVERLOADED:
    - "立即停止所有新项目"
    - "每天工作不超过6小时"
    - "取消所有非必要会议"
    - "委托所有可委托的任务"
  
  STRESSED:
    - "本周不接受新任务"
    - "每天留出1小时缓冲时间"
    - "优先处理高优先级任务"
```

---

## 常见使用模式

### 模式 1：每周日晚上检查

1. 打开 GUI：`python run_gui.py`
2. 回顾本周情况
3. 输入数据
4. 查看评估结果
5. 根据建议调整下周计划

### 模式 2：项目启动前评估

在接受新项目前：
1. 运行评估
2. 如果是 NORMAL：可以接受
3. 如果是 STRESSED：谨慎考虑
4. 如果是 OVERLOADED：拒绝

### 模式 3：每日快速检查（不推荐）

虽然设计为每周使用，但如果需要每日检查：
```bash
# 创建别名
alias plcheck='python -m pl_dss.main'

# 快速检查
plcheck --deadlines 3 --domains 2 --energy 3 3 4
```

**注意：** 每日使用可能导致过度关注，违背工具的设计初衷。

---

## 故障排除示例

### 问题：GUI 无法启动

**测试 Tkinter：**
```bash
python -c "import tkinter; tkinter.Tk()"
```

如果出错，安装 Tkinter：
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk

# Windows
# Tkinter 通常随 Python 安装
```

### 问题：配置文件错误

**验证配置：**
```bash
python -c "from pl_dss.config import load_config; print(load_config())"
```

### 问题：输入验证失败

**测试输入验证：**
```python
from pl_dss.evaluator import StateInputs

# 有效输入
inputs = StateInputs(
    fixed_deadlines_14d=3,
    active_high_load_domains=2,
    energy_scores_last_3_days=[3, 4, 3]
)
print("Valid input created")

# 无效输入（会抛出异常）
try:
    inputs = StateInputs(
        fixed_deadlines_14d=3,
        active_high_load_domains=2,
        energy_scores_last_3_days=[6, 4, 3]  # 6 超出范围
    )
except Exception as e:
    print(f"Validation error: {e}")
```

---

## 总结

- **GUI 模式**：适合日常使用，直观友好
- **CLI 模式**：适合自动化和脚本
- **配置文件**：灵活自定义阈值和规则
- **每周使用**：推荐的使用频率
- **状态驱动**：根据评估结果调整行为

选择适合你的使用方式，保持简单，避免过度使用！
