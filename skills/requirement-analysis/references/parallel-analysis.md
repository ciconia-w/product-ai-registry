# 并行分析建议

分析阶段通常是全流程里最耗时、最复杂的一段，尤其当样本量变大、且需要按原始 `requirement-analysis` 框架输出多维度结果时。

建议的并行策略：

1. 采集与合并仍保持单线程，确保输入唯一真源稳定。
2. 在 `merged.json` 产出后，按固定批次切分：
   - 例如每 `5` 条或 `10` 条一批
   - 可直接运行：

```bash
python3 scripts/run-parallel-analysis.py \
  --input outputs/merged.json \
  --output-dir outputs/batches \
  --batch-size 5
```

执行后会生成 `parallel_plan.json`，里面列出每个批次推荐的输入与输出路径。
3. 每个子 agent 只负责：
   - 一批需求的标准化
   - 需求穿透分析
   - 当前能力判断
   - 聚类 / 优先级 / 初步模块归属
   - 输出一份局部 `report fragment` 与 `delivery fragment`
   - 推荐直接运行：

```bash
python3 scripts/analyze-batch.py \
  --input outputs/batches/batch_01.json \
  --report-output outputs/batches/batch_01_report.md \
  --delivery-output outputs/batches/batch_01_delivery.json
```
4. 主 agent 负责：
   - 合并所有局部输出
   - 做竞品 / 标准 / 报告总览层汇总
   - 执行 `finalize-delivery.py`
   - 决定哪些外语条目需要翻译
   - 写飞书

合并子批次输出时可运行：

```bash
python3 scripts/merge-analysis-fragments.py \
  --delivery-output outputs/delivery_merged.json \
  --report-output outputs/report_merged.md \
  outputs/batch_01_delivery.json \
  outputs/batch_02_delivery.json
```

输出格式要求见 `references/batch-contract.md`

这样做的好处：

- 子 agent 的上下文更小，单批分析更稳定
- 总体吞吐更高
- 最终仍由主 agent 统一把关，不会出现多份风格冲突的终稿

适用条件：

- 样本量较大
- 用户要求高维度完整分析
- 允许多 agent 协同

不适用条件：

- 只有 1~3 条样本
- 只是快速验证流程是否可跑
- 当前阶段重点是联调权限、写入和表头，而不是深度分析
