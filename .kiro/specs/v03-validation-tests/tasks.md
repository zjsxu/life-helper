# Implementation Plan: v0.3 验证测试套件

## Overview

实现 5 个核心维度的验证测试：Decision Core、Authority、Containment、L1 Advisory、Safety Boundary。

## Tasks

- [x] 1. 创建测试文件和基础设施
  - 创建 tests/test_v03_validation.py
  - 设置 pytest fixtures 和辅助函数
  - _Requirements: 6.1_

- [x] 2. 实现 Dimension 1: Decision Core 测试
  - [x] 2.1 实现状态判定测试
    - 测试 OVERLOADED、STRESSED、NORMAL 状态判定
    - 测试判定理由完整性
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

  - [ ]* 2.2 编写属性测试：状态判定确定性
    - **Property 1: 相同输入产生相同判定**
    - **Validates: Requirements 1.4**

- [x] 3. 实现 Dimension 2: Authority 测试
  - [x] 3.1 实现权限派生测试
    - 测试 planning_permission 随状态变化
    - 测试 execution_permission 始终为 DENIED
    - 测试权限派生自 Decision_Core
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. 实现 Dimension 3: Containment 测试
  - [x] 4.1 实现拒绝行为测试
    - 测试规划被拒绝时的行为
    - 测试执行被拒绝时的行为
    - 测试拒绝消息的完整性
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 4.2 编写属性测试：拒绝一致性
    - **Property 2: 连续拒绝保持一致**
    - **Validates: Requirements 3.5**

- [x] 5. 实现 Dimension 4: L1 Advisory 测试
  - [x] 5.1 实现建议功能测试
    - 测试 ALLOWED 时提供建议
    - 测试 DENIED 时不提供建议
    - 测试建议语言非指令性
    - 测试输入数据不被修改
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 6. 实现 Dimension 5: Safety Boundary 测试
  - [x] 6.1 实现安全边界测试
    - 测试 execution_permission 始终为 DENIED
    - 测试 Advisory_Layer 不调用 Execution Layer
    - 测试权限派生自 Decision_Core
    - 测试无法绕过 Authority_System
    - 测试调用 Execution Layer 失败
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. 实现测试报告生成
  - [x] 7.1 实现维度测试结果输出
    - 为每个维度输出 PASS/FAIL
    - 输出失败详情
    - 输出通过率和总体摘要
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8. 实现 CLI 命令
  - [x] 8.1 添加 validate-v03 命令
    - 实现运行所有 v0.3 测试的命令
    - 实现按维度过滤的选项
    - 实现退出码处理（通过返回 0，失败返回非零）

- [x] 9. Final Checkpoint - 完整验证
  - 运行完整测试套件
  - 验证所有 5 个维度测试通过
  - 验证输出格式正确
  - 如有问题，询问用户

## Notes

- 标记 `*` 的任务是可选的属性测试任务
- 每个任务都引用了具体的需求
- 测试应该简洁明了，直接验证 5 个核心维度
