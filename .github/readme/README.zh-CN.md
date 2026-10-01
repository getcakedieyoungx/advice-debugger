<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>你的 AI 给你建议，却永远不知道建议是否奏效。<br/>现在它知道了。</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="许可证"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="测试"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="零依赖">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="在 Patreon 上支持"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.tr.md" title="土耳其语">🇹🇷</a> ·
  <a href="README.es.md" title="西班牙语">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="葡萄牙语（巴西）">🇧🇷</a> ·
  <a href="README.de.md" title="德语">🇩🇪</a> ·
  <strong>🇨🇳</strong> ·
  <a href="README.ja.md" title="日语">🇯🇵</a>
</p>

## 安装

将以下内容粘贴到 Claude Code（或任何编程代理）中：

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

或者作为 Claude Code 插件安装：

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

更多选项见 [INSTALL.md](../../INSTALL.md)。

## 问题所在

代码有测试。修复出错时，会有东西变红。

建议什么都没有。你的助手告诉你“每天发帖”或“给 20 个人发冷邮件”，你照做了，却因为没人预料到的原因失败了，而下一周同一个助手会用不同的措辞给你同样的建议。它从未看到结果。

## 改变什么

### 一个习惯

<table>
<tr>
<td width="50%">

**之前**

> **你：** 我按你说的每天发帖。坚持了 3 天，然后放弃了。写内容不难，但每天都要决定写什么，把我耗尽了。
>
> **AI：** 坚持就是胜利！试试设置每日提醒、随时备好灵感清单，记住积少成多。哪怕发一小段也算。你可以的！💪

</td>
<td width="50%">

**之后**

> **AI：** 记录 #1 的结果。我们假设瓶颈是*写作*，结果发现是*每天决定写什么*。这个假设不成立，所以提醒解决不了问题。
>
> **试一周：** 每周日选 5 个主题，用 40 分钟一次性起草。工作日只发布草稿。
>
> **信号：** 7 天内发布 ≥5 篇。记录为 #2（修订 #1），10 月 8 日复查。

</td>
</tr>
</table>

### 一个代码库

<table>
<tr>
<td width="50%">

**之前**

> **你：** 两周前你让我把 `shared/` 拆成小包。现在几乎每个 PR 都会改动其中四个。
>
> **AI：** 模块化架构稳定之前这是正常的！加上 Turborepo 做缓存，用 ESLint 强制边界，再给它几周时间。会有回报的。🚀

</td>
<td width="50%">

**之后**

> **AI：** 没有靠猜，我对照 `git log` 里最近 14 个 PR 核对了 #5：
>
> ```diff
>   expected   ≤ 2 packages touched per PR
> - actual     4 per PR, pricing + checkout changed together in 11/14
> ```
>
> **A1 不成立：** “pricing 和 checkout 独立变更”。把这两个合并回一个包，保留其他拆分。
>
> **信号：** 接下来 10 个 PR 中每个 PR 涉及 ≤2 个包。记录为 #6（修订 #5）。

</td>
</tr>
</table>

#5 在台账中记录的内容：

```json
{
  "status": "failed",
  "actual": "Median PR touched 4 packages; pricing and checkout changed together in 11 of 14 PRs.",
  "gap": "expected <= 2 packages per PR, got 4",
  "verdicts": {
    "A1": { "verdict": "broke", "note": "pricing and checkout are one unit of change" },
    "A2": "held"
  },
  "lesson": "Splitting modules that change together multiplied the packages touched per PR.",
  "source": "git log, last 14 PRs"
}
```

## 工作原理

每一条可执行的建议都会变成本地台账中的一个小的、可证伪的实验：

1. **假设：** 这个建议要成立，需要哪些条件为真？其中一个标记为*关键*。
2. **预期结果：** 应该发生什么变化、哪个观察能证明它、以及截止时间。
3. **小实验：** 3–14 天，只测试关键假设，而不是一个月的计划。
4. **对比：** 当你反馈结果时，每个假设被标记为 `held`、`broke` 或 `untested`。之前遗漏的假设也会被记录下来。
5. **下一条建议：** 从被推翻的假设出发，并链接回旧条目。在回答之前，助手会对照每一条被推翻的假设检查自己的草稿，目的是阻止同样的建议换一种说法卷土重来。

台账在给出**新建议之前**会被检查，所以上个月实验的教训会塑造今天的回答。

当复查日期到来时，插件的会话启动钩子会提醒助手用一句话问你进展如何。没有到期事项时它保持沉默。

## 不给性格下结论

一次失败的实验永远不会变成“你缺乏自律”。教训被记录为**条件 + 结果**（“需要每天做新决定的日常习惯在第 3 天停滞了”），因为条件可以重新设计，而标签不能。

## 适用场景

| 领域 | 它能学到什么 |
|---|---|
| 学习 | 哪种学习方法真的能提高记忆？ |
| 商业 | 哪种获客渠道真的能带来回复？ |
| 软件 | 那次重构真的降低了维护成本吗？（git 历史会回答） |
| 规划 | 你的时间估算在哪些地方总是偏差？ |
| 内容 | 哪种创作节奏是你真正能持续下去的？ |

## 台账

纯 JSON 文件存放在 `~/.advice-ledger/`，外加一个可读的 `ledger.md`。一个 Python 脚本（仅用标准库）负责所有写入操作，带锁、校验和备份。参见[示例台账](../../examples/example-ledger.md)。

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**隐私：** 台账是本地文件，脚本不进行任何网络调用。你的助手读取的部分会像它打开的任何文件一样成为该对话的一部分。用 `ADVICE_LEDGER_DIR` 更改位置，用 `ADVICE_DEBUGGER_NO_HOOK=1` 关闭提醒钩子。

## 自定义

Fork 它，编辑 [`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md)，然后安装你的 fork。用 `python -m unittest discover -s tests` 运行测试。

## 支持

advice-debugger 是免费且 MIT 许可的。如果它帮你省去了一轮又一轮重复的建议，你可以在 [Patreon](https://www.patreon.com/monkeytax407) 上支持更多类似的工具。

## 许可证

[MIT](../../LICENSE)。

如果你的助手曾经把同一条失败的建议换着说法再给你一次，就给它点个 ⭐ 吧。
