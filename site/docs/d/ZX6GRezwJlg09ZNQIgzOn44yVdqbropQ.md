---
title: "07-WMS 2B出库作业"
description: "07-WMS 2B出库作业的操作说明。"
---

# WMS 2B出库作业

## 一、适用场景

本文适用于 **WMS 2B出库** 全流程操作，包括：

**出库订单 → 出库计划 → 拣货任务（波次/分配/调整）→ 拣货确认 → 交接发货**

2B出库适用于企业对企业的大批量、计划性出库场景。与2C出库不同，2B出库以 **出库计划** 为操作单位，支持多次分批出库、多种拣货模式（批拣/按单拣/边拣边分）以及集货交接。

::: warning 注意事项
当前2B功能存在局限：

- 不能同2C出库包裹一样支持 **预处理自动取号、设置承运方案、灵活指定承运商配置、无销售平台匹配平台取号配置、打印设置选择模板自动打印**。
- 取号打印环节功能较弱。
- 集货功能代码暂不在交付范围。
- 仅可用的功能完全可用 **2C出库包裹** 替代。
:::

::: tip 补充说明
取快运子单数量功能需要提升：2B出库计划中 **单据类型=冷链B2B出库（2B）** 时，自动根据 **SKU总数量** 取云冷子单数量，此为新开发功能。
:::

## 二、前置条件

操作前请确认以下准备项：

- **权限要求**：账号需具备仓库管理员权限，并已完成仓库货主配置中的 **2B自动化参数** 设置。
- **系统配置**：
  - 单据类型设置为 **2B类型**。
  - 已配置 **B2B波次规则**、**任务拆分规则**、**B2B分配条件**、**承运商配置**。
- **设备要求**：
  - PC端：用于操作 **出库订单/计划/波次/交接**。
  - PDA端：用于操作 **B2B拣货/交接发运**。

## 三、操作入口

2B出库涉及以下菜单页面，请按实际业务选择对应入口：

- **出库订单**：所有订单池
- **出库计划（2B）**：根据出库订单生成单次出库计划任务，1个出库订单可拆分多次出库计划
- **出库计划明细**：总览计划下每SKU的分配、拣货、交接进度
- **B2B波次**：多为一单一波，小出库计划可合并创建波次组合拣货
- **B2B拣货**：拣货任务
- **集货规则**：设置如何分配集货位，出库计划预处理可预分配集货库位
- **集货管理**：以集货位视角汇总计划拣货、集货进度
- **单据类型**：设置出库单据类型为2B或2C，决定出库订单进入不同流程
- **作业流程**：设置2B出库作业流程，当前仅可免交接发运环节
- **B2B波次规则**：组波分配拣选集货规则
- **任务拆分规则**：按计划单据/SKU/库区/巷道拆分拣货任务
- **B2B分配条件**：预设货主和分配规则关系，用于逐单拣选出库计划
- **PDA B2B拣货**：执行拣货任务并放置在集货区
- **PDA B2B交接发运**：用于与承运公司交接

## 四、核心名词解释

- **出库订单**：上游推送的出库单据，一个订单可分多次创建出库计划。2B出库单据类型为 **THCK（退货出库）**、**QTCK（其他出库）**。
- **出库计划**：2B出库订单的一次出库计划任务，是2B出库的核心操作单位。
- **B2B波次**：多为一单一波，小出库计划可合并创建波次组合拣货。波次类型分为 **B2B批拣**、**B2B按单拣选**、**B2B边拣边分** 三种。
- **B2B批拣**：多单加入一个波次，再按拣货任务总拣。
- **B2B按单拣选**：每出库计划生成一个拣货任务，一单一拣货任务。
- **B2B边拣边分**：每单分配一个集货位，按SKU总拣后立即分到每集货位（面向门店或车线）。
- **集货规则**：设置如何分配集货位，出库计划预处理可预分配集货库位。
- **交接发货**：与承运公司完成包裹交接并触发发运的环节（PC或PDA操作）。

## 五、操作步骤

### 5.1 出库订单生成出库计划

**系统功能路径**：**出库 -> 出库订单**

1. 进入 **出库 -> 出库订单** 页面。
2. 确认出库订单是否为2B出库单据。

::: danger 重点提醒
只有 **出库订单类型=THCK退货出库**、**QTCK其他出库** 的订单才是2B出库单据，才可以创建出库计划。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/f6008957-0843-4571-8937-538a7e343664.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=al2RAvzrrEd%2Ffa8%2BwE0daT2PE2E%3D "")

3. 如需修改订单，点击 **变更信息**，变更出库订单信息。

::: warning 注意事项
变更出库订单信息后，会作废已创建的出库计划，需要重新生成。
:::

4. 点击 **生成计划**，手动生成本次计划出库数量对应的出库计划。

::: tip 补充说明
是否自动创建出库计划，受参数 **仓库货主配置——手动生成计划单据类型** 控制。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/6ba3e0f5-dcb4-4c10-a4ba-9d9b9da67ef0.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=iGYTuRk15cPU2VPznI%2BznpQAjHg%3D "")

### 5.2 查看或生成出库计划

**系统功能路径**：**出库 -> 出库计划（2B）**

出库计划是2B出库订单的一次出库计划任务。

1. 进入 **出库 -> 出库计划（2B）** 页面。
2. 查询已生成的出库计划。
3. 按业务需要继续进行库存分配、组波或拣货任务生成。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/e3e90591-3423-4645-b2fc-608bf33ff326.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=AwkPhYWwhH90O%2Bhb5qylTyQnmRw%3D "")

### 5.3 生成拣货任务

创建拣货任务前，需要先分配库存，再生成拣货任务。支持以下三种方式，三者可以组合使用、互相补充。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/7927cee2-b025-436b-b180-2e150a875e13.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=qSKVeU7Xg0BDiKXbRrXpZ3BtvmE%3D "")

#### (1) 方式A：加入波次

适用于批量操作，多个订单一起加入波次组合操作，更普遍、方便。系统会按 **B2B波次规则** 中的分配规则自动分配库存。

1. 选择需要处理的出库计划。
2. 将出库计划加入波次。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/3c809799-0bb7-4fa1-a73d-deae05c904a4.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=OWz5INEbKb1XjQ9s2IlmtA90RJA%3D "")

**波次类型说明：**

- **B2B批拣**：多单加入一个波次，再按拣货任务总拣。
- **B2B按单拣选**：每出库计划生成一个拣货任务，一单一拣货任务。
- **B2B边拣边分**：每单分配一个集货位，总拣后立即分拣到各集货位。如波次跨库区拣货，则按库区拆分多个拣选任务，每个拣货任务总拣后立即分拣到每个出库计划所在集货位。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/e36aa21b-6efb-4a8f-81e3-6fe7391822b2.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=o9iVmlvhtOVNJZQJFPrcreFv2%2B8%3D "")

**波次操作流程：**

1. 进入 **B2B波次** 页面，点击 **创建波次**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/8eb4721e-d3de-4a90-96e0-ae2648dd1812.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=z%2BYKKFX44AiXP%2BkNN%2BdICwiStbM%3D "")

2. 点击 **运行波次**。
3. 如有需要，可执行 **更改集货区**。
4. 点击 **释放波次**，系统产生 **B2B拣货任务**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/4ef4ece1-6cc7-45ce-ad5a-06df66c24a61.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=NlJLu5JwKnbVl6QErWFUYLfyEJg%3D "")

5. 点击 **打印单据**。

::: danger 重点提醒
务必先 **释放波次**，再 **打印单据**。
:::

**可打印单据说明：**

- **B2B批拣单**：每个拣货任务打印一页，用于总拣。
- **按单拣货单**：每个出库计划打印一页，用于大2B订单。
- **送货单**：每个出库计划打印一页，用于与司机、门店交接。

#### (2) 方式B：分配库存

适用于按单操作，常用于货主有特殊分配要求的场景。

1. 选择需要处理的出库计划。
2. 调用 **B2B分配条件** 进行库存分配。
3. 分配成功后，如有需要可继续调整分配。
4. 生成拣货任务（可手动/可自动）。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/39c01a59-1433-4d0c-839e-95bb1b2d28dc.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=9haGgCOJHI0X3HUKuzZu3bmmWDo%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/ebe261fc-07ba-4b25-a1d8-98ead6b47e87.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ymlUZGVO%2FFm58ZRaesECSVujleQ%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/1034e263-e642-4d03-a674-00369807f5ac.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=AOVMVe%2F5Nj7zFF4dsiM%2BobPdICY%3D "")

#### (3) 方式C：调整分配

适用于不需要系统规则分配、需要手动指定库存的场景，例如 **仅出临期**、**仅从退货区出库** 等。

1. 进入出库计划详情。
2. 点击 **调整分配**。
3. 检索库位，并指定库位库存。
4. 分配结束后，点击 **生成拣货任务**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/140c3ad2-6166-470e-8ac2-597fdaec547a.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=2lZ45fdpDMAOju1eukZznu1gwFI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/6b682567-641b-4eb2-8a51-7cc334c5b1ec.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=rZ69wxI1907r0Bi%2Fwm7nAzXEfKA%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/72cbf501-13a9-46ba-920b-1f2f8f6d0ee2.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=q%2F%2BtNsOfcmkPpki8NFJEFjVIqYI%3D "")

### 5.4 拣货任务确认

拣货任务生成后，可选择以下任一方式确认拣货。

#### (1) 方式一：纸质单拣货

1. 打印拣货单。
2. 仓内按纸质单完成拣货。
3. 在PC端进入 **B2B拣货**。
4. 执行 **任务确认**。

::: warning 注意事项
拣货任务不能更改库位，但可以少拣或多拣。是否允许多拣、少拣，取决于 **操作配置-拣货**。
:::

#### (2) 方式二：PDA拣货

1. 使用PDA进入 **B2B拣货**。
2. 选择对应拣货任务。
3. 按页面提示完成拣货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/1da9769f-fb73-475a-938a-8946d53901d3.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=TOFYkM2m0sjbRjpyLH6aPSTQryE%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/c8cebce3-e304-4cc5-97b4-e085a4064b9b.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=73RyZlXyrQz02SqbZ66G3gfnQ5E%3D "")

**PDA支持的三种拣选模式：**

- **B2B批拣**：拣选B2B批拣波次任务。
- **B2B按单拣货**：拣选B2B按单拣选波次任务。
- **B2B边拣边分**：拣选B2B边拣边分波次任务。

::: tip 补充说明
操作说明可参考：《中通仓链20260423系统更新日志》。
:::

### 5.5 交接发货

拣货完成后，可选择PC或PDA进行交接发货。

#### (1) 方式一：PC交接发货

1. 在PC端进入交接发货相关页面。
2. 查询需要交接的出库计划或包裹。
3. 按页面提示完成交接发货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/78acfb11-9617-4040-8b9f-cc2ea7193b03.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=AD0raTnv6kcGeZSLzANOjoSpr5U%3D "")

#### (2) 方式二：PDA B2B交接发运

1. 使用PDA进入 **B2B交接发运**。
2. 查询或扫描需要交接的单据。
3. 按页面提示完成与承运公司的交接发运。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/cd24e8e6-eaa6-4b29-986b-332beba04450.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lQb3W83IU3YQi2wAG4jWDVYwzzw%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/f3ba8c84-d958-4602-8ca0-591b4b7c9a7d.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=j36y6yKfAFHS%2Bsr3%2B4gwMgj%2BW8E%3D "")

## 六、操作结果

完成以上操作后，应达到以下结果：

1. 2B出库订单已生成对应的 **出库计划**。
2. 出库计划已完成库存分配，并生成 **B2B拣货任务**。
3. 拣货任务已通过PC或PDA完成确认。
4. 出库货品已完成 **交接发货** 或 **PDA B2B交接发运**。

## 七、注意事项

::: danger 重点提醒
- 只有 **THCK（退货出库）**、**QTCK（其他出库）** 类型的出库订单，才可按2B流程创建出库计划。
- 打印单据前，务必先 **释放波次**。
- 2B当前取号打印能力较弱，部分能力不能同2C出库包裹一致。
:::

::: warning 注意事项
- 变更出库订单信息后，会作废已创建的出库计划，需要重新生成。
- 集货功能代码暂不在交付范围，如当前功能无法满足业务，可暂用 **2C出库包裹** 替代，或等待后续版本更新。
- 拣货任务不能更改库位；是否允许多拣、少拣，取决于 **操作配置-拣货**。
:::

### 7.1 相关系统参数

**仓库货主配置——手动生成计划类型**

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4EZlweZdGEbRGqxA/img/31e59378-0063-4d79-98b7-8b7f6f07b50f.png?Expires=1783781725&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=GtpD85MJjdZdQZPejxZz4ZcPoas%3D "")

## 八、常见问题

### 8.1 常见异常与处理

| **序号** | **异常现象** | **常见原因** | **解决方案** |
|----------|----------------|----------------|----------------|
| 1 | 无法创建出库计划 | 出库订单类型不是2B（THCK/QTCK） | 确认单据类型配置为2B类型 |
| 2 | 集货功能不能用 | 集货功能代码暂不在交付范围 | 暂用2C出库包裹替代，或等待后续版本更新 |
| 3 | 取号失败 | 承运商配置未匹配 | 检查承运商配置，确保已为2B出库单据类型配置承运方案 |
| 4 | 波次释放后无法打印 | 未先释放波次再打印 | 务必先释放波次再打印单据 |

### 8.2 B出库和2C出库有什么区别？

**A**：2B以 **出库计划** 为操作单位，支持多次分批出库、多种拣货模式、集货交接。2C以 **出库包裹** 为单位，支持自动预处理（取号/承运/包装）。2B取号打印功能相对薄弱。

### 8.3 三种波次类型如何选择？

**A**：

- **B2B批拣**：多单合并总拣，适合杂乱小订单。
- **B2B按单拣选**：一单一拣，适合大订单。
- **B2B边拣边分**：按集货位分拣，适合面向门店/车线的出库。

### 8.4 出库订单可以分多次出库吗？

**A**：可以。一个出库订单可以拆分为多次出库计划分批发货。