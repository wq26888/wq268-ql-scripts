# 青龙任务

以下命令与当前目录结构一致：

| 任务 | 定时规则 | 命令 |
| --- | --- | --- |
| 69云签到 | `0 10 * * *` | `wq268-ql-scripts/69yun/69yun_checkin.py` |
| GLaDOS 签到 | `35 12 * * *` | `wq268-ql-scripts/glados/checkin.py` |
| iKuuu 签到 | `0 21 * * *` | `wq268-ql-scripts/ikuuu/ikuuu_checkin.py` |
| 天翼云盘签到 | `1 16 * * *` | `wq268-ql-scripts/cloud189/cloud189_checkin_v2.py` |
| 夸克签到 | `13 18 * * *` | `wq268-ql-scripts/quark/quark_signin.py` |

定时规则只是当前使用示例，可在青龙面板中按需要修改或停用。脚本内部启用随机延迟时，实际执行动作会晚于任务启动时间。
