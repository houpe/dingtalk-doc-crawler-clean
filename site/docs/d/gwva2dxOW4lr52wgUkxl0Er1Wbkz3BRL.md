---
title: "08-库内作业"
description: "08-库内作业的操作说明。"
---

# 库内作业

## 一、适用场景

本文适用于 WMS 库内作业全流程操作，包括：

- **盘点**：仓库定期或临时发起库存实物核对，支持**明盘**、**盲盘**。
- **移库**：仓库内部库位间库存转移，支持 **PDA-直接移库**、**PDA-移库下架/移库上架**、**PC-移库**。
- **补货**：拣选区库存不足时，从存储区向拣选区补充库存。
- **库存状态调整**：对库位库存进行非数量类变更，如锁定、冻结、属性变更等。
- **加工单**：包括**组合套装**和**预包**。
- **增值服务**：非标准化仓库附加服务，通常线下作业、线上登记。

## 二、前置条件

- **权限要求**：操作账号需具备仓库管理员相关权限。
- **货主配置**：货主档案中需完成相关配置，例如开启**盘点调整允许**。
- **基础资料**：
  - 组合套装、预包相关货品需提前在**【组合货品】**页面维护。
  - 安全库存需提前在库位配置中设置。
- **设备要求**：
  - PC 端：用于**盘点开单**、**盘点任务确认**、**调整单据**、**加工单管理**、**补货预警**等操作。
  - PDA 端：用于**直接移库**、**移库下架/移库上架**、**补货任务执行**等操作。
- **容器准备**：**移库下架/移库上架**和**补货任务**需使用容器中转，请提前编码容器并在系统中维护。

## 三、操作入口

各业务入口如下，具体以系统实际菜单路径为准：

| 业务 | 操作入口 |
|---|---|
| 盘点 | **库内 -> 盘点计划** |
| PDA 直接移库 | **PDA -> 直接移库** |
| PDA 移库下架/上架 | **PDA -> 移库下架 / 移库上架** |
| PC 移库 | **库内 -> PC-移库** |
| 补货预警 | **库内 -> 补货预警** |
| 补货任务 | **库内 -> 补货任务** |
| 库存状态调整 | **库内 -> 库存状态调整** |
| 加工单-组合套装 | **库内 -> 加工单 -> 组合套装** |
| 加工单-预包 | **库内 -> 加工单 -> 预包** |
| 增值服务 | **库内 -> 增值服务** |

## 四、核心名词解释

- **盘点开单**：创建一次盘点任务，选择盘点范围（库区/库位/SKU）和盘点方式（明盘/盲盘）。
- **盈亏单据**：盘点差异（盘盈/盘亏）自动生成的差异单据，确认后产生调整单。
- **调整单据**：所有库存调整的统一记录入口，包括盘点调整、库位库存状态属性调整、效期属性自动调整等。
- **直接移库**：不借助容器，从下架库位直接扫描转移到上架库位的移库方式。
- **移库下架上架**：需借助容器周转，流程为下架到容器 → 容器转移 → 从容器上架到目标库位。
- **补货分析**：对比订单需求数量与拣选区、存储区可用数量，生成补货建议。
- **补货预警**：根据订单池、安全库存分析自动生成的补货提醒，可据此创建补货任务。
- **加工单**：将多品组合为新品的作业单据，运行后生成拣货任务，完工确认后新品上架。
- **预包**：预先完成商品包装组合的加工方式，下游出库时可直接调用预包结果。

## 五、操作步骤

### 5.1 盘点作业

#### (1) 盘点流程总览

**操作入口**：**库内 -> 盘点计划**

盘点计划是盘点操作入口。盘点计划操作说明详见关联文档《盘点计划操作说明》。

盘点整体流程：

1. 创建**盘点开单**。
2. 系统生成**盘点任务**。
3. 分配盘点人或由 PDA 领取任务。
4. 录入**实盘数量**。
5. 系统根据差异生成**盈亏单据**。
6. 对盈亏单据执行**调整**。
7. 系统生成**调整单据**。
8. 确认调整单据后，库存变更完成。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/f4fbb5f6-24ad-4529-8a36-554ae3f17c09.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=nYZLFyybeN61RqJDlFUCImEfCV0%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/54d9f8c1-e4df-4075-bca1-3348adecbb52.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7mfcXHxVSWPqcjt2AKg3hA1eZlE%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/ea261a29-be53-4075-babc-4b3b7faa1f8c.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=HeVK6bdeQwrjwoVx04zVjO9Bdhw%3D "")

#### (2) 盘点开单

1. 进入**库内 -> 盘点计划**。
2. 创建盘点单。
3. 选择盘点范围，可按**库区**、**库位**、**SKU**或**全仓**选择。
4. 选择盘点方式：
   - **明盘**：显示系统库存数量。
   - **盲盘**：不显示系统库存数量。
5. 提交后，系统生成盘点任务。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/bcca411b-d50b-4548-80aa-a74b41ab53b4.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Aub5%2BII12HF5XkSp5ilNWbNdr6k%3D "")

#### (3) 盘点任务

盘点开单后，系统会自动生成盘点任务。

1. 进入盘点任务页面。
2. 根据需要分配盘点人。
   - 可分配给指定用户。
   - 未分配时，可在 PDA 自由领取。
3. 点击**编辑**，录入实际盘点数量。
4. 保存实盘数量。
5. 如需纸质盘点单，点击**打印**按钮，打印纸质盘点单用于线下作业。

::: danger 重点提醒
**必须分配盘点人账号**，否则无法提交实盘数量。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/ef43a596-203d-4f7d-b22d-4b72a92390d8.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2BmAFsmESVOdLFjvuMclaJUdW3to%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/89ff5d4d-9aeb-44fc-8e38-ac45401c08dd.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=nOIfJrkHBc2aGyw9L0LQwVvom0Y%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/f874c1d0-8382-4171-ba51-c57154b7817f.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lT4hXLpsIrZXlaSuOAdDvsaq2B8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/9df1dd3d-8b62-4663-9fad-33ad35c401fc.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=GlBcfXdS6SBjVLRk5LCNjcPS%2BVc%3D "")

#### (4) 盈亏单据

盘点结果存在盘盈或盘亏差异时，系统会自动创建**盈亏单据**。

1. 查看盈亏单据。
2. 如需修正库存，点击**调整**。
3. 系统产生调整单据，用于后续库存修正。
4. 如系统触发复盘，按提示重新完成盘点任务。

::: warning 注意事项
如果同一 **SKU** 存在多条不同属性的库存，系统会要求复盘。复盘会生成新的盘点任务，需要重新录入实盘数量。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/94dd4f22-e492-48c3-b0fc-e74838a08da9.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=pDTkAxhrvAFYzgzTI7wGkUvC%2BB8%3D "")

#### (5) 调整单据

已确认的盈亏单据会自动产生**调整单据**。

1. 进入调整单据页面。
2. 查看由盈亏单据生成的调整单据。
3. 确认调整单据。
4. 系统正式调整库存数量。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/9f53e964-cc98-4c0d-a0eb-7c6012422b09.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4EYlRBfhdcdRgaZXDPOf2FyXnSM%3D "")

::: tip 补充说明
所有库存调整都会进入**调整单据**，包括盘点调整、库位库存状态属性调整、依据 SKU 档案效期属性的自动调整等。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/565ba34d-2c32-4932-bc1c-7341288c5eb1.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=89norduuItw04qqisCpw4gD6GBs%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/77f25abc-9afa-4994-acc1-9124a0795825.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=TYs60fhwmcuJvKdfnLlWw7PiefE%3D "")

盘点流程补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/8c676bf6-21f9-4463-b682-4366b9a118eb.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=sxO5IZ2HfCFzyXfrPSNb53qm%2BHs%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/0e5020fc-c8ea-45d4-b47b-99f3cee8b480.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Il0hBRSrtcUPwG4hRu98ICS%2FsCA%3D "")

### 5.2 PDA 直接移库

**操作入口**：**PDA -> 直接移库**

直接移库不需要容器中转，适用于单个库位间的快速库存转移。

1. 打开 PDA，进入**直接移库**。
2. 扫描下架库位编码，或手动选择下架库位。
3. 扫描或输入商品条码。
4. 选择上架库位。
5. 确认后完成移库。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/3c30a3b1-5027-4d68-8674-2a3057fbac27.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Ebq060lTORXJJfNQuC%2FMc91jX58%3D "")

### 5.3 PDA 移库下架与移库上架

**操作入口**：**PDA -> 移库下架 / 移库上架**

该方式需要借助容器中转，适用于跨库区移库、批量移库或需要作业记录的场景。

#### (1) 移库下架

1. 在 PDA 领取或创建移库任务。
2. 扫描下架库位。
3. 扫描商品。
4. 扫描指定容器编码，将商品下架到容器。
5. 确认后完成下架，商品进入容器。

#### (2) 移库上架

1. 扫描容器编码。
2. 确认容器中的商品。
3. 扫描上架库位。
4. 确认数量。
5. 完成上架后，容器释放。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/4a4885eb-359c-4030-9e93-155e67e70a1b.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=jnigy93TpmCPW4kZ7CSs2eNC0dA%3D "")

PDA 移库补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/5486207b-f9e5-499b-bc43-e4729096d18a.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=UjB97JekwzTZRsWkh0EK2ErN4KQ%3D "")

### 5.4 PC 移库

**操作入口**：**库内 -> PC-移库**

PC 端支持批量创建移库计划，适用于大量库存的整体转移。PC 端创建移库单据后，可在 PDA 端领取并执行。

1. 进入**库内 -> PC-移库**。
2. 创建移库单据或移库计划。
3. 提交后，由 PDA 端领取并执行移库作业。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/6db7c444-5c94-40f0-9d82-0b7e92bc524c.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=HqPht%2FQNGrAQBGIZScb%2B%2BRlY%2FpY%3D "")

### 5.5 补货作业

补货用于在拣选区库存不足时，从存储区向拣选区补充库存。系统支持多种触发方式和操作入口。

| **补货触发场景** | **操作入口/页面** | **功能说明** |
|----------------------|-----------------------|----------------|
| 出库-缺货提醒、补货 | PC-出库包裹-补货分析 | 根据单据需求、拣选、存储区域库存，生成补货建议。 |
| 出库-缺货提醒、补货 | PC-包裹汇单-补货分析 | 对待加入波次包裹批量补货分析，自动生成补货预警 |
| 出库-缺货提醒、补货 | PC-安全库存 | 设置拣选区库位库存的安全库存，自动分析与指导补货，当触及预警线，自动生成从存储区到拣选区的补货预警 |
| 出库-缺货提醒、补货 | PC-【出库包裹】【包裹汇单】加入波次 | 加入波次判断缺货，自动生成补货预警 |
| 出库-缺货提醒、补货 | PC- 补货预警 | 查看补货预警，批量生成补货任务，PDA- 补货任务操作补货下架然后补货上架 |
| 出库-缺货提醒、补货 | PC-补货任务 | 仅查看或取消补货任务，前往 PDA-补货任务执行 |
| 出库-缺货提醒、补货 | PDA-补货预警 | PDA 自动根据订单池、安全库存分析，自动生成补货预警，依据补货预警创建补货任务 |
| 出库-缺货提醒、补货 | PDA-补货任务 | PDA领取并完成补货任务 |

#### (1) 补货预警

**操作入口**：**库内 -> 补货预警**

补货预警由系统根据订单池需求、拣选区库存水平、安全库存设置自动分析生成。

1. 进入**库内 -> 补货预警**。
2. 查看系统生成的补货建议。
3. 选择需要处理的补货预警。
4. 批量生成补货任务。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/ed68b2ef-25b9-4613-aa5f-25e5ddbf5771.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=RfuClh5iNnY%2Bn6%2F6fz132JCbnS4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/4f26ccde-4d8b-4522-8d05-40f9eafc2dd9.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Wg70gwIGmnIHyMsvEoHrXOZbsXc%3D "")

#### (2) 补货任务

**操作入口**：**库内 -> 补货任务**

补货任务示例：当订单需求为**2件**，拣选区可用**1件**，存储区有**4件**时，系统分析缺货并生成补货任务。

1. 进入**库内 -> 补货任务**。
2. 查看补货任务。
3. 如需批量补货，选择**批量补货**。
4. 系统进行补货分析。
5. 判断库存充足后，可加入波次，简化操作流程。
6. 补货任务生成后，会产生**PDA-补货任务**。
7. 作业人员在 PDA 端领取补货任务。
8. 先完成**补货下架**。
9. 再从容器**补货上架**到目标库位。
10. 补货上架完成后，系统自动释放容器。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/6b87a229-c9ed-410d-8858-ca0b37ac88c4.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=0w3LQ4aYnbcgd70sXDgYshp7mD4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/63fb52a0-437d-422c-a6ae-809e4656950d.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=5YkbHquqv4U53%2FZouDMDMphVvc4%3D "")

在**【PC-补货任务】**页面可以查看补货记录，包括任务状态、操作人员、完成时间等。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/98aa1970-0cbb-46fb-8317-843d387d64c3.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=WdYjHeUCACRcGBn125E95%2Ftne0o%3D "")

::: warning 注意事项
依据补货预警产生补货任务后，需要扫描容器进行中转。补货上架完成后，系统自动释放容器。
:::

补货任务补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/dcf2211d-999a-432f-809f-0c0a701dfe59.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=iXRzvChpZ0%2Fs7nypOzdA2aUbiT8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/4cd4dad5-90ed-4d27-8663-1d4e16f2e0e9.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2BG6ojxvuuuVRW336mMcl%2F74s9so%3D "")

### 5.6 库存状态调整

**操作入口**：**库内 -> 库存状态调整**

库存状态调整用于变更库位库存的非数量属性，例如锁定/解锁、冻结/解冻、批次属性修正等。

1. 进入**库内 -> 库存状态调整**。
2. 选择需要调整的库位库存。
3. 修改对应库存状态或属性。
4. 确认调整。
5. 系统正式修改库存状态。
6. 系统在库存日志中记录完整变更链条。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/671f3b73-75a7-4ee0-b6d2-0a0309c599ee.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=l3RFC583huBLYBVhKn%2FgV2ztIIA%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/f18020e9-ddc5-423a-985b-aef2cf1d7ec0.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=eXN2kx9lZqqM2YhI8bY%2Ffhofhgw%3D "")

库存状态调整补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/3c2d0ccb-f55e-43e8-b91b-53c151f457e5.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=rQIcxFDscXWnyOtdhl72p7LTo%2FQ%3D "")

### 5.7 加工单组合套装

**操作入口**：**库内 -> 加工单 -> 组合套装**

组合套装用于将多品（多个 SKU）组合为一个新品（新 SKU）。加工完成后，系统增加新品库存，同时扣减原材料多品库存。

1. 操作前，先在**【组合货品】**页面维护组合方案，定义原材料 SKU 与成品 SKU 的对应关系及用量。
2. 进入**库内 -> 加工单 -> 组合套装**。
3. 创建加工单。
4. 运行加工单。
5. 选择库存分配规则。
6. 确定并运行成功。
7. 打印拣货单。
8. 线下完成商品组合。
9. 完工确认，同时新品上架。
10. 可在**【库内-加工拣货】**页面查看拣货详情，追踪加工单的物料下架和完工进度。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/c9882e79-3145-4aa9-88b8-13492069494e.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=hMUhZinszcMyWHFNx84Eb3vnuHc%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/39e579ee-8604-4845-b6d5-e023b17ebef7.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=GMTrz1slk2ptusm%2FQCcT9q2ygHQ%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/7830ba83-f62a-4451-a6e0-a49dd24c07a8.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=pCzqH8JWleOddEExdfIadelNSHY%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/03d47eca-bb16-4abe-ac9a-59c2ed69717d.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Skx%2FnCzbgeBSwv%2FYTve1YCj9XGM%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/73f68dab-8d28-40d5-9e46-663459c0aa9b.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CReLr6Hw5EugXCN69hQUU1QWne4%3D "")

### 5.8 加工单预包

**操作入口**：**库内 -> 加工单 -> 预包**

预包是预先完成商品包装组合的加工方式。操作前需在**【组合货品】**中新增预包方案，定义预包包含的 SKU 及数量。

1. 进入**【组合货品】**，新增预包方案。
2. 进入**库内 -> 加工单 -> 预包**。
3. 新增预包加工单。
4. 运行加工单。
5. 选择库存分配规则。
6. 确定并运行成功。
7. 打印拣货单。
8. 线下完成商品组合。
9. 完工确认，同时新品上架。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/1e9a83aa-992f-4354-b005-3749026529b4.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=A0tQ1wJRaTWLrsAcRWvQm1WrrAs%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/33534c47-7d49-4de7-a2f1-4800ed66b458.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=fxvFRrM4RqM8N5DEEwNU5fO1kRw%3D "")

::: danger 重点提醒
预包下架操作需将原材料移库下架到预包区，**必须有规定的下架数量**，系统会校验。
:::

### 5.9 增值服务

**操作入口**：**库内 -> 增值服务**

增值服务用于登记仓库提供的非标准化附加服务。由于服务内容个性化、流程非标准，通常采用线下作业、线上登记的模式。

1. 进入**库内 -> 增值服务**。
2. 创建或登记增值服务单。
3. 根据实际服务内容，记录服务信息。
4. 线下完成对应作业。
5. 系统端完成登记记录，便于后续追溯和计费。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/115cf4fc-8424-4bbf-94bf-4e2245a6237e.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=I9IMZA7VVDNYTRsVehOwbcBeMJk%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/e4f8aea4-b84b-4689-a24c-aafe82e9fc48.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=yHKP6Bh0rxpAgTq2t%2FaSImES9d8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/00f6bee3-7e30-4dfc-abc3-93c1f5cd42a4.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=RcNOOeRuNtIqmoPeVM5pG%2BE0cBM%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/59ce2268-f296-4719-b85c-0ea6c929ca5e.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lX053N%2B%2F5ZpHEDEdnOOdbHdewmI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/6db8e831-1a8e-4fe5-a21d-0516ef4d8969.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=JlbsxTM6OFKJMoANPHvApxtCr3Y%3D "")

::: tip 补充说明
增值服务单标准化程度低，主要以线下作业为主，系统端完成登记记录，便于追溯和计费。
:::

增值服务补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/b54803f9-95ae-4609-a775-1a64b376bddd.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4C9NGFzMNsUH2T3bCmY2w6sRzVI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/NpQlK5jB090LjqDv/img/9fc090dd-180b-431b-bde9-a7734b1e4b6b.png?Expires=1783781706&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=iaBDrfN%2Bkn8lERF%2FRJ6EcQeFKQE%3D "")

## 六、操作结果

完成对应库内作业后，可看到以下结果：

- **盘点**：生成盘点任务、盈亏单据和调整单据；确认调整单据后，库存数量完成修正。
- **移库**：库存从原库位转移到目标库位；使用容器中转的任务完成后，容器释放。
- **补货**：系统生成补货预警或补货任务；PDA 完成补货下架和补货上架后，拣选区库存得到补充。
- **库存状态调整**：库存状态或属性变更完成，并产生调整记录和库存日志。
- **加工单**：原材料库存扣减，新品库存增加；可在**【库内-加工拣货】**查看进度。
- **增值服务**：系统完成增值服务登记，便于后续追溯和计费。

## 七、注意事项

::: danger 重点提醒
- **盘点调整**需在货主档案中开启相关权限。
- **盘点任务必须分配盘点人账号**，否则无法提交实盘数量。
- **预包下架**必须有规定的下架数量，系统会进行校验。
:::

::: warning 注意事项
- 盘点过程中，如果同一 **SKU** 存在多条不同属性库存（如批次、效期不同），系统可能触发复盘。
- 移库下架/上架、补货任务涉及容器中转时，需确保容器内商品全部完成上架确认，否则容器可能无法释放。
- 加工单运行前，请确认原材料库存充足，并确认**【组合货品】**方案已维护。
- 补货任务生成失败时，请检查存储区库存和安全库存设置。
- 增值服务流程个性化较强，具体作业方式需结合实际服务内容处理。
:::

## 八、常见异常与兜底方案

| **序号** | **异常现象** | **常见原因** | **解决方案** |
|----------|----------------|----------------|----------------|
| 1 | 盘点不允许调整 | 货主档案中未开启调整权限 | 前往货主档案配置，开启盘点调整开关 |
| 2 | 无法提交实盘数量 | 未分配盘点人账号 | 在盘点任务页面分配盘点人后再执行操作 |
| 3 | 复盘要求触发 | 同一SKU存在多条不同属性库存（批次/效期不同） | 按系统提示完成复盘操作，会生成新的盘点任务 |
| 4 | 移库容器无法释放 | 移库上架未完成或容器中有未确认商品 | 检查容器内所有商品是否已完成上架确认 |
| 5 | 补货任务生成失败 | 存储区库存不足以补充；补货预警未触发 | 确认存储区库存数量；检查安全库存设置是否合理 |
| 6 | 加工单运行失败 | 原材料库存不足；组合货品方案未维护 | 检查原材料库存；在【组合货品】页面确认方案已维护 |

## 九、常见问题

### 9.1 Q1：盘点开单后可以修改盘点范围吗？

**A**：盘点开单后一般不建议修改范围。如确实需要调整，可取消当前盘点计划，重新创建盘点单并选择正确的范围。

### 9.2 Q2：直接移库和移库下架上架有什么区别？

**A**：直接移库无需容器中转，适合单库位快速移库；移库下架上架需要借助容器中转，适合跨库区移库、批量移库或需要作业记录的正式移库场景。

### 9.3 Q3：补货分析什么时候会触发？

**A**：补货分析在多个环节自动触发，包括：

- **出库包裹**页面按包裹逐单分析。
- **包裹汇单**页面对待加入波次包裹批量分析。
- **出库包裹/包裹汇单**加入波次时判断缺货。
- 安全库存触及预警线时。

可在**补货预警**页面统一查看和生成补货任务。

### 9.4 Q4：盘点产生亏损后库存何时修正？

**A**：盘点差异生成盈亏单据后，点击**调整**产生调整单据；确认调整单据后，库存即时修正。所有调整记录都会进入**调整单据**统一管理，可追溯。

### 9.5 Q5：加工单（组合套装）与预包加工有什么区别？

**A**：组合套装是正式加工流程，将多品组合为新 SKU，产生新品库存。预包加工是预先包装作业，为下游出库做备货准备，出库时可直接调用预包结果减少包装耗时。两者操作流程相同，区别在于业务目的和成品用途。

### 9.6 Q6：增值服务单如何操作？

**A**：增值服务因需求个性化，目前以线下作业为主。在系统端创建增值服务单进行登记，记录服务内容、工时、耗材等信息，便于后续结算和追溯。具体操作流程根据服务类型单独设计。

### 9.7 Q7：库位库存调整后在哪里查看变更记录？

**A**：所有库存调整，包括盘点调整、状态属性调整、效期自动调整等，均进入**【调整单据】**统一管理。确认后产生库存日志，可追溯每次变更的时间、操作人、变更前后状态。