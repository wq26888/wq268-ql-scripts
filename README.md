# wq268-ql-scripts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

这是我自己在青龙里跑的几个签到脚本。

脚本大多是以前从网上找来的。原版有些已经失效，有些放进青龙后不太好用，所以这些年陆续修过域名、登录流程、多账号、代理和通知。放到 GitHub 主要是给自己留个备份，换机器时也省得重新整理。

这不是原创脚本合集。能找到的出处都写在 [SOURCES.md](SOURCES.md) 里，找不到的也会直接说明。

## 现在有这些

```text
69yun/       69 云签到
ikuuu/       iKuuu 签到
quark/       夸克签到
cloud189/    天翼云盘签到
glados/      GLaDOS 签到
common/      Bark、Telegram 公共通知
```

`common/notify.py` 是仓库自带的，不是青龙默认文件，所以目录结构不要拆开。

## 依赖

在青龙的“依赖管理 -> Python3”里安装：

```text
requests
beautifulsoup4
rsa
```

也可以直接执行：

```bash
pip3 install -r requirements.txt
```

## 怎么用

- 环境变量看 [ENVIRONMENT.md](ENVIRONMENT.md)
- 任务命令和定时参考看 [TASKS.md](TASKS.md)
- 第一次部署建议先手动跑一遍，确认账号、代理和通知都正常

## 青龙订阅

在青龙的“订阅管理”里新建订阅：

```text
名称：wq268-ql-scripts
类型：公开仓库
地址：https://github.com/wq26888/wq268-ql-scripts.git
分支：main
定时：17 4 * * *
白名单：^(69yun/69yun_checkin|ikuuu/ikuuu_checkin|quark/quark_signin|cloud189/cloud189_checkin_v2|glados/checkin)\.py$
黑名单：留空
依赖文件：^common/notify\.py$
文件后缀：py
自动添加任务：开启
自动删除任务：开启
```

这样 `common/notify.py` 只会作为公共依赖复制，不会单独生成一个通知任务。第一次运行订阅后，到定时任务里检查一下生成的五个签到任务。

旧版青龙如果支持 `ql repo` 命令，也可以执行：

```bash
ql repo "https://github.com/wq26888/wq268-ql-scripts.git" "^(69yun/69yun_checkin|ikuuu/ikuuu_checkin|quark/quark_signin|cloud189/cloud189_checkin_v2|glados/checkin)\.py$" "" "^common/notify\.py$" "main" "py" "" "true" "true"
```

部分新版青龙只在面板里管理订阅，终端里没有 `ql` 命令，按上面的字段填写即可。

## 手动拉取

不使用订阅管理时，也可以直接用 Git。

第一次拉取：

```bash
git clone --depth 1 https://github.com/wq26888/wq268-ql-scripts.git /ql/data/scripts/wq268-ql-scripts
```

以后更新：

```bash
git -C /ql/data/scripts/wq268-ql-scripts pull --ff-only
```

更新命令可以直接建成青龙定时任务。已经在“订阅管理”里添加仓库的，不用再建更新任务。

## 说明

上游脚本仍按各自原来的许可使用，许可副本放在 `licenses/`。根目录的 [LICENSE](LICENSE) 只管我后来补的代码、修改和文档。
