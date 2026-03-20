# Cloud Agents Starter Skill（wechat2rss-opml）

## 什么时候用
- 你第一次接手这个仓库，需要**立刻跑通**“下载源数据 -> 校验 -> 转换 -> 产物检查”流程。
- 你需要在 Cloud Agent 中快速判断：这次改动是否破坏了 OPML 生成链路。

## 仓库速览（按代码区块）
- `scripts/validate_source.py`：校验 Markdown 源数据是否可用（分类、链接数量、链接格式）。
- `scripts/convert_to_opml.py`：把 Markdown 源数据转换为 `wechat2rss.opml`。
- `.github/workflows/convert-to-opml.yml`：CI 真实执行链路（下载 `all.md`、校验、转换、提交）。
- `wechat2rss.opml`：最终产物文件。

## 0) Cloud 运行前检查（登录/鉴权/环境）
> 这个仓库是离线脚本工具链，**没有 Web 登录页面、没有后端服务、没有 feature flags 系统**。  
> 这里的“登录/鉴权”主要是 GitHub 与 Git push 能力检查。

1. 检查 Python（CI 使用 3.11+）：
   - `python3 --version`
2. 检查 GitHub CLI 身份（可选但推荐）：
   - `gh auth status`
3. 检查远端可写（需要提交结果时）：
   - `git remote -v`
   - `git status --short --branch`

## 1) 区块：源数据获取（Source）
### 目标
拿到 `all.md` 作为后续校验与转换输入。

### 标准流程（与 CI 对齐）
- `curl -L --fail -o /tmp/all.md "https://raw.githubusercontent.com/ttttmr/Wechat2RSS/refs/heads/master/list/all.md"`

### Mock 流程（网络不稳/离线调试）
用最小样例模拟，不依赖线上下载：
- `python3 -c "from pathlib import Path; Path('/tmp/mock_all.md').write_text('## 安全\\n[示例号](https://wechat2rss.xlab.app/feed/0123456789abcdef0123456789abcdef01234567.xml)\\n', encoding='utf-8'); print('written /tmp/mock_all.md')"`
- 注意：`/tmp/mock_all.md` 只有 1 条链接，会触发 `validate_source.py` 的最小链接阈值保护；它主要用于调试转换脚本或命令连通性。

### 该区块测试工作流
- 成功标准：目标文件存在且非空。
- 快速检查：
  - `python3 -c "from pathlib import Path; p=Path('/tmp/all.md'); print(p.exists(), p.stat().st_size if p.exists() else 0)"`

## 2) 区块：数据校验（Validation）
### 目标
在转换前拦截“源数据清零/格式错误/分类缺失”问题。

### 执行命令
- `python3 scripts/validate_source.py /tmp/all.md`

### 结果判定
- 通过：输出 `✅ 文件验证通过`，进程退出码为 0。
- 失败：输出 `❌ 文件验证失败`，需先修复源数据再继续。

### 常见失败与处理
- `文件不存在`：检查下载路径是否正确。
- `没有发现有效的 XML 链接`：确认链接包含 `wechat2rss.xlab.app/feed/`。
- `XML 链接数量过少`：很可能是上游数据异常，不要继续覆盖产物。

### 该区块测试工作流
- 正向：对真实 `all.md` 运行一次，应通过。
- 反向：传不存在路径（例如 `/tmp/not_exists.md`），应失败，确认守护逻辑仍生效。

## 3) 区块：格式转换（Convert）
### 目标
把校验通过的 Markdown 生成 OPML 产物。

### 执行命令
- `python3 scripts/convert_to_opml.py /tmp/all.md /tmp/wechat2rss.test.opml`

### 结果判定
- 输出 `转换完成！` 且按分类打印统计。
- 生成的 OPML 以 XML 声明开头，并包含 `<opml version="1.0">`。

### 该区块测试工作流
- 正向：使用已通过校验的输入运行转换。
- 负向：缺参数运行（`python3 scripts/convert_to_opml.py`）应打印用法并失败。

## 4) 区块：CI 对齐回归（Workflow Parity）
### 目标
在本地复现 CI 主路径，减少“本地好使、CI 失败”。

### 推荐一键流
- `curl -L --fail -o /tmp/all.md "https://raw.githubusercontent.com/ttttmr/Wechat2RSS/refs/heads/master/list/all.md" && python3 scripts/validate_source.py /tmp/all.md && python3 scripts/convert_to_opml.py /tmp/all.md /tmp/wechat2rss.test.opml`

### 该区块测试工作流
- 若改动了 `scripts/*.py` 或 `.github/workflows/convert-to-opml.yml`，必须跑一次该一键流。
- 若仅改文档，可跳过转换，但至少确认命令未过时（手动 spot-check 关键命令）。

## 5) 产物检查与提交流程
### 目标
避免提交空产物、损坏 XML 或异常缩减数据。

### 建议检查
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('/tmp/wechat2rss.test.opml'); print('xml ok')"`
- 对比分类/订阅数量是否在合理范围（异常缩减要先排查源数据）。

### 实际产物更新（仓库文件）
- `python3 scripts/convert_to_opml.py /tmp/all.md wechat2rss.opml`
- `git add wechat2rss.opml`
- `git commit -m "Update OPML from latest source"`
- `git push -u origin <your-branch>`

## Feature Flags 说明（本仓库特例）
- 当前仓库**没有应用运行时 feature flags**。
- 如需“开关式测试”，使用“输入数据 mock”替代：
  - 小样本输入：快速验证脚本功能。
  - 真实 `all.md`：验证生产路径。

## 维护这个 Skill（新增 runbook 经验时）
每次发现新技巧/坑位，按下面规则更新本文件：
1. 把经验放到对应区块（Source / Validation / Convert / CI / 产物）。
2. 每条经验必须包含：
   - 触发条件（什么时候会遇到）
   - 1 条可复制命令
   - 成功/失败判定标准
3. 若是高频问题，追加到“常见失败与处理”。
4. 改完后至少跑一次“CI 对齐回归一键流”，确保文档命令仍可执行。
