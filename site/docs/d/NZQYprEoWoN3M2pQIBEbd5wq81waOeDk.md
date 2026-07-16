---
title: "05-入库作业"
description: "05-入库作业的操作说明。"
---

# 入库作业

## 一、适用场景

本文适用于 WMS 入库全流程操作，包括：

- 上游推单 / 本地建单
- PC / PDA 收货扫描
- 收货记录拆分与自动定位
- 上架任务执行（纸质单 / PDA）
- 容器收货
- 期初收货（切仓平移）

入库是 WMS 作业链路的起点，用于将外部货物收入仓库，并上架到指定库位。入库单来源主要有两种：

1. 上游系统（OMS）通过接口推单（标准方式）。
2. 仓库本地手动建单（应急方式，适用于客户未对接系统的情况）。

收货完成后，系统会根据库存属性（批次 / 批号 / 效期 / 托规）自动拆分收货记录，调用定位规则确定上架库位，并自动创建上架任务。仓库人员根据上架任务将货物放入指定库位，完成入库闭环。

## 二、前置条件

- **权限要求**：账号需具备仓库操作员权限，并拥有入库相关菜单的访问权限。
- **系统配置**：已完成定位规则、定位条件、上架策略等入库策略配置（参考《配置规则策略》）。
- **库位配置**：已完成库位创建（参考《创建库位、SKU》），存储区库位已就绪。
- **设备要求**：
  - PC 端：用于收货扫描和上架任务管理。
  - PDA 端：用于移动收货和上架操作。
  - 打印机：用于打印入库单和上架任务单。
- **前置数据**：SKU 档案已维护完整，包括条码、效期、批次属性等信息。

## 三、操作入口

- **入库单据**：**入库 -> 入库单据**
- **PC 收货扫描**：**入库 -> 入库单据** 或 **收货扫描**
- **PDA 普通收货**：**PDA端 → 普通收货**
- **上架任务**：**PC端入库 -> 上架任务**；**PDA端上架任务**
- **容器收货、期初收货**：请以系统实际菜单路径为准。

## 四、核心名词解释

- **入库单**：入库操作的源头单据，由上游 OMS 推送或仓库手动创建。包含入库明细行：SKU、数量、库存状态、批次 / 效期等信息。
- **收货扫描**：将实物与入库单明细进行核对并记录的过程。分为 PC 端扫描和 PDA 端扫描两种方式，支持按件扫描和批量扫描模式。
- **收货记录**：收货后系统根据库存属性（批次 / 批号 / 效期 / 托规）自动拆分生成的记录。每条收货记录对应一条上架任务明细和一条库位库存明细。
- **上架任务**：将收到的货物放入指定库位的操作任务。系统根据定位规则和定位条件自动匹配上架库位并创建任务。
- **定位规则**：定义入库货物应上架到哪个库位的匹配规则（参考《配置规则策略》）。
- **容器收货**：收货到容器的特殊模式。扫描容器领取上架任务，适用于需要按容器管理货物的场景（实际使用较少）。
- **期初收货**：切仓过程中从旧系统平移库存的特殊收货方式。可跳过 SKU 收货的多种校验规则，一键收货，仅用于仓库切换场景。
- **快速上架**：PDA 收货后立即进入上架环节，扫描或选择推荐库位，立即完成上架，无需事先创建上架任务。

## 五、操作步骤

### 5.1 新建入库单

1. 进入 **入库 -> 入库单据**。
2. 根据业务情况选择入库单创建方式。

#### (1) 方式一：上游推单（推荐）

上游 OMS 系统通过标准接口推送入库单据到 WMS。入库单会自动进入 **入库 -> 入库单据** 列表，仓库人员可直接开始收货。

#### (2) 方式二：本地手动建单

当客户没有对接系统时，可手动为货主创建入库单。

1. 进入 **入库 -> 入库单据**。
2. 点击 **新建入库单**。
3. 选择货主。
4. 填写入库明细。
5. 提交入库单。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/4ca3875f-f6c0-48e6-b15e-54c5e9cf1aa2.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=MWKdnhPiQiP7hKIy8AFcZR3wyLs%3D "")

### 5.2 PC 收货扫描

#### (1) 进入收货扫描页面

可以通过以下两种方式进入收货扫描页面。

**方式一：从入库单据进入**

1. 进入 **入库 -> 入库单据**。
2. 找到对应入库单。
3. 点击单据上的 **开始收货**，进入收货扫描页面。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/8177e187-1ab5-4840-bd33-777004046767.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Sj%2FIpcw3M3bsivmgfV0zmuuMGRM%3D "")

**方式二：从收货扫描页面进入**

1. 打印入库单。
2. 进入 **收货扫描** 页面。
3. 扫描入库单号，进入对应入库单的收货扫描页面。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/a2cf5290-ce04-4577-a817-224815f9a584.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=JYQl82sRuk28ugTOJ6n9J3SwvXk%3D "")

#### (2) 收货扫描方式

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/545961bc-e25a-44f7-901e-e8746205679f.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ORz5x6K9BCX1M%2BjyhEeRKGQH8J8%3D "")

- **按件扫描**：扫一次添加已扫描明细 **1件**，适用于逐件核对的高精度收货场景。
- **批量扫描**：扫描商品条码后，手动输入数量，提交后一次性记录多件，适用于大批量收货。
- **批量完成扫描**：勾选入库单明细行，点击 **批量完成扫描**，系统会将所有勾选行加入已扫描明细并提交收货，适用于整单快速收货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/ced483da-852c-458e-b168-42fdbb49af44.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=QN8w3BlNLErtwzbK7g1HJeMW7g0%3D "")

### 5.3 PDA 普通收货

1. 登录 PDA。
2. 进入 **PDA端 → 普通收货**。
3. 根据现场作业方式选择 **按件模式**、**批量模式** 或 **全选批量完成**。
4. 扫描商品并提交收货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/d84c4828-6ece-4bae-b46a-b8ad3cc20834.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=y%2FQkIfO1aKPC5syQirQZZ3nmECA%3D "")

#### (1) PDA 收货方式

- **按件模式**：切换到 **按件**，逐件扫描。扫描一次添加已扫描明细 **1件**，适用于高精度要求的收货场景。
- **批量模式**：切换到 **批量**，扫描一件商品后手动输入数量，一次性记录多件，适用于大批量收货。
- **全选批量完成**：全选明细行后，批量完成扫描。

::: danger 重点提醒
如果 SKU 需要采集 **批次 / 效期** 属性，则不允许批量完成扫描，需逐条录入属性信息后提交。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/757e19ca-b962-4382-b085-6befc363011b.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=QcnHdvJQ3kc3w6BtUnpJyQbge10%3D "")

#### (2) 快速上架

PDA 收货后可立即进入上架环节，扫描或选择推荐库位，并立即完成上架。该方式可省去“先收货、再领取上架任务”的两步操作。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/5b3574c8-1bcb-4e97-9e9e-c275000c5151.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=KnPFiBUKrmMa9V3W1cHJUkT%2F0OY%3D "")

### 5.4 收货记录与自动定位

收货完成后，系统会自动执行以下逻辑：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/92aa619b-ac3f-4efe-9d9b-9a57528c7681.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=znRIDBxr%2BpNXFRpLgrMPANnLgNI%3D "")

1. **拆分收货记录**：系统根据库存属性（批次、批号、效期、SKU 档案一级单位托规）自动拆分为多条收货记录。
2. **生成关联明细**：每条收货记录对应一条上架任务明细和一条库位库存明细。
3. **自动定位库位**：系统自动调用定位条件和定位规则，结合库位配置（区域绑定货主优先、空库位优先 / 补满库位优先），确定每条收货记录的上架目标库位。
4. **创建上架任务**：系统根据定位结果自动创建上架任务，任务会出现在 **入库 -> 上架任务** 列表中。

### 5.5 上架任务执行

1. 进入 **PC端入库 -> 上架任务**，或在 PDA 端进入 **上架任务**。
2. 根据作业方式选择纸质单上架或 PDA 上架。
3. 完成上架后，在系统中确认上架结果。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/9462596e-d9ff-4890-93bc-4d4bf8b5697e.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ASbwGozAegiezympaXvvOckxWVk%3D "")

#### (1) 上架任务功能说明

- **分配**：可指定 PDA 用户执行任务。分配后，其他用户不能领取该任务，适用于指定专人负责特定任务。
- **任务确认**：纸质单作业完成后，根据纸质单记录的实际上架库位和数量，回到电脑端进行任务确认并完成上架，适用于纸质单作业的小仓库。
- **取消分配**：取消分配后，用户可在 PDA 自由领取任务，也可以重新分配给其他人。
- **取消任务**：取消任务后，关联的收货明细会被重置为 **待定位** 状态。可在收货记录页面手动重新定位库位并创建上架任务。

#### (2) 方式一：纸质单上架（适用于小型仓库）

1. 打印纸质上架单。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/d2fefb00-1d9f-4add-a33c-f0b7463af522.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=d7FSsUMz0AfUFv%2BlFCcJCAaELwQ%3D "")

2. 仓库人员凭纸质单在线下完成上架。
3. 如实际上架库位或数量有调整，需记录在纸质单上。
4. 回到电脑端进行 **任务确认**。
5. 根据纸质单记录的实际作业结果，在电脑端完成系统上架。

#### (3) 方式二：PDA 上架（适用于大型仓库）

1. 在 PC 端将任务分配给员工，或由员工在 PDA 端领取 **待上架** 任务。
2. 员工在 PDA 上执行上架。
3. 按系统提示完成扫描、数量录入和上架确认。

| PDA上架，适用于PDA作业的大仓库。任务可以分配给员工，员工在PDA领取"待上架"任务。![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/bc919d79-d2ac-48a6-bacd-81ac15da4a80.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=953dKe25svOl5MW%2Fu%2FNPqDQcU%2F8%3D "")![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/a6171450-d46c-4297-af4a-9d8b4d0efae4.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Tez0kWjVo9XlCn5U700D9b%2Bugro%3D "") |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 5.6 容器收货（补充功能）

容器收货是一种特殊的收货模式：收货时扫描容器，将货物收入容器中，后续通过扫描容器领取上架任务。实际使用较少，仅适用于有容器管理需求的仓库。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/8e0c8850-16a9-4357-bdb1-fb7fcd23ddca.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=0BE4%2BrjUk5GDqx9S1E4lDtSwDMU%3D "")

#### (1) 容器收货操作流程

1. **收货到容器**：收货时扫描容器，将货物收至容器中。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/c1b7ed5f-9bfe-4ea2-a5f6-b57d66c6f93e.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=VuO%2FggB4kWb1au2Acyhq%2Fefjnl8%3D "")

2. 选择 **批量收货** 或 **逐件收货**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/b506b23b-b223-446f-98eb-408fe4f68b05.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ZSBeP97x92pCqOn1FbXdNvFZW1g%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/a86871ac-3b64-4db2-95ab-d9f1080a1547.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2FH8H2oCOA2SkVqIDe%2BSXYtk%2FEyg%3D "")

3. **扫描容器上架**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/e6c63b67-6f92-4da1-ba3e-8dd9e1ba4f2f.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7hXiHsQ9MjU%2BzKE%2FcDvSVxrdbLM%3D "")

4. 扫描容器查询任务。
5. 领取任务。
6. 扫描 SKU。
7. 录入数量。
8. 完成上架。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/ab2bbdf2-4ed9-4ebc-af1a-5c4e0089a487.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=5zEY6RSJLblGDRgPS6jTlICfkRY%3D "")

9. 上架完成后，容器释放，可重新用于下次收货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/52d31833-c72f-46a3-aed1-c4a6f5da98ff.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Oh6jvQhWBWeq1epGru%2F%2BzS5Q1Tg%3D "")

### 5.7 期初收货（仅切仓使用）

期初收货是仓库切换过程中的特殊功能，用于从旧 WMS 系统平移库存到新 WMS 系统。该功能可跳过 SKU 收货的多种校验规则（如条码校验、效期校验、批次校验等），支持一键收货。

::: danger 重点提醒
**期初收货仅用于切仓场景，日常操作严禁使用。**
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmbQd0MEAOm9/img/6d9279e9-fe3c-4148-8892-9795f3b7e149.png?Expires=1783781741&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=u8PoC0nOHaF%2BcTCgKMcsVg0eKo8%3D "")

## 六、操作结果

完成入库作业后，应达到以下结果：

1. 入库单已完成收货。
2. 系统根据库存属性自动生成收货记录。
3. 系统根据定位规则生成上架任务。
4. 仓库人员完成上架后，货物进入对应库位库存。
5. 如使用容器收货，上架完成后容器释放，可继续用于下次收货。

## 七、注意事项

::: warning 注意事项
- 手动建单适用于客户未对接系统时的应急场景。
- PC 收货和 PDA 收货都支持 **按件 / 批量** 扫描，实际使用时可按仓库作业方式选择。
- 若 SKU 需要采集 **批次 / 效期** 属性，不能使用批量完成扫描，需逐条录入属性信息。
- 取消上架任务后，关联收货明细会被重置为 **待定位** 状态，需要重新定位并创建上架任务。
- 容器收货实际使用较少，仅适用于有容器管理需求的仓库。
- 期初收货会跳过多种收货校验，仅用于切仓平移库存，日常入库不要使用。
:::

## 八、常见问题

### 8.1 Q1：PC 收货扫描和 PDA 普通收货有什么区别？

**A**：功能上基本一致，都支持按件 / 批量扫描。差异在于：PC 端适合仓库办公桌旁的集中收货场景；PDA 端适合移动收货，并支持快速上架（收货后立即上架）。大仓库推荐使用 PDA 操作。

### 8.2 Q2：什么时候使用上游推单，什么时候手动建单？

**A**：上游 OMS 已对接时，统一使用接口推单，保证数据一致性和可追溯性。手动建单仅用于客户未对接系统的应急场景，能保证先把货收进来。

### 8.3 Q3：收货记录为什么会拆分成多条？

**A**：系统会根据库存属性（批次、批号、效期）和 SKU 档案的一级单位托规自动拆分。比如同一 SKU 不同批次会拆成多条记录，对应多条上架任务和库位库存明细，保证库存维度精确。

### 8.4 Q4：取消上架任务后会怎样？

**A**：取消任务后，关联的收货明细会被重置为 **待定位** 状态。可在 **入库 -> 收货记录** 页面手动重新定位库位，并重新创建上架任务。

### 8.5 Q5：期初收货和普通收货有什么区别？

**A**：期初收货可跳过 SKU 收货的多种校验规则（条码 / 效期 / 批次校验等），并支持一键收货。该功能仅用于切仓平移库存，日常入库严禁使用期初收货。

### 8.6 常见异常与处理方案

| **序号** | **异常现象** | **常见原因** | **解决方案** |
|----------|----------------|----------------|----------------|
| 1 | 收货时无法扫描货品条码 | SKU档案中未维护条码 / 操作配置中校验开关限制 | 检查SKU档案中条码字段；检查【配置-操作配置-收货】中相关的扫描校验设置 |
| 2 | 收货后没有生成上架任务 | 定位规则未配置或定位条件未关联 | 检查【配置-定位规则】和【配置-定位条件】，确保入库单据类型已关联定位规则 |
| 3 | 上架任务无法领取 | 任务已被分配给其他用户 | 在PC端取消任务分配，或由已分配用户执行。也可取消任务后重新定位并创建任务 |
| 4 | PDA收货无法批量完成扫描 | SKU需要采集批次/效期属性 | 需要采集属性的SKU不允许批量完成扫描，需逐条录入属性信息后提交 |
| 5 | 上架时库位不足 | 库位容量已满且未开启忽略容量 | 在库位管理中开启"忽略容量"选项，或手动将库位类型切换为"库存"类型 |