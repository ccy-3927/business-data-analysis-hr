# IBM员工离职分析与可视化

以模拟企业HR业务场景为主线，回答岗位案例集中度、员工结构和离职识别三个问题，并提出访谈、工作负荷核查及员工支持方案。

**数据明确对应课程附件A“UCI / Kaggle·IBM HR”条目。**选用 IBM HR Analytics Employee Attrition & Performance，共1470条、35字段。它由IBM数据科学家制作，是虚构样本，不是IBM真实员工记录。模拟场景不等于伪造数据来源；实施方案与计划不写成已经取得的成效。

## 查看成果

- `docs/商业数据分析期末论文.docx`：按原模板制作；封面个人信息留空。
- `商业数据分析.ipynb`：可直接在现有Jupyter中逐步运行，发布版清空本地执行输出，可按顺序重新运行。
- `outputs/figures`：24张PNG图表，包含教材图形迁移与业务分析图，部分图形已按展示需要调整。
- `outputs/tables`：数据审计、ABC、聚类、预测及评估明细。
- `docs/字段与分析口径.md`：字段解释与指标口径。
- `docs/思路与答辩说明.md`：分析思路与答辩说明。

## 运行

在本目录打开终端，使用已有Anaconda内核。已检查的主要包为Python环境中的pandas 2.2.3、scikit-learn 1.6.1、Matplotlib 3.10.0、Bokeh 3.6.2；无需重新安装现有包。

```powershell
python run_all.py
python 启动大屏.py
```

大屏文件为 `outputs/dashboard/员工离职管理驾驶舱.html`，双击即可打开。新版使用原生SVG、CSS网格与JavaScript，数据和首屏图表内嵌，无需Bokeh浏览器运行库、联网或Python服务。桌面窗口采用紧凑双排布局，表格内部滚动；窄屏自动改为纵向排列。运行 `python scripts/dashboard.py` 可单独重建大屏，不影响论文和PNG配图。

如使用全新环境，才执行 `python -m pip install -r requirements.txt`。论文生成还需要python-docx；可在已有该包的环境执行 `python scripts/build_report.py`。论文需在Word中核验排版，不能以脚本运行成功代替视觉核验。

## 三个商业分析模块

1. 岗位离职案例ABC：以离职人数计算贡献，跨越80%与95%的岗位归前一类别。四个A类岗位覆盖199/237，即83.97%的案例；不是按工资给员工评定价值。
2. K-Means员工分群：7个特征标准化，K=2至6按轮廓系数选择。最终K=2；离职标签不参与聚类。群1为1188人、群2为282人，离职标签占比18.01%与8.16%。聚类为全样本描述，不接入分类模型。
3. 离职分类预测：分层75%/25%隔离测试；训练集分层5折按AP选择逻辑回归，与随机森林、常数基线比较。阈值仅用训练折外F2选择，为0.09。测试ROC-AUC约0.826、AP约0.609；识别46、漏报13、误报100、正确排除209。不同模型阈值不同，主要用AP/AUC比较排序能力。

预测输入排除目标、员工ID、常量、年龄、性别、婚姻状态及聚类标签；这不自动消除代理偏差。自助区间只覆盖固定模型测试样本的不确定性。数据缺少日期，故不编造月度趋势、同比、年度离职率及同期群留存；MonthlyIncome币种未明确，使用原始数值单位。

## 数据获取与许可

- 发布者：pavansubhash；数据集版本1。
- 页面：https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset
- 获取方式：2026-10-27从Kaggle官方下载API取得ZIP，无网页抓取。
- 接口：https://www.kaggle.com/api/v1/datasets/download/pavansubhasht/ibm-hr-analytics-attrition-dataset
- 平台授权标签：**Database: Open Database, Contents: Database Contents**。来源官方元数据保存在 `data/raw/platform_metadata.json` 和 `dataset_description.json`；文件哈希见 `manifest.json`。
- 原始数据及衍生数据保留来源和相应数据库/内容许可要求，不声明为CC0；代码不改变数据原许可。见 `DATA_LICENSE.md`。
- 教材图形来自用户提供的原文件，只保留样式映射与解析证据，不再分发教材工作簿。

## 文件组织与复现边界

`data/raw` 原始文件、平台说明与哈希；`data/clean` CSV与SQLite；`scripts` 自编分析、图形、大屏与论文代码；`outputs` 结果；`docs` 论文与说明。

随机种子2026，固定模型参数。不同库版本可能出现微小数值差异，以项目记录版本和已保存结果为准。修改特征、参数或数据后应重新生成全部结果，并审核论文中的解释与管理方案。核心统计由结果表读取，少量固定案例说明仍需人工检查。

## 提交状态与分工

仓库：https://github.com/ccy-3927/business-data-analysis-hr

最终提交前：填写姓名、学号、学院、专业班级；填写实际成员分工；本人复核代码与结论；确认论文中的仓库链接与提交信息。

AI使用：OpenAI Codex参与要求核对、代码、图表、论文初稿及排版核验。论文有完整披露，作者应按课程规定审核并理解成果。成员分工：________________。

## 发布文件说明

本仓库保留分析和展示所需文件，不包含本地验收记录、临时截图、缓存及回调测试材料。数据清洗记录与模型评估结果属于分析证据，予以保留。原始ZIP是分析脚本的输入，论文模板是论文生成脚本的依赖。

已保存的PNG包含后续单独美化版本；`scripts/visuals.py`生成的是基础绘图版本，运行`run_all.py`或Notebook的绘图单元会覆盖当前PNG外观。若仅查看成果，可直接浏览PNG和HTML。论文保留本地现有版本，未在本次上传中重新排版或替换插图。
