---
title: "04-配置规则策略"
description: "04-配置规则策略的操作说明。"
---

# 配置规则策略

## 一、适用场景

本文适用于在 **WMS系统** 中配置各类业务规则策略，包括 **作业流程**、**操作配置**、**仓库货主参数**、**定位规则**、**分配规则**、**波次规则** 等核心配置。

常见使用场景：

1. 已完成基础资料配置后，需要进一步配置出入库作业逻辑。
2. 不同 **货主**、**单据类型**、**仓库** 有不同作业要求，需要通过策略规则实现差异化配置。
3. 出现出库包裹无法更新状态、无法打开详情、入库收货无法扫描等问题时，需要检查相关规则配置。

## 二、前置条件

- **账号与权限要求**：需要拥有 **总部管理员权限**。若无权限，请联系系统管理员开通。
- **基础资料要求**：已完成 **仓库**、**货主**、**员工**、**库位**、**SKU** 的创建。
- **业务信息准备**：提前确认货主的出入库流程要求，例如是否需要 **复核**、**打包**、**称重**，以及承运商信息、定位策略偏好（**空库位优先** / **补满库位优先**）等。

## 三、操作入口

常用配置入口如下：

- **策略 > 作业流程**
- **配置 > 操作配置**
- **配置 > 仓库货主配置**
- **配置 > 策略**

::: tip 说明
不同系统版本或账号权限下，菜单名称和展示位置可能略有差异，请以系统实际菜单路径为准。
:::

## 四、名词解释

- **作业流程**：按 **仓库 + 货主 + 单据类型 + 流程类型** 配置作业流程节点，决定出入库需要经历哪些环节，例如 **复核**、**打包**、**称重**。

::: danger 重点提醒
如未配置作业流程，可能导致出库包裹无法更新状态，且无法打开出库包裹详情。
:::

- **操作配置**：当仓库货主在进行某操作、满足某条件时，需要遵循的操作验证规则。配置项包括是否校验 **库位**、**货品编码**、**数量**、**首件扫描**、**逐件扫描** 等。
- **仓库货主参数**：仓库维度下的货主级业务参数配置，涵盖 **入库信息**、**库存信息**、**B2C出库信息**、**B2B出库信息**、**回传信息** 等多个大类共 **40+项参数**。
- **定位策略**：入库上架库位的匹配规则。根据 **基本单位**、**货主**、**库存类型** 筛选库位范围，按定位原则和上架策略排序后，循环确定定位库位与数量。
- **定位原则**：**绑定区域优先**，即绑定货主 / 货品的库位优先分配。
- **上架策略**：
  - **空库位优先**：就近找符合条件的空库位。
  - **补满库位优先**：在符合条件库位范围内找到未装满库位填满，不会拆分基本单位。
- **分配策略**：出库库存分配规则，包括 **库位分配原则**、**属性分配原则**，用于筛选库位并对库位库存排序。状态属性条件按订单下发商品属性严格筛选库存。
- **波次规则**：订单批量处理的组波规则。波次类型分为 **批量波次**（仅订单结构一致的订单）和 **散单波次**（无规律订单），不同波次类型拉动不同出库流程。
- **承运方案**：为包裹分配 **承运商 + 网点 + 产品类型 + 增值服务** 的规则。
- **上架定位条件**：用于配置 **货主 + 单据类型** 可以使用哪条定位规则，将定位规则与业务场景关联。
- **拆包规则**：自动拆包的触发条件：按重量、体积超出阈值自动拆包，或按组合货品配置自动拆分。
- **包装方案**：为包裹推荐和指定包装方式的配置，包括 **主包材**、**辅助包材**、**耗材** 等。

## 五、操作步骤

### 5.1 配置作业流程与操作配置

#### (1) 配置作业流程

1. 进入 **策略 > 作业流程** 页面。
2. 按 **仓库 + 货主 + 单据类型 + 流程类型** 组合配置作业流程节点。
3. 根据实际业务需要维护流程节点。
4. 如业务要求打包只做计件，实际打包在复核环节完成，可关闭 **打包** 节点。

::: danger 重点提醒
作业流程未配置或配置不完整时，可能导致出库包裹无法更新状态，且无法打开出库包裹详情。
:::

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/c5c70b55-d6f2-41b6-824c-2698548d8ef2.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=f%2BtOMDQsI87QEe8bB%2BX6nvpTHu4%3D "")

#### (2) 配置操作配置

1. 进入 **配置 > 操作配置** 页面。
2. 根据仓库货主的作业要求，配置满足条件时需要遵循的操作验证规则。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/b05124fb-acbb-450d-afbd-9664060afaa2.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=oohMEqjpEbk1BFEximgnBhfS7kA%3D "")

3. 将 **复核**、**打包**、**称重** 配置为 **无需验证**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/57832018-7cff-4bdf-8d8e-704204d9b593.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=cudBS%2F0R6vtou0gnUWej%2FoO%2FEr8%3D "")

4. 将相关校验项配置为 **否**。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/3d2b2c91-474c-4f3b-a669-7a26533e69d0.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7B%2F1YfhbeNcM1V%2BPs08KXNtgcbM%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/6876faf1-0119-47fb-8286-3085589e8ab2.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=JsOFx%2FVynR5rbqJz1MA0Mvxl4S0%3D "")

### 5.2 配置仓库货主参数

1. 进入 **配置 > 仓库货主配置** 页面。
2. 按仓库、货主维度维护相关业务参数。
3. 根据业务场景配置 **入库信息**、**库存信息**、**B2C出库信息**、**B2B出库信息**、**回传信息**、**运营配置-B2C**、**配置发件人** 等参数。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/1c67365d-ce63-456e-8455-bb79ccafe806.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zyZp17k3MtboElKx0%2B5yka2hPpc%3D "")

#### (1) 核心参数表

| <strong>大类</strong> | <strong>参数</strong> | <strong>含义</strong> |
|----------|----------|----------|
| 入库信息 | 分批入库 | 分批入库回传开关，每上架一笔则回传上游一笔 |
| 入库信息 | 分批入库单据 | 分批入库单据类型 |
| 入库信息 | 允许超收类型 | 允许超收类型单据类型，允许超出通知数量收货 |
| 入库信息 | 库存状态强校验 | 开启后对应单据类型的入库单需按订单明细中的库存状态操作收货 |
| 入库信息 | 序列号强校验 | 开启后，如果入库单下单含snList计划应到的序列号，则只能收计划序列号，在收货时会校验扫描序列号与计划序列号是否一致（入库单明细行维度），不一致则会报错 ![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/4b82ad2d-cd78-47ef-8bed-f0ab21a2232d.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=O%2BewIf35ARBnaR52DjNVJgVA7UQ%3D "") |
| 入库信息 | 到货登记回传 | 到货登记页面，登记退件包裹，登记后会回传。到货登记和销退登记的区别：到货登记是包裹到仓后扫描记录有哪些单号的包裹退回 |
| 入库信息 | 入库抽检类型 | 抽检单据类型，需要质检登记 |
| 入库信息 | 抽检比例(%) | 以及抽检比例 |
| 入库信息 | 整单入库类型 | 不可多次分批入库 |
| 入库信息 | 收货提醒 | 开启后，收货时若SKU档案的信息未维护（一级和二级单位的体积/毛重/换算数量、是否管理效期、是否管理入库日期），则系统进行提醒 |
| 入库信息 | 扫序列号类型 | 哪些单据类型开启序列号扫描？ |
| 入库信息 | 建单通知销退类型 | 销退入库的单据类型 |
| 库存信息 | 禁售调整 | 开启后达到禁售日期的库存会调整库存状态 |
| 库存信息 | 临期调整 | 开启后达到临期日期的库存会调整库存状态 |
| B2C出库信息 | 重量验证 | 是否称重环节验证称重与理论重量差异 |
| B2C出库信息 | 重量差异 | 差异的最大范围 |
| B2C出库信息 | \*允许拦截节点 | 允许上游通过接口拦截节点 |
| B2C出库信息 | \*预售允许拦截节点 | 仅针对预售出库单据，可忽略 |
| B2C出库信息 | \*允许作废节点 | 允许仓内作废节点，作废后会将包裹作废，并创建新的包裹，重新出库 |
| B2C出库信息 | 回传节点 | 回传上游出库单作业节点 |
| B2C出库信息 | 分批回传 | 是否多个包裹分多次回传 |
| B2C出库信息 | 序列号加波次 | ![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/d56be190-f16b-4216-95fd-8dc7e6ab3190.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=YsNelEP9Y29AtOyIdLgUsFSwH%2Bg%3D "") |
| B2C出库信息 | 扫序列号类型 | 出库单据类型 |
| B2C出库信息 | 出库序列号库存 | 货品序列号管理：出入库 ![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/3f1985bf-c916-473f-b611-2e2424190638.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=rqq25LfcSJHiD%2BRl1sZRalUER80%3D "") |
| B2C出库信息 | 缺货判断 | 接口推单是否需要校验仓库库存，如推单总数可超出仓库可用库存 |
| B2C出库信息 | 抽检比例(%) | 批量单抽检比例，可忽略 |
| B2C出库信息 | 允许暂挂节点 | 允许上游暂挂节点 |
| B2C出库信息 | 预售允许暂挂节点 | 仅针对预售单据 |
| B2C出库信息 | 自动拆包 | 新包裹是否根据拆包规则自动拆包 |
| B2C出库信息 | 自动取单 | 出库包裹是否自动取面单号 |
| B2C出库信息 | 排除承运公司 | 货主仓库不用承运商 |
| B2C出库信息 | 推荐包材个数 | 系统自动推荐包装方案数量 |
| B2C出库信息 | 预售接单放行状态 | 预售单默认放行状态 |
| B2B出库信息 | 拆分维度 | 拆分拣选任务维度 |
| B2B出库信息 | 手动生成计划类型 | 手动创建出库计划的出库单据类型 |
| B2B出库信息 | 不允许拦截节点 | 不允许接口拦截节点 |
| 回传信息 | 库存调整回传类型 | 回传调整结果给上游客户 ![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/34c0ecf4-8170-49b3-8052-7223099e007b.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=3%2FSU4p3SwV2TYpZ%2FJcgybmAAyMM%3D "") |
| 回传信息 | 盘点通知单回传 | |
| 回传信息 | 出入库库存异动 | 对接了库存异动通知回传标准接口的，可开启 ![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/0822e185-e86d-46a6-814d-78452ae83085.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=2Jp766HVj27jM1zazYw3IsP9Tzw%3D "") |
| 回传信息 | 入库单据类型 | 出入库移动回传的单据类型 |
| 回传信息 | 出库单据类型 | 出入库移动回传的单据类型 |
| 运营配置-B2C | 重量验证 | 是否称重环节验证称重与理论重量差异 |
| 运营配置-B2C | 重量差异 | 差异的最大范围 |
| 运营配置-B2C | 重量验证单据 | 需要校验重量差异的单据类型 |
| 配置发件人 | 发件人 | 申请面单的寄件人 |

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/58e1f268-95e7-4f9d-9148-33e72a9c494b.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6VLxMa%2FlmgWASbL8EMW0nesnzgk%3D "")

### 5.3 配置策略规则

1. 进入 **配置 > 策略** 页面。
2. 根据业务场景选择需要配置的策略类型。
3. 按货主、单据类型、流程类型、优先级等条件完成规则配置。
4. 如策略需要与业务场景关联，请同步配置对应的条件类规则，例如 **上架定位条件**、**分配条件** 等。

#### (1) 策略清单（共21项）

| <strong>策略名称</strong> | <strong>说明</strong> |
|----------------|----------|
| 作业流程 | 不同货主+流程类型+单据类型的作业流程，决定出入库操作流程![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/f686ba44-cb6b-4d94-ae0a-dcd9dfddeecd.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=kEbq%2BNVxK371rMWDYEN2OrgXIUs%3D "") |
| 定位规则 | 上架定位规则：区域绑定货主优先/默认，根据规格/单位/货主/质量状态选择库位范围，按优先级执行。上架定位条件，关联货主+单据类型+定位![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/5d2935a3-63bb-4efa-877c-415183d33e51.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4Yh0WFMFp%2BfoaHOC20DKodPZPfg%3D "") |
| 拣货任务拆分规则 | B2B波次使用，根据分配请求按维度拆分创建任务单![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/1206c1a8-1f8f-4e7e-b8f0-8103c6cd475c.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=xIWMU7%2Bju192ifB2cvUGEj1eJcQ%3D "") |
| 分配规则 | 出库库存分配规则![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/c8041697-7da8-4fec-a3f2-2bde0ada785d.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ki6GTZZGWdO2W35P7qTu9yl%2BCKA%3D "") |
| 分配条件 | 将分配规则关联到具体业务场景的条件![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/328135e0-edf8-498f-800e-d074ed851e3e.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=YlyQIzHXUt%2BIDqzWWwHyzLXm7iU%3D "") |
| 波次规则 | 订单组波规则，包含波次类型/分组/分配规则/打单模式等![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/2d3584a6-50e2-4ab6-8fa9-a32cd0d952e7.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Y%2Fxv6W7nyqathkg9Z6J9Ym7BsIQ%3D "") |
| 集货规则 | 根据货主/单据类型/集货维度选择集货区，应用于B2B波次![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/41edeb94-71e1-4cfa-a08e-b1368fa1584a.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=e24WGEFg8LU%2B1mYW%2FPvnr5Fsd3U%3D "") |
| 包装方案 | 为包裹推荐和指定包装方式的配置![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/090c1e71-2d34-4784-a271-1b8411f96a7d.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=jTq7EXOFiT1qrPmtc4fztvM3hF4%3D "") |
| B2B分配条件 | B2B订单的分配规则：是否自动分配/指定规则/自动拆分任务![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/61f2109f-0a1f-4591-850e-5ca076d1bb3b.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=BaVeK%2B7KZof8DLz6lkFw%2FciFB5A%3D "") |
| B2B波次规则 | B2B出库的波次规则![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/d824709c-e7b7-4bb4-89c8-7eadacaca8ba.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=2F1fk6o9lQeH6ZZGu6kvmWWkaps%3D "") |
| 拣货任务拆分规则(2B) | 将分配请求或包裹明细分组合并创建拣货任务![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/ac446f52-a6ee-4af5-82d9-26dc54bc6591.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=GZB1ctT3dgT%2BIlUWqqhSjUGLIJU%3D "") |
| 赠品规则 | 货主、销售平台与赠品的关系配置![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/5229b776-504a-4811-8181-473f8cdf0730.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ux065OZtlnob8MeMf4UMbGpmRtQ%3D "") |
| 拆包规则 | 自动拆包规则，配合组合货品使用 |
| 序列号管理 | SKU如何管理序列号 |
| 序列号规则 | 如何截取保存序列号 |
| 指定包装方案 | 指定标识、指定包装方案、指定货品结构，为包裹指定包装方案的规则 |
| 盘点计划 | 周期盘点的计划，可自动产生盘点单 |
| 条码截取规则 | 如果外来条码太长，会按照截取规则截取固定长度拼接固定符号 |
| 打印设置 | 业务流程需要打印某种模板，归属菜单+模板类型+流程节点+打印类型的规则 |
| 承运方案 | 为包裹分配承运商+网点+产品类型+增值服务的规则 |
| SKU接口更新规则 | OMS再次推送SKU时允许更新字段的规则 |

### 5.4 配置定位策略

1. 在 **配置 > 策略** 中选择 **定位规则**。
2. 根据 **基本单位**、**货主**、**库存类型** 筛选库位范围。
3. 按 **定位原则**、**上架策略** 对库位排序。
4. 系统循环确定定位库位与定位数量。
5. 当剩余待定位数量不足第一优先级基本单位时，顺次选择第二优先级，直至全部收货数量定位完成。
6. 配置 **上架定位条件**，将 **货主 + 单据类型** 与定位规则关联，决定使用哪条定位规则。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/aadc0759-9c44-4382-ab43-242f10d5d437.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=hCb8KTxO7NIZFriDsoaPJWQfbjI%3D "")

- 🔹 **定位原则**：**绑定区域优先**，即绑定货主 / 货品的库位优先。
- 🔹 **上架策略-空库位优先**：就近找符合条件的空库位。
- 🔹 **上架策略-补满库位优先**：库位配置 **忽略容量=否** 时，在符合条件库位范围内找到未装满库位填满，不会拆分基本单位。例如基本单位 **100**，库位剩余容量 **80**，则跳过该库位。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/6c3d3427-56ad-490c-b77f-8230b25b8f9c.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=fjTSG%2F3QZNKnDs5XgDJ2Mbsy36Q%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/58e1f268-95e7-4f9d-9148-33e72a9c494b.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6VLxMa%2FlmgWASbL8EMW0nesnzgk%3D "")

### 5.5 配置分配策略

1. 在 **配置 > 策略** 中选择 **分配规则**。
2. 配置 **库位分配原则**、**属性分配原则**，用于筛选库位并对库位库存排序。
3. 按订单下发的商品属性，通过状态属性条件严格筛选库存。
4. 范围信息按照分配单位级别确定范围。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/1489a0aa-d9f8-43a3-a932-1034b473d324.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=WzhL%2FtEjKujmDMM0KPtDa033On0%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/1d22831b-0826-460e-8996-7d6e980a82fb.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=N%2FL0jP%2BV83Wyn5k749eYD%2FuQQ24%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/0acdf833-0f26-4de3-b873-48202298c8bb.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=o%2B%2BBmneKPdRd2%2FyY3hGxKO1%2BFQU%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/02f43ed0-9696-4a2e-8c07-3bbe7102cb03.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zfQRmjE5pzv%2FKT7WfZYshrkfb7g%3D "")

### 5.6 配置波次规则

1. 在 **配置 > 策略** 中选择 **波次规则**。
2. 按业务需要配置 **波次类型**、**波次分组**、**分配规则**、**打单模式**、**任务数** 等字段。
3. 根据波次类型，确认订单是否符合加入波次的要求。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/KM7qeobp1E2Y7lpj/img/7fecbae8-45c5-490e-a21a-a4260435daa6.png?Expires=1783781747&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=b2MR5qoC%2BWx8sadCj%2FqkcWks%2Fik%3D "")

#### (1) 波次规则字段说明

| <strong>字段名称</strong> | <strong>含义</strong> |
|----------------|----------|
| 波次类型 | 波次单类型，不同类型拉动不同流程。批量仅支持加入订单结构一样的订单，可以批量复核、称重。散单支持加入结构无规律的订单使用。 |
| 波次分组 | 对波次内的订单进行分组，可用以分组拣选，组号/序号可打印到面单上 |
| 分配规则 | 出库分配占用库存的规则 |
| 打单模式 | 前置或后置打印节点。对于单品单件散单使用货找单复核则可使用后置打单，扫描货品则打出订单 |
| 任务数 | 拆分的任务最大数量 |
| 任务最大单量 | 每个任务最多明细行数 |
| 任务最小单量 | 每个任务最小明细行数 |
| 预售波次 | 仅针对预售类型订单，选择否即可 |

## 六、操作结果

完成配置后，系统将按已配置的规则执行对应业务逻辑：

- 出入库包裹按 **作业流程** 流转到对应节点。
- 仓库货主作业时，按 **操作配置** 执行对应校验或无需验证。
- 入库上架时，按 **定位规则** 和 **上架定位条件** 自动推荐或匹配库位。
- 出库分配时，按 **分配规则** 筛选库存并排序。
- 订单组波时，按 **波次规则** 生成对应波次并拉动后续出库流程。
- 仓库货主相关业务参数按 **仓库货主配置** 生效。

## 七、注意事项

::: danger 重点提醒
- **作业流程** 必须按 **仓库 + 货主 + 单据类型 + 流程类型** 完整配置，否则可能导致出库包裹无法更新状态，或无法打开出库包裹详情。
- **复核**、**打包**、**称重** 需要配置为 **无需验证**。
- 相关校验项需要配置为 **否**。
- **补满库位优先** 不会拆分基本单位。例如基本单位 **100**，库位剩余容量 **80**，则跳过该库位。
- **批量波次** 仅支持加入订单结构一样的订单。
- **预售波次** 仅针对预售类型订单，选择 **否** 即可。
:::

::: warning 注意事项
- 策略配置后如未生效，需检查是否已关联对应 **货主 + 单据类型**，例如是否配置了 **上架定位条件**。
- 多条策略同时满足时，需关注策略优先级及是否被更高优先级策略覆盖。
- 涉及接口回传、拦截、作废、暂挂等参数时，应结合上游系统对接情况谨慎配置。
:::

## 八、常见问题

### 8.1 为什么配了策略但没生效？

请重点检查以下内容：

1. 策略是否已关联到对应的 **货主 + 单据类型**，例如 **上架定位条件**。
2. 策略优先级排序是否正确。
3. 是否被其他更高优先级的策略覆盖。

### 8.2 定位策略“补满库位优先”和“空库位优先”如何选择？

- **空库位优先**：适用于希望货物分散存放、提高库位利用率的场景。
- **补满库位优先**：适用于希望集中存放、方便管理的场景。

::: warning 注意事项
**补满库位优先** 不会拆分基本单位。例如基本单位 **100件**，库位剩余容量 **80件**，则跳过该库位。
:::

### 8.3 出库包裹无法更新状态怎么办？

常见原因是 **作业流程未配置或配置不完整**。

处理方式：

1. 进入 **配置 > 作业流程**。
2. 补充配置 **仓库 + 货主 + 单据类型 + 流程类型** 的作业流程。
3. 保存后重新检查出库包裹状态。

### 8.4 出库包裹详情页打不开怎么办？

常见原因是 **作业流程未配置或配置不完整**。

处理方式：

1. 进入 **配置 > 作业流程**。
2. 补充完整对应 **仓库 + 货主 + 单据类型 + 流程类型** 的作业流程。

### 8.5 入库收货无法扫描怎么办？

常见原因是 **操作配置** 中相关验证开关未正确配置。

处理方式：

1. 进入 **配置 > 操作配置**。
2. 检查 **货品编码**、**库位** 等校验开关设置。
3. 按业务要求调整后再重新扫描。