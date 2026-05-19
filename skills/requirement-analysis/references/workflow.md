# 工作流

标准顺序必须是：

1. 检查依赖与授权
2. 检查飞书表头
3. 采集原始需求
4. 合并原始数据
5. 生成分析报告与基础交付 JSON
6. `finalize-delivery.py` 补链接、检测非中文、生成翻译队列
7. 如果存在翻译队列，先由 agent 生成 `translations.json`，再重新执行 finalize
8. 确认 `K/L/M` 三列完整
9. 写入飞书
10. 只有在以上都通过后，才允许打包、入 registry、产出 showcase

全流程入口：

```bash
python3 scripts/run-full-workflow.py --days 7 --forum-max 10 --feedback-max 10 --deepin-home-page-size 10 --deepin-home-pages 1
```

如果流程在 finalize 阶段退出并提示存在翻译队列：

```bash
python3 scripts/finalize-delivery.py \
  --input outputs/delivery.json \
  --output outputs/delivery_final.json \
  --translation-queue outputs/translation_queue.json
```

然后由 agent 根据 `translations.example.json` 生成 `translations.json`，再执行：

```bash
python3 scripts/finalize-delivery.py \
  --input outputs/delivery.json \
  --output outputs/delivery_final.json \
  --translation-queue outputs/translation_queue.json \
  --translations outputs/translations.json
```
