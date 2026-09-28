---
title: "一切皆可评测：DSH 三个硬细节 × 六篇论文，给评测管线的实战清单"
subtitle: "把 Hugo Zhu 的 DSH 三细节文章与六篇论文精读笔记，揉成一份日常工作清单"
date: 2026-09-28
tags: ["agent", "评测", "DeepSeek-Harness", "论文笔记"]
---

> 来源说明：本文把 Hugo Zhu 的《一切皆插件：DeepSeek Harness 真正硬核的是三个细节》（https://hugozhu.site/post/2026/348-dsh-three-details-reversible-effects/）与我近两周采集的六篇论文笔记揉在一起——DSec（arXiv:2609.22978）§1 中英对照精读、CodeAssay（arXiv:2608.03535）与 CCTU（arXiv:2603.15309）中文精读、GAUGE（arXiv:2609.12191）精读、Efficient Benchmarking in Production（arXiv:2609.21267）与 How Do Agent Harnesses Create Value?（arXiv:2609.20474）每日进修精简版。目标只有一个：落到算法评测的日常工作——评测链路搭建和线上问题追踪分析——能直接抄作业。

---

## 一、DSH 三个细节速览（先对齐上下文）

**细节一：注册即副作用，卸载即回滚。** 插件每注册一个能力（注册工具、监听事件、挂路由），同时登记一个对应的清理动作；卸载或重载时一起撤销。官方原话：*registrations are effects that unwind when their plugin unloads*。原文点评：**可替换是口号，可回滚才是能力。**

**细节二：模型看见的一切，必须能在日志里找到。** Session 不是聊天记录，是**仅追加的事件日志**（append-only event log）：模型可见的所有消息都从这份日志推导，工具调用、工具结果、流式 chunk 全部写回同一处。每轮还写入 request header 快照——供应商、模型名、思考强度、系统提示词、工具目录。一份日志解决五件事：恢复、分叉、回放、检索、审计。硬原则：上下文压缩、截断、摘要，任何对历史的加工如果不可回溯，恢复出来的 Agent 就不再是原来那个 Agent。

**细节三：工具可以乱序完成，写回必须按原序。** 模型一次吐出多个工具调用，允许并行的先进并行池（默认上限 10），但写回模型的结果仍按最初调用顺序排列——因为同一轮上下文是模型的推理基础，顺序抖动不会报错，只会让后续推理悄悄变味。任务取消时，已启动的尽量收尾，来不及启动的写合成结果，日志里永远不凭空少半截工具链。

**附带的安全提醒：插件是宿主代码。** 三档权限（只读 / 工作区可写 / 完全访问）管的是模型行为；但装进 Profile 的第三方插件不经过沙箱，权限接近 dsh 进程本身，要按"即将在你机器上以你权限运行的程序"来审查。`web_fetch` 默认关闭、创造模式≈给 Agent Shell 权限，都是官方警惕的信号。

**原文的使用建议：** 现阶段最大价值是学习不是日常使用——可逆副作用怎么设计、事件日志怎么做脊柱、上下文三道控制线怎么省 token，答案都能抄。一轮 14 步任务缓存命中率 93% 是实测参考。

---

## 二、为什么评测工程师要读这三个细节

原文最后一句值得单独拎出来：**一个 Agent 运行时的可靠性，不体现在它跑得起来，而体现在它被打断、被替换、被取消之后，状态依然自洽。**

这句话换到评测语境里几乎不用改：**一条评测链路的可靠性，不体现在它跑得通，而体现在它被插桩、被并行、被中断之后，结论依然可信。** 我们日常工作的一大半——线上问题追踪、回归对比、benchmark 迭代——本质上都是在跟"状态不自洽"打架。三个细节恰好对应评测管线的三个经典病：

| DSH 细节 | 评测管线的对应病 |
|---|---|
| 注册不回滚 → 旧工具残留、监听器叠加、行为漂移 | 评测插桩（mock、judge、打点）污染基线，A/B 对比的其实是"两个不同的系统" |
| 模型所见不可回溯 → 恢复的 Agent 活在另一份历史里 | 回归时压缩/截断后的上下文不可复现，"退步 2 个点"可能是换了历史，不是换了模型 |
| 写回乱序 → 因果链抖动，推理悄悄变味 | 并行评测、异步 judge 的结果写回顺序错乱，结论偏差不报错、只潜伏 |

---

## 三、六篇论文笔记 × 三个细节：能对上号的证据

### 3.1 细节二（事件日志做脊柱）是最值得抄的

- **DSec（DeepSeek Elastic Compute，arXiv:2609.22978）**：这篇讲 agent 训练沙箱基础设施的论文，正文**明确引用了 DeepSeek Harness**。它列出的 7 类平台约束——突发式创建、高密度运行、有状态长存活、高度异构、环境多样性高、agent 执行不可信、执行可中断——每一条都是线上问题追踪的日常。DSec 的存在本身说明：没有可回放、可审计的执行日志，"agent 执行不可信"这条约束根本无解。
- **GAUGE（arXiv:2609.12191，Amazon，EMNLP 2026 Industry Track）**：25 个 agent（6 家厂商）× 约 3,700 会话的实证。离线评测的"排序"整体可靠（与可验证奖励 Spearman ρ=0.94），但"满意度"与"任务成功"彻底脱钩——人评"满意"的会话里 57.5% 实际失败（ρ=−0.147）。教训：**把"排序有效性"和"构念有效性"分开审计**。落到日志上就是：你记录的到底是"模型做对了什么"（可验证事件），还是"人觉得好不好"（主观信号）？两者要分开落盘、分开审计，混在一起的日志，回放出来也是混的。
- **Efficient Benchmarking in Production（arXiv:2609.21267，Meta/CMU）**：生产 agent 持续评测，52 天 574 runs 的实证，对比"难度分层固定子集"与"IRT 自适应测试"两种降本路线。持续评测的前提是每一次 run 的 trajectory 可复现、可对比——没有细节二那种"request header 快照 + 仅追加日志"，持续评测退化成"每周跑一遍、数字随缘"。*（完整精读按计划留到下周，本文先用每日进修精简版结论。）*

### 3.2 细节一（可回滚）对应评测插桩的卫生

- **How Do Agent Harnesses Create Value?（arXiv:2609.20474，CUHK/Edinburgh）**：在 τ²-bench 上做 Fixed vs Sham 规划对照，规划这层 harness 带来 **+7.17pp**；更关键的是**终端校验器拦截了 61% 的 false-pass**，成本 **<$0.01/episode**。这正是"注册即副作用"的评测版：校验器作为可插拔、可卸载的一层挂在管线末端——挂上时拦截假通过，摘掉时不留残留、不污染基线分数。结论很实用：**judge 之后再加一道硬规则校验器，又便宜又有效**，而且它应该是可逆的实验层，不是焊死在管线里的祖传逻辑。
- **CodeAssay（arXiv:2608.03535）**：185 个 Python 任务，真值审计后 1,890 个固定输出里 170 个正确性标签翻转（**9.0%**），模型最好与最差的差距从 11.9 拉到 23.7 个百分点。可直接抄的三件套：**ground truth 审计、公开/隐藏测试隔离、mutation testing**（完整/隐藏测试的 mutation score 分别为 82.6%/74.8%）。对应到细节一：题库本身也是"注册进系统"的东西——没审计过的题库就像没清理动作的插件，悄悄污染你所有的结论。

### 3.3 细节三（按序写回）对应评测的因果卫生

- **CCTU（arXiv:2603.15309）**：200 个复杂工具调用案例，12 类约束分属资源/行为/工具集/响应四维，平均每例 7 类约束、上下文约 4,754 token。九个模型**严格无违规完成率全部低于 20%**，所有模型在超 50% 案例中出现约束违规。它的方法论贡献正是"顺序敏感"的：**把"最终完成"（SR）与"全程无违规"（PSR）拆成两个指标，并逐步记录约束状态和纠错成功率**。这跟 DSH"写回按原序"是同一个哲学：**过程的顺序和中间态是结论的一部分**，只看终态的评测会漏掉"成功了但违规了"这类线上最常见的中间态——而线上问题追踪恰恰主要跟中间态打交道。

### 3.4 安全节（插件是宿主代码）对应线上 agent 治理

DSec 的七约束里有"agent 执行不可信"和"执行可中断"，DSH 原文提醒"模型在笼子里，不代表装插件的手也在笼子里"。合在一起就是线上 agent 的治理 checklist：沙箱管模型行为（DSH 三档权限 + 逐次审批），**代码审查管插件/工具行为**（按宿主代码标准审安装脚本、依赖和 Host 代码），两者缺一不可。日常更稳的起点：工作区可写 + 逐次审批。

---

## 四、落到日常工作的清单（按"今天就能做"排序）

1. **把这句话写进管线评审清单**："模型看见的东西，必须能回到日志里找到。" 任何上下文加工（压缩、截断、摘要）上线前先回答：加工可逆吗？回放时能重建模型当时看到的内容吗？
2. **Trajectory 日志升格为评测脊柱**：每次 run 落盘 request header 快照（模型、系统提示词、工具目录、思考强度等）+ 仅追加事件流。这是线上问题追踪的"第一现场"，也是回归可信的前提。
3. **评测插桩也要"注册即副作用"**：mock、judge、打点代码随实验卸载而回滚；做 A/B 前先确认基线没被历史实验污染。
4. **题库先审计再卷模型**（CodeAssay）：9% 的标签翻转率说明，真值不审计，模型排名可能只是在给脏题库打工。公开/隐藏测试隔离 + mutation score 做题库健康度指标。
5. **指标拆分：SR 与 PSR 分开报**（CCTU）：任务成功率之外，单独报"全程无违规率"。九个模型严格无违规完成率均 <20%——线上要的恰恰是这个视角。
6. **CI 里放零成本 tripwire**（GAUGE）：completion bit 与可验证奖励 ρ=0.87，优于付费 judge 的 0.80——先用它做回归截断，贵 judge 只用在可疑 case 上。实力接近的 pair 差距在采样噪声内就弃权（误判率 31% → 14.8%）。
7. **评测末端加终端校验器**（Harnesses Create Value）：硬规则拦截 61% false-pass，成本 <$0.01/episode。judge 之后永远再过一道确定性校验。
8. **持续评测降本二选一**（Efficient Benchmarking）：难度分层固定子集 vs IRT 自适应测试，52 天 574 runs 实证在前——完整精读下周补上后再定用哪条。
9. **并行评测的写回顺序**（DSH 细节三）：异步 judge、多并发 run 的结果写回保持调用原序；顺序抖动不报错、只让结论悄悄变味，review 时重点看这一层。
10. **插件/工具按宿主代码审查**：线上 agent 的工具与插件变更，走"即将在我机器上以我权限运行"的审查标准；日常用工作区可写 + 逐次审批。

---

## 五、关键术语中英对照（结合论文翻译）

| 中文 | 英文 |
|---|---|
| 注册即副作用 / 可逆副作用 | registrations are effects that unwind / reversible effects |
| 仅追加事件日志 | append-only event log |
| 请求头快照 | request header snapshot |
| 恢复 / 分叉 / 回放 | resume / fork / replay |
| 校准弃权 | calibrated abstention |
| 变异分数 | mutation score |
| 真值审计 | ground truth audit |
| 假通过 | false-pass |
| 终端校验器 | terminal verifier |
| 完成位（零成本截断信号） | completion bit |
| 难度分层固定子集 / IRT 自适应测试 | difficulty-stratified fixed subset / IRT adaptive testing |
| 约束违规 | constraint violation |
| 排序有效性 / 构念有效性 | ranking validity / construct validity |

---

## 附：论文与文章来源

- Hugo Zhu《一切皆插件：DeepSeek Harness 真正硬核的是三个细节》https://hugozhu.site/post/2026/348-dsh-three-details-reversible-effects/
- DeepSeek《DeepSeek Elastic Compute (DSec): A Sandbox Infrastructure for Effective Agentic Training at Scale》arXiv:2609.22978（§1 中英对照精读已入库 daily-notes）
- Amazon《GAUGE: When Not to Trust LLM-as-a-Judge in User-Simulated Evaluation of Task-Oriented Agents》arXiv:2609.12191（精读已入库 daily-notes）
- 《CodeAssay: A Multi-Metric Benchmark with Audited Ground Truth for LLM Code Generation》arXiv:2608.03535（中文精读）
- 《CCTU: A Benchmark for Tool Use under Complex Constraints》arXiv:2603.15309（中文精读）
- Meta/CMU《Efficient Benchmarking in Production》arXiv:2609.21267（精简版；完整精读待下周）
- CUHK/Edinburgh《How Do Agent Harnesses Create Value?》arXiv:2609.20474（精简版）
