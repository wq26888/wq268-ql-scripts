# wq268 Qinglong Scripts

个人使用的青龙签到脚本维护版。部分脚本来自公开项目或早期流传版本，经过兼容性修复和青龙适配。仓库只保存可公开的源码、公共模块和配置说明，不保存账号、密码、Cookie、token、推送 key、数据库、日志或运行缓存。

## 目录

```text
common/      公共通知模块
69yun/       69云签到
ikuuu/       iKuuu 签到
quark/       夸克签到
cloud189/    天翼云盘签到
glados/      GLaDOS 签到
```

`common/notify.py` 是本仓库自带的模块，并非青龙默认文件。Python 脚本会根据自身位置加载它，因此订阅后应保留完整目录结构。

## 安装依赖

这些脚本没有需要编译的本地模块。Python 依赖可在青龙的“依赖管理 -> Python3”中安装：

```text
requests
beautifulsoup4
rsa
```

也可以在仓库目录执行：

```bash
pip3 install -r requirements.txt
```

## 青龙任务

任务命令和当前使用的定时示例见 [TASKS.md](TASKS.md)，环境变量见 [ENVIRONMENT.md](ENVIRONMENT.md)。

建议订阅后先手动运行一次，确认账号、网络代理和推送配置均可用，再启用定时任务。

## 来源与许可

脚本来源、修改内容和上游许可见 [SOURCES.md](SOURCES.md)。本仓库的 [LICENSE](LICENSE) 只覆盖仓库维护者新增的代码、文档及依法可以再许可的修改；第三方代码继续受各自上游许可约束。

分发第三方脚本时应保留原作者、来源和许可声明。69 云脚本的原始出处目前无法确认，仓库不会将其旧有部分声明为原创。

## 隐私

所有私密数据都应通过青龙环境变量提供。提交前请确认 `git status` 中没有数据库、日志、抓包文件、缓存或本地备份。
