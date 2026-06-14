---
name: conda-env-selector
description: >-
  要运行用到第三方库的 Python 时先用本 skill 选 conda 环境，不要默认丢进 base。覆盖这些常见请求：跑
  train.py / app.py / evaluate.py / spider.py 等脚本、运行 notebook 里的可视化或分析代码、按
  requirements.txt 或 environment.yml 装依赖再运行、clone 或打开一个 Python 项目后在本地把它跑起来、跑
  flask/django 服务、用 pandas / numpy / sklearn / torch 做数据分析或写作业、pip install
  某个包好让代码能跑；以及代码报 ModuleNotFoundError / ImportError / No module named XXX、import
  某库失败、明明 pip install 了却还是找不到模块这类情况。判断要不要用：只要用户想真正「执行」一段依赖第三方包的
  Python 代码，就先走本 skill 选环境（项目同名环境 / 通用 general 环境 / 新建项目环境）。不适用：纯标准库的一两行临时验证、非
  Python 代码（如 node 跑 index.js）、只是解释报错含义、对比 conda 与 venv 该用哪个、只把代码改写成别的语法而不运行、只创建环境或只检查
  environment.yml 格式、只 review 代码不运行、conda 命令本身找不到。
version: "1.0"
---

# Conda 环境选择

## 这个 skill 解决什么问题

AI 在帮用户跑 Python 时，最容易犯两个错：一是图省事直接用 `base` 环境，把各种包乱装进去，
把 base 搞脏；二是遇到 `ModuleNotFoundError` 就盲目 `pip install`，结果污染了不该动的环境、
或装出版本冲突。本 skill 给出一套固定的决策流程，让环境选择变得可预测：**项目代码进项目环境，
杂活进通用环境，base 保持干净。**

## 何时启动这个流程

满足以下任一条件，就先走下面的决策流程，**不要默认用 base 跑**：

- 你准备运行的 Python 代码依赖第三方库（不是纯标准库）。
- 在 base 里跑出了 `ModuleNotFoundError` / `ImportError`，或装包遇到版本冲突。
- 你打算 `pip install` / `conda install` 某个包来让代码跑起来。

> 纯标准库、一两行的临时验证（比如 `python -c "print(1+1)"`），可以直接用 base，不必走流程。

## 决策流程

### 第 0 步：确定"当前项目文件夹名"

环境命名以**项目根目录的文件夹名**为准。判断项目根：

- 如果在 git 仓库里，用 `git rev-parse --show-toplevel` 的结果取 basename。
- 否则用当前工作目录（用户实际在操作的目录）的 basename。

记下这个名字，记作 `<项目名>`。注意 conda 环境名不能含空格等特殊字符；如果文件夹名包含
空格或中文，把它规范化（空格→`-`，去掉特殊符号），并在告知用户时说明你用的实际环境名。

### 第 1 步：列出现有环境

```bash
conda env list
```

看清楚都有哪些环境，逐一和下面的情况比对。

### 第 2 步：按情况选环境

**情况一 —— 存在与 `<项目名>` 同名的环境**

直接用它。这是为这个项目准备的环境，缺什么包就往这里装。

**情况二 —— 没有同名环境**：再判断这是"小任务"还是"大项目"。

#### 怎么区分小任务 vs 大项目

不要机械套用，结合下面的信号做整体判断；拿不准时优先**问用户**。

倾向"**小任务**"（→ 用通用环境 `general`）：
- 单个或少量脚本、作业、练习、demo、临时数据分析、一次性计算。
- 项目目录里**没有**依赖声明文件（`requirements.txt` / `environment.yml` /
  `pyproject.toml` / `setup.py` / `Pipfile`）。
- 用户的措辞是"帮我写个作业""算一下""跑个脚本看看"这类一次性请求。
- 用完大概率不会再长期维护。

倾向"**大项目**"（→ 询问是否新建项目环境）：
- 目录里有上面那些依赖声明文件，或有明显的包/多模块结构（多个子目录、`src/`、`__init__.py`）。
- 是个有实质代码的 git 仓库，会持续迭代。
- 需要固定/特定版本的依赖，和别的项目隔离很重要。
- 用户把它称作"项目""系统""我的工程"，或要长期开发。

#### 情况二之 A：小任务 → 用通用环境 `general`

`general` 是处理杂活的共享环境。先确认它在不在 `conda env list` 里：

- 已存在：直接用，缺包就往 `general` 里装。
- 不存在：创建它（无需征求用户，这是 skill 约定的通用环境）：

```bash
conda create -n general python -y
```

然后用 `general` 跑代码、按需装包。

#### 情况二之 B：大项目 → 询问用户是否新建项目环境

**先问用户**（这一步不要自作主张创建），例如：

> 当前项目 `<项目名>` 没有对应的 conda 环境。这看起来是个需要独立环境的项目，
> 我建议新建一个名为 `<项目名>` 的环境来隔离它的依赖。要现在创建吗？

- 用户同意：创建并使用。如果项目里有依赖声明文件，按它来装依赖：

  ```bash
  # 优先用 environment.yml（它自带环境名和依赖）
  conda env create -f environment.yml
  # 或者新建空环境后按 requirements 装
  conda create -n <项目名> python -y
  conda run -n <项目名> pip install -r requirements.txt
  ```

  没有依赖声明文件时，先建空环境，再按代码实际报错缺什么装什么。

- 用户拒绝或想用别的环境：按用户的选择来（比如临时用 `general`，或指定某个已有环境）。

## 怎么"用"选定的环境跑代码

在非交互 shell 里 `conda activate` 经常不生效。运行命令时优先用 `conda run`，它最稳：

```bash
conda run -n <环境名> python your_script.py
conda run -n <环境名> pip install <包名>
```

如果需要在同一个会话里连续操作、或脚本本身依赖被激活的环境，再考虑显式激活
（`source activate <环境名>` 或先 `conda init` 后激活），并向用户说明。

## 一句话总结优先级

1. 有同名项目环境 → 用它。
2. 没有同名环境 + 小任务 → 用（必要时创建）`general`。
3. 没有同名环境 + 大项目 → 问用户，同意则新建 `<项目名>` 环境再用。
4. 任何时候都别拿 base 当垃圾桶乱装包。
