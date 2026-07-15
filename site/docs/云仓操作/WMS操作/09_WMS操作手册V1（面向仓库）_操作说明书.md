---
title: "09-WMS操作手册V1（面向仓库）"
description: "09-WMS操作手册V1（面向仓库）的操作说明。"
---

# 09-WMS操作手册V1（面向仓库）

📌 <strong>文档基本信息</strong>

本文档面向仓库操作人员，覆盖WMS仓库管理系统V1版本的全流程操作：库位创建 → SKU维护 → 入库收货上架 → 出库2C拣货复核称重发运 → 规则配置（承运方案/拆包规则/包装方案等）→ WCS打印客户端配置 → PDA-APP安装。文档以场景化步骤展示，配合界面截图，帮助仓库人员快速上手。

## 业务场景与名词解释

### 业务场景（为什么用？）

1. WMS仓库管理系统是仓库日常作业的核心平台。本文档覆盖从库位/货架搭建、SKU档案维护，到入库收货上架、出库拣选复核称重发运的完整业务闭环。仓库人员通过本文档可快速掌握系统PC端和PDA端的标准操作方法。
2. 文档同时涵盖规则配置（承运方案、拆包规则、包装方案等）、WCS打印客户端配置、PDA-APP安装等辅助操作，确保仓库人员能够独立完成系统的基础配置和日常运行。

### 核心名词解释（不迷路）

- <strong>库位</strong>：仓库中用于存放货物的最小物理位置单元。每个库位有唯一编码，可通过导入或手动创建。库位属性包括：库位类型、库存种类、巷道编码、存储策略、动线号、绑定货主/SKU等。
- <strong>货架/库区</strong>：多个库位组成的物理区域。库区是库位的上一级单位，用于仓库的区域划分和管理。创建库位前需先创建货架和库区。
- <strong>SKU（库存单位）</strong>：Stock Keeping Unit，即库存进出计量的最小单位。每个SKU有唯一的编码和属性（尺寸、重量、条码、批次效期要求等）。SKU档案在系统中通过接口同步或手动创建维护。
- <strong>入库单</strong>：入库操作的源头单据，由上游OMS推送或仓库手动创建。包含入库明细行：SKU、数量、库存状态、批次/效期等信息。
- <strong>收货扫描</strong>：将实物与入库单明细进行核对并记录的过程。分为PC端扫描和PDA端扫描两种方式，支持按件扫描和批量扫描模式。
- <strong>收货记录</strong>：收货后系统根据库存属性（批次/批号/效期/托规）自动拆分生成的记录。每条收货记录对应一条上架任务明细和一条库位库存明细。
- <strong>上架任务</strong>：将收到的货物放入指定库位的操作任务。系统根据定位规则和定位条件自动匹配上架库位并创建任务。支持PC端任务确认和PDA端直接上架。
- <strong>波次管理</strong>：将多个出库订单按规则组合成一个波次，统一进行拣货、复核、称重等操作的作业方式。分为批量波次（货品结构一致）和散单波次（货品结构无规律）。
- <strong>复核</strong>：出库过程中对拣货结果进行核对确认的环节。包括普通复核（逐单）、批量复核（批量单）、货找单复核（单品单件）、播种复核（总拣后二次分拣）四种方式。
- <strong>承运方案</strong>：配置包裹分配的承运商、物流产品、增值服务等规则。系统根据承运方案自动为包裹匹配承运公司和物流产品。
- <strong>包装方案</strong>：定义包裹使用的包材、耗材组合。系统可根据指定包装方案或历史操作习惯自动推荐，也可手动指定。
- <strong>拦截</strong>：出库流程中对异常订单进行阻止继续操作的机制。不同节点（加入波次前/待拣货/待复核/待称重）均可触发拦截，拦截后订单进入异常单管理流程。
- <strong>WCS打印客户端</strong>：Warehouse Control System打印客户端，连接打印机后用于打印面单、拣选单、上架单、盘点单等。需安装并保持"已连接"状态。
- <strong>定位规则</strong>：定义入库货物应上架到哪个库位的匹配规则。系统结合库位配置（区域/货主/SKU绑定等）自动匹配上架库位。
- <strong>PDA</strong>：手持终端设备，安装WMS的PDA-APP后用于移动收货、上架、拣货、复核、称重等操作。

## 前置准备与环境配置

- <strong>权限要求</strong>：需拥有仓库操作员权限，能够访问入库、出库、基础配置、规则配置等WMS相关菜单。
- <strong>系统配置</strong>：已完成定位规则、定位条件、上架策略等入库策略配置；已完成承运方案、拆包规则、包装方案等出库策略配置；已完成库位/货架/库区创建。
- <strong>硬件设备</strong>：PC端用于系统配置和任务管理；PDA手持终端用于移动作业；条码打印机用于打印面单和单据；蓝牙秤用于称重环节。
- <strong>软件环境</strong>：WCS打印客户端已安装并连接打印机；PDA-APP已下载安装并登录账号；浏览器建议使用Chrome最新版本。
- <strong>前置数据</strong>：SKU档案已维护完整（条码、效期/批次属性等）；库位/货架/库区已创建；承运商账号已配置。

## 场景化标准操作步骤（怎么用？）

### 创建库位

#### 创建货架、库区

<strong>系统功能路径</strong>：基础 → 库位管理

在创建库位之前，需要先创建货架和库区。货架是库区的上一级组织单位，库区是库位的容器。操作步骤：进入"基础-库位管理"页面，先创建货架（填写货架编号和名称），再在对应货架下创建库区（填写库区编码和名称）。库区创建完成后，即可在该库区下导入或手动创建库位。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/00ce805a-dcfc-4a9e-bd95-385c753a1e5e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=P2XI8BU1Cw9b%2F9l5pkck5usZFrI%3D "")

#### 导入库位

如果仓库已有库位编码体系，推荐使用导入方式批量导入。操作步骤：在库位管理页面点击"导入"按钮，下载导入模板，按模板格式填写库位信息后上传。模板内容包括：库位编码、所属库区、库位类型、巷道编码、动线号等字段。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/79232ce1-9828-4af4-a988-37d3d8abf8b6.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=RS8wyLvLWHtWf5MDRGFIasGaiAI%3D "")

<strong>查看导入结果</strong>：导入完成后系统会显示导入结果汇总，包含成功条数和失败条数。如存在失败记录，可下载失败明细查看具体原因（常见原因：库位编码重复、库区不存在、必填字段为空等），修正后重新导入。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/73270745-c1a4-4a53-bbe8-ae465aa8282f.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lO9nB%2BKj7jTd6MFQAy%2F%2B0gUMjYE%3D "")

<strong>导入库位模板</strong>：请至钉钉文档查看附件《库位配置导入.xlsx》。更新库位模板：请至钉钉文档查看附件《库位配置更新模版.xlsx》。

#### 手动创建库位

手动创建库位适用于开新仓场景，系统会自动为库位编码。操作步骤：进入库位管理页面 → 点击"手动创建" → 选择所属库区 → 设置库位数量 → 系统自动生成连续编号的库位。创建完成后可在库位列表中查看和编辑每个库位的详细参数。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/a0352331-3017-4596-9958-d23b2db643e5.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Fho517TnQmGag1iqv6q3LP5rDUo%3D "")

#### 库位相关参数意义

| <strong>库位参数</strong> | <strong>意义</strong> |
|----------------|----------|
| 库位类型 | 统一选择"库存"，目前入库出库只分配库存类型库位 |
| 库存种类 | 用于限制库位允许的作业类型。如腾空库位，则设置为可出不进 |
| 忽略容量 | 忽略容量后，就不会在入库定位时因库位剩余容量不足而跳过该库位 |
| 巷道编码 | 填了巷道编码可以应用在包裹汇单筛选包裹（前提是包裹前置分配库存），波次规则按巷道分配 |
| 存储策略 | 库位配置关联存储策略后，可限制库位可存入货品属性（效期、品类等） |
| 上架动线号
拣货动线号

盘点动线号 | 动线号用于在任务明细中排序库位动线，优化行走路径 |

| 绑定货主
绑定SKU | 绑定货主、SKU后，会在定位、分配环节优先分配 |

### 创建SKU

<strong>系统功能路径</strong>：基础 → SKU档案

SKU档案是WMS系统的基础数据。创建SKU有两种方式：①上游系统通过接口同步SKU到WMS（推荐方式，保证数据一致性）；②在SKU档案页面手动创建（适用于未对接系统的货主）。

#### 接口同步SKU（推荐）

上游系统（如OMS）通过标准接口将SKU数据同步到WMS。同步内容包括：SKU编码、名称、条码、尺寸重量、行业属性（批次/效期要求）、ABC分类等。同步后SKU自动进入SKU档案列表。

#### 首次入库新品维护

在【仓库货主配置】中开启"收货提醒"后，首次入库的SKU会触发新品维护流程，系统强制要求补充SKU完整信息后才能继续收货。操作步骤：进入收货页面 → 系统弹窗提醒新品需要维护 → 点击维护按钮 → 填写SKU属性信息（尺寸、重量、条码、行业属性等） → 保存后继续收货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ad54d51a-5875-468d-85bd-e1609fce5849.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Rsn8yzqLxAhzJieRGeIdbP3B3kU%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/b1e23a93-44d9-4d84-886d-c6c7910e4253.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6U6nwYiE9qrqk9aNYNRHP1a6T7U%3D "")

#### SKU档案中需要注意的配置

在SKU档案编辑页面中，以下配置项需要重点关注：行业属性（决定收货时是否需要采集批次/效期）、ABC分类（影响库位定位匹配）、单位尺寸和重量（用于推荐包材和校验库位容量）、托规（决定上架时的托盘拆分）、包装单位条码（支持多级条码收货）。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9b57f27b-f39e-4219-86e8-c8c5deb92c8c.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=T%2Ft9f9wvAtSjixL3P0cb0Qp0LSQ%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/87e937f8-174a-4f90-a742-6d25493c3eee.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4TndP3ZuWh1n9usWnweC6Au9jOI%3D "")

#### SKU相关参数意义

| <strong>SKU属性参数</strong> | <strong>意义</strong> |
|-------------------|----------|
| SKU档案-行业属性 | 设置收货需要采集的信息（批次/批号/效期等），决定收货扫描时的必填字段 |
| 类别、ABC分类 | 可用于定位库位时与库位属性匹配。A类高周转、B类中周转、C类低周转 |
| 单位-长宽高体积毛重净重 | 用于推荐包材、校验库位可存储商品数量时的计算 |
| 托规 | 根据SKU托规上架为多个托盘，只看一级单位托规 |
| 包装单位条码 | 扫描包装单位条码也可以收货（多级包装单位） |

### 入库收货与上架

#### 上游系统推单至WMS

<strong>系统功能路径</strong>：入库 → 入库单据

上游OMS系统通过标准接口推送入库单据到WMS。入库单会自动进入"入库-入库单据"列表，可查看所有待收货的入库单（单据号、货主、预计到货时间、SKU明细等）。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/a66c83b6-d830-4038-a51a-6034752ea424.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=J6k9fk8FiG60RXUW9ju04N0s1R0%3D "")

#### PC-收货扫描

<strong>系统功能路径</strong>：入库 → 入库单据 或 收货扫描

两种进入收货扫描页面的方式：①点击入库单据列表中对应单据的"开始收货"按钮；②打印入库单后，打开"收货扫描"页面扫描入库单号，开始收货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/47027da3-e0a1-4c97-8b55-5ed4d04eccc3.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Vqw5N7Hd2cPIsp1Ib6LuCMKzIXI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/f48c77e2-d5a7-458f-8f8e-cb992e80e3f9.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=sGBAv0Q1ZsozNUPOA6rnYmBosdI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/47027da3-e0a1-4c97-8b55-5ed4d04eccc3.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Vqw5N7Hd2cPIsp1Ib6LuCMKzIXI%3D "")

<strong>收货扫描功能说明</strong>：

- <strong>按件扫描</strong>：扫一次添加1件已扫描明细，适用于逐件核对的高精度收货。
- <strong>批量扫描</strong>：扫描商品条码后手动输入数量，提交后一次性记录多件，适用于大批量收货。
- <strong>批量完成扫描</strong>：勾选入库单明细行，点击批量完成扫描，则所有勾选行全部加入已扫描明细并提交收货，适用于整单快速收货。

#### PDA-普通收货

<strong>系统功能路径</strong>：PDA端 → 普通收货

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/118deeab-4668-41ac-a915-9b0e3d486a59.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=cV3AX142rL8zqOkVDmiadD%2B4BRg%3D "")

<strong>PDA收货功能说明</strong>：

- <strong>按件模式</strong>：切换到"按件"，逐件扫描，扫描一次添加已扫描明细1件。
- <strong>批量模式</strong>：切换到"批量"，扫描一件商品后手动输入数量，一次性记录多件。
- <strong>全选批量完成</strong>：全选明细行批量完成扫描。注意：如果SKU需要采集批次/效期属性，则不允许批量完成扫描，需逐条录入。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/f4fd8fdc-141c-4ef0-b809-48774480e44a.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=QSl0RbWjFMsknuK6wBTjmi7EsJo%3D "")

<strong>快速上架功能</strong>：PDA收货后立即进入上架环节，扫描或选择推荐库位立即完成上架，省去先收货再领取上架任务的两步操作，大幅提升效率。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/beeb6158-b503-42b7-b4e7-e7fa44ff5e45.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=FsUBr9f2LsdKRmSX9Om0EAPKAcQ%3D "")

#### 收货记录与自动定位

<strong>系统功能路径</strong>：入库 → 收货记录

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/941c912f-c4f2-43f2-a0e5-4c73d652205d.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2B%2Fdeu9qNnoWnRI3HdlQSyd1LGnc%3D "")

收货完成后系统自动执行以下三步处理：

1. <strong>拆分收货记录</strong>：根据库存属性（批次、批号、效期）和SKU档案的一级单位托规自动拆分为多条收货记录。每条收货记录对应一条上架任务明细和一条库位库存明细。
2. <strong>自动定位上架库位</strong>：调用定位条件和定位规则，结合库位配置（区域绑定货主优先、空库位优先/补满库位优先），确定每条收货记录的上架目标库位。
3. <strong>创建上架任务</strong>：依据定位结果自动创建上架任务，任务出现在"入库-上架任务"列表中。

#### PC-上架任务管理

<strong>系统功能路径</strong>：入库 → 上架任务

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/5428d6f0-688b-4410-97ef-7e79dc207044.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7apzH9A7Gq4aGvxWBtPyd290%2Fps%3D "")

<strong>上架任务功能说明</strong>：

- <strong>分配</strong>：指定PDA用户执行，则其他用户不能领取。不分配则PDA自由领取。
- <strong>任务确认</strong>：纸质单作业完成后，根据记录的实际上架库位和数量，在电脑端确认并完成上架。
- <strong>取消分配</strong>：取消后用户可在PDA自由领取任务或重新分配。
- <strong>取消任务</strong>：取消后关联收货明细重置为待定位状态，可重新定位并创建任务。

#### 两种完成上架任务的方式

<strong>方式一——纸质单上架（小型仓库）</strong>

4. <strong>打印纸质单</strong>：在上架任务页面打印上架任务单

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/76a748b6-cde5-41e3-baab-7d2829af32c3.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2FxcvJ0wCmqg5alwUv%2BpzuFe%2FZiI%3D "")

5. 仓库人员凭纸质单线下完成上架任务，如有调整库位或数量记录在单上。
6. <strong>任务确认</strong>：回到电脑端，点击任务确认，根据纸质单记录的实际作业结果完成系统上架。

<strong>方式二——PDA上架（大型仓库）</strong>

任务可分配给指定员工，或由员工在PDA自由领取"待上架"任务。在PDA上扫描库位编码和货品编码，输入数量，提交完成。PDA上架支持实时库位校验，减少出错率。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/2a80296f-5c99-484c-9369-eb61f85bb582.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=X2L6ZfpgtiMt3ftPI9uyoTPnphU%3D "")

### 出库2C订单处理

#### 上游推单至WMS - 订单分流

<strong>系统功能路径</strong>：出库 → 出库订单

WMS收到上游推送的出库订单后，根据订单类型（2B/2C）自动分流到不同页面：2C类型订单流入"出库-出库包裹"；2B类型订单流入"出库计划"。本文档重点讲解2C出库流程。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/0cc03659-73eb-4554-aa61-e34e0c9a200a.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=cBLZ7ZdH95uBzEvH50UWbAEE85k%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/77d70f31-aa76-4747-bbbc-7ee1a200a63c.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=UyrQ7Apfs6MHU9eJaNsaV9HJieM%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/df0c2537-9f29-4ec4-a8d7-02dc47a76346.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=J2UADuzTD2N6TgXf%2B2u5%2BnDqPes%3D "")

#### 出库包裹处理

<strong>系统功能路径</strong>：出库 → 出库包裹

对于2C订单，系统在出库包裹页面自动进行以下预处理：

- <strong>自动拆包</strong>：根据拆包规则（重量/体积/组合货品）自动拆分包裹。
- <strong>自动匹配作业流程</strong>：支持自定义流程，可免复核、免打包、免称重。
- <strong>分配承运公司</strong>：根据承运方案自动匹配承运商、物流产品、增值服务。
- <strong>自动取号</strong>：查询承运商配置自动获取面单号（有开关控制）。
- <strong>自动推荐包装方案</strong>：根据指定包装方案、历史操作习惯自动推荐。
- <strong>定义时效产品</strong>：查询时效产品管理，按时效要求出库。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/dc1a2498-e088-4600-8262-e01d1361dc40.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=1JVrWBTUo4r9khJR9KOWV%2F917bw%3D "")

<strong>出库包裹页面很重要，要重点关注！！</strong>所有自动操作功能也可以手动重置。

#### 出库包裹手动变更功能

- <strong>手动拆合包</strong>：手动对包裹进行拆分或合并。
- <strong>指定承运商</strong>：变更承运公司、产品类型、增值服务。
- <strong>变更作业流程</strong>：更改包裹的作业流程（添/取消复核、打包、称重）。
- <strong>重新获取面单</strong>：获取推荐包装方案、指定包装方案。手动指定后系统会记录供后续推荐使用。
- <strong>补货分析</strong>：对比包裹需求与拣选区库存，缺货可创建补货任务。
- <strong>编辑录入单号</strong>：对不需要取号的场景手动录入单号用于交接。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/5b1f3599-eae1-4b26-b6bb-e12b21281eb0.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=SEpnsi450WvDS7Fw%2F0Dl%2B592Y7s%3D "")

#### 加入波次

完成取号且库存充足的包裹可加入波次。波次是出库作业的核心组织单位，将多个订单按规则组合后统一进行拣货、复核、称重。

<strong>波次分为两种类型</strong>：

- <strong>批量波次</strong>：仅货品结构一致的订单可加入。可批量拣选、批量复核、批量称重，处理一单则整波完成。
- <strong>散单波次</strong>：货品结构无规律，需先拣后分/边拣边分，逐单复核称重。

操作建议：先筛选批量订单加入批量波次，剩余散单加入散单波次，最大化批量处理优势。

#### 加入波次的多种方式

<strong>方式一：出库包裹-加入波次</strong>

在出库包裹页面筛选符合条件的包裹，点击"加入波次"按钮。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/8e086164-477d-4389-bcc4-8c006a462b50.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=1ibvOJnp1jNrKiQBhgDlqkmk6cY%3D "")

<strong>方式二：包裹汇单-加入波次</strong>

包裹汇单支持多维度筛选汇总：按承运公司、货主、收件省等维度汇总包裹，便于批量打单（不同承运公司指向不同打印机）、便于不同承运公司包裹分堆存放与交接。支持批量拆包、批量指定包装方案。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/fc2cab71-f431-4538-860b-5e702206dfd3.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=OBuY9sXW5xiBWF01hHnP%2B9MgG6E%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/e7c6f0e5-d212-4ee3-8851-e21e9bb08b9f.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=39IPWDd6SFXtM3H7PEhPYphhtr4%3D "")

<strong>汇单操作流程</strong>：

7. 批量单先加入批量波次（货品结构一致，批量拣货/复核/称重提升效率）。
8. 剩余散单加入散单波次（边拣边分后逐单复核）。
9. 选择波次规则，组波。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/1bd01acf-e103-4e27-8736-f3f08a0fe326.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=5t8tn0Eq5X7swyaIVQLCMPTzR2c%3D "")

可使用"分配库位"预分配功能提前占库，根据分配库区区域筛选包裹汇波。可将每次筛选条件保存便于下次引用。

波次单会自动运行：分配库存 → 分组 → 创建拣货任务。波次默认锁定，此时仍可审单、拦截。确认无误后需释放波次才可执行拣选任务。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/507bba5e-9e04-4600-927f-220699c93846.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ZYlofn%2BOWlw2WLP6XtRvAkLwnzg%3D "")

#### 波次管理

<strong>系统功能路径</strong>：出库 → 波次管理

波次管理页面可执行：打印拣货单/快递单/发货单 → 释放任务。如加入前置打单波次，需打单后才可释放。波次释放后才会生成拣货任务供PDA或PC执行。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9b8547bf-2e76-44b8-bf85-6aa37441460e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7qpKkplJGfz1Hy2OY%2BciiH1Nv6s%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/709c2251-3f26-4fc7-ad97-3553cee7b2a4.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=DrlsXZaRMbo23PytCvnNygO04Is%3D "")

#### 拣货任务

<strong>系统功能路径</strong>：出库 → 拣货任务

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9b8547bf-2e76-44b8-bf85-6aa37441460e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=7qpKkplJGfz1Hy2OY%2BciiH1Nv6s%3D "")

拣选是仓库最高频操作。为提升效率、减少出错，在"加入波次"环节将订单分类后加入批量波次/散单波次，相应创建批量单/散单拣选任务。

<strong>完成拣货任务的两种方式</strong>：

10. <strong>PC-任务确认</strong>：打印纸质拣货单 → 线下完成拣货 → 回到PC端任务确认。
11. <strong>PDA拣货</strong>：批量单使用PDA-批量单拣货；散单使用PDA-散单拣货。

#### 拣选方式总览

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/dbf04a0c-8f87-4001-b781-8da32127ab7e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6J5%2BCsJPzXIncY6I8XGwzoVLYKY%3D "")

#### 纸质单拣货

打印拣货单 → 线下完成拣货 → 回到电脑端确认任务。目前必须从分配库位拣货。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ed8c8fb0-c2f1-4149-98f0-e7e32b8dd928.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=hdlxXjDVlqNjS8Jf3iXeyVmd8AI%3D "")

#### PDA拣货

PDA操作流程：PDA-散单拣货/批量单拣货 → 领取拣货任务 → 扫描库位、货品编码 → 输入数量 → 提交 → 所有明细完成后任务完成。

任务分配：可在PC-拣货任务将任务分配给某人，则其他人无法领取。未分配的任务员工可在PDA自由领取。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/4b4cea74-0f15-4054-8cf2-26909bf2303e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CR46jQ8UR3x63AmBcQJc5hZ6bhE%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/d270ddff-a89d-4429-b452-515b8dac28a4.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=LSeFo0cLU5cK57Ed3mJoKU6WYDQ%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/1e08662c-112c-4786-a328-08e1569d4abc.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=x8ZIy6loruc0MveRA7yi41XfVQ4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/0f611e98-965d-478b-916d-36360579c0a7.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=H2r1A%2Fo%2FaHt2Ibg8Aa%2FX4hQrr7c%3D "")

PDA拣货操作规则：可在"配置-操作配置-拣货"中设置是否校验库位/货品编码/数量，以及首件扫描、逐件扫描等。

PDA需手动输入：①拣货货品数量；②客户货品无条码时手动输入条码回车；③最后点击提交按钮。

<strong>效率提示</strong>：批量单（货品结构一致）在加入波次时先加入批量波次，后续可批量拣选/复核/称重，无需二次分拣。

#### 复核

<strong>复核前准备</strong>：扫描工作台号（如：工作台编码1）。工作台来自：容器类型 → 基本类型-工作台 → 使用环节-出库 → 工作台配置。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ac1160db-5d04-40c8-94ec-2218c4b0d3c2.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=KqV7XfkgZZI5xUp7bbQ9tZxseuI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/f5027a87-3863-4cb2-988f-bee3ad968d6e.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=9gBBo7qyr8moI9ZwZ29N4iA6AR0%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/94516958-ac28-4c3e-bc01-29797db86ba8.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=OKnSXhqISbAJCXootX2wqgfd194%3D "")

<strong>复核的四种方式</strong>：

- <strong>普通复核</strong>：散单波次边拣边分后复核，逐单复核。
- <strong>批量复核</strong>：批量单波次复核。与普通复核差别：①拦截订单需确认踢出；②完成一单后自动完成同波其他订单；③不能拆包。
- <strong>货找单复核</strong>：单品单件混品散单+后置打单复核。扫描货品出对应面单。
- <strong>播种复核</strong>：总拣后需二次分拣时使用。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/b62b53f3-ca89-41b4-91d2-207c8ecdccd0.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=cIrt5gw2fBUHV8f2pmuzkTZOB2k%3D "")

<strong>批量复核</strong>：与普通复核的主要差别——有拦截订单需确认并踢出；完成一单后自动完成同波其他订单；不能拆包。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/5b7ebe4f-2622-4596-a2ed-359b3117547d.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=w%2FI8n2rA1kPWRwXt4CZ4ue663Xo%3D "")

如果开启了"复核并称重"参数，则在复核结束后立即进入称重环节。

#### 复核详细流程表

| <strong>序号</strong> | <strong>流程</strong> | <strong>页面</strong> |
|----------|----------|----------|
| 1 | 打开普通复核，扫描复核台编码1，进入复核页面 | 复核页面 |
| 2 | 关联打包员，输入打包员账号（非必须操作） | |
| 3 | 扫描单据：后置打单可扫任务号/容器/波次号/包裹号（需在波次管理打印面单） | |
| 4 | 逐件扫描货品：如需拆包则扫描后点击拆包；如缺货则点击缺货打印；如货品错误则换货 | |
| 5 | 扫描包装方案/包材/耗材：扫描包裹后带出推荐方案，可扫描指定方案或包材耗材 | |
| 6 | 可在复核环节点击"更换"来更换首末仓包装方案 | |
| 7 | 复核环节右上角功能键操作 | |
| 8 | 如复核环节有被拦截订单需返架，弹窗提示根据要求操作 | |
| 9 | 如开启了复核并称重，则自动进入称重环节 | 称重页面 |
| 10 | 如后置打单则自动打印面单 | |
| 11 | 操作打包 | |
| 12 | 贴单，结束 | |

#### 称重

连接蓝牙称重设备，选择称重设备自动读取重量数据。扫描包裹面单自动提交称重结果。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/8fd1bb00-c342-4aea-9956-ae76b031bb86.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=HAGLQHhZJhomK0aIL6f58mVi8dw%3D "")

<strong>批量称重</strong>：仅针对批量波次，称重一单后整个波次完成。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/e922867f-fbb9-4a14-ab63-bded5c7ab549.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=x0CCV3dCzRmdKoPM10T1XrrsXDU%3D "")

#### 发运

根据作业流程配置，称重完成后自动发运。发运后包裹状态变为已发运，完成出库闭环。

#### 拦截

拦截单系统确认有两种方式：系统操作触发确认。订单拦截后进入异常单管理列表，异常确认后取消订单；如已下架则进入回库明细列表，回库后确认。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9170f6ad-d1c0-43d9-a0f6-0de817fd4456.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Tx7LdaerrYmnVpkVVrL8sOi7jk8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/74d1804a-c053-4622-9ac7-da118a1ee3b8.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CDWhoa%2Fft%2FdkgOqWJKmzU1biXeE%3D "")

#### 拦截节点说明

| <strong>拦截节点</strong> | <strong>拦截后操作</strong> |
|----------------|-------------------|
| 加入波次前 | 直接拦截成功，订单不会进入波次 |
| 待拣货 | PDA拣货时提醒异常单，确认后踢出；PC拣货确认后触发确认异常单，确认后回库 |
| 待复核 | 复核触发，创建异常单→异常单确认→创建回库明细→回库确认→库存返架 |
| 待称重 | 称重触发，创建异常单→异常单确认→创建回库明细→回库确认→库存返架 |

以下为出库环节补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/b6a66f24-7af0-4adc-8a35-4c7b47442688.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=IezUEfKlKrgYoGnhBCq2ysIvGwA%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/c2bbe778-c3d7-4126-af01-4b67a3e49c32.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=trR5KmTu1T%2BVbXRsTYIRubXcKLg%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/91382484-7027-4158-b914-6254748efd45.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=N%2F96FALh8%2BvTEGlkFNqNAIrViN0%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9e219f19-2188-4edf-9605-861b223b0713.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=h%2FhimAMqKWuWf%2BfUUKLItGKk%2FkY%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/a8fb8573-04e8-4927-938c-ef483a356c0c.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lnPKajyrkuM8YFd%2FUXI2V8%2BiN8o%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/611e96fd-fac0-4c4f-946f-458686203284.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=yIG9pTF7qV5RoIFzmU8i34tbXu4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/e6f625aa-d9e5-459f-866e-df7ba71abcf3.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=oGwAUlw%2FhvCD9T3TzrD%2BibDnXa8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/2a1e89d3-7bae-4285-b900-990878336c3a.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=h4drs2er7uSKrFnlje%2FWsRJehV4%3D "")

### 规则配置

#### 承运方案

<strong>系统功能路径</strong>：配置 → 承运方案

承运方案定义包裹应分配到哪个承运公司、使用哪个账号、哪种物流产品类型、哪些增值服务。选中包裹后系统根据承运方案配置规则自动匹配承运公司+账号+产品类型+增值服务。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ae6b2c4d-3012-4046-9210-83aac7f718e5.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=GsgvYCpqmDXU4VC6%2BpofFnbj%2FDw%3D "")

#### 拆包规则

<strong>系统功能路径</strong>：配置 → 拆包规则

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/1703195c-e73d-4a58-8b10-62f2b04c3ce2.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=oL91iJMpjDuFbVczTCjExHboWaU%3D "")

拆包规则定义包裹自动拆分的条件：①按重量（超出设定重量自动拆包）；②按体积（超出设定体积自动拆包）；③按组合货品（需在"组合货品"中配置，包含货品组合则自动拆出为新包裹）。

#### 组合货品

<strong>系统功能路径</strong>：配置 → 组合货品

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/6fd907a1-5295-4551-8931-b221930d57ba.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4fYbAqJSMW6lN357iTDpjRrH91E%3D "")

组合货品定义哪些货品组合在一起应作为一个独立包裹出库。配置组合货品后，拆包规则中"按组合货品"拆包才会生效。每个货主可配置多个组合货品方案。

#### 包装方案

<strong>系统功能路径</strong>：配置 → 包装方案

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/2d007502-3073-4df9-8728-45451e287f49.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Vp0wuICI9tyYAQ%2BQ99y4cmXMZE4%3D "")

包装方案定义包裹使用的包材和耗材组合：

- <strong>所属货主</strong>：选择"仓库货主（共用）"，目前所有包材耗材库存挂在其下。
- <strong>包材</strong>：选择主包材（最外层包材，不含耗材）。
- <strong>填充率、最大承重</strong>：用于推荐箱型，目前功能未上线，填1、1000即可。
- <strong>辅助包材、耗材</strong>：除主包材外所需的其他材料。
- <strong>是否自动扣减库存</strong>：需扣库存选"是"。
- <strong>可用货主</strong>：选择全部货主/自定义货主/所属货主。

#### 指定包装方案

<strong>系统功能路径</strong>：配置 → 指定包装方案

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/5d3348dc-412d-453b-a2e1-c9b3fd216214.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Mcuqr6DqkKYRrc4plN09%2BXkOfFs%3D "")

为特定货品组合推荐指定包装方案。包裹包含该货品组合时，系统优先推荐此处指定的方案，而非推荐策略计算的结果。

#### 推荐包装方案策略

<strong>系统功能路径</strong>：配置 → 推荐包装方案策略

定义满足条件的包裹应使用哪些包装方案。拆包策略：按重量（大于该值则拆出直到不能再拆）；按组合货品（需配合"组合货品"使用）。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/af274a84-3a5e-49f9-948f-2b04fa90602f.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ZuCrmCPKCYDJPt%2BP%2B6NFev37Thg%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/2236df52-29e6-44bf-b00a-663b7c3e0a51.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Rv2n9mKpLwCSwAp2EwudIQ5ZfyQ%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/8b7d8623-c192-4682-aa96-0fd9cab41370.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=w9%2FPVA3SbyQ%2FCFgtg2lv1GxIlWI%3D "")

### WCS打印配置

WCS（Warehouse Control System）是WMS的打印客户端软件，用于打印面单、拣选单、上架单、盘点单等各类作业单据。

#### 下载安装WCS客户端

下载安装WCS客户端程序 → 安装插件 → 双击桌面图标启动。确保右上角显示"已连接"标识，才可正常打印面单。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/e6891142-3fb5-4282-84ec-e805994ef822.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=QL3LnqvqiKy6P8AaoSmufwDfw38%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/2d80a2c9-ddba-411c-834f-15807cf10efc.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Ro5addes1lIE9Av9t3XnhVXUiAs%3D "")

#### 打印管理

首次使用WCS配置：①下载打印模板（PC端更新后需下载到WCS）；②将模板指向打印机并保存设置（不指向则每次弹窗手动选择打印机）。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/af8de4b7-8736-42a8-86fd-78cc9935d67c.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zcT%2BeKOQaLhavXoef3OTlRusu0w%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/23482caa-932e-4cf4-a07b-22a793de462b.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=5DacFEQpmntiVS%2FWASsGGcDgNhU%3D "")

### PDA-APP安装

PDA-APP是WMS手持终端应用程序，用于移动收货、上架、拣货、复核、称重等操作。

#### PDA-APP安装步骤

12. 在PDA上打开浏览器，光标定位到浏览器输入框。
13. 扫描PC端显示的下载二维码，开始下载APP安装包。
14. 安装完成后，使用创建账户时短信中的账号密码登录APP。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/a9249f29-6c2a-4e39-97c1-098a4b9169d4.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=XNM3V%2F5aq%2FD%2FS40H4VMW9gq%2BNt8%3D "")

#### 创建自定义导出模板

仓库如需自定义导出模板，通过"配置-导入导出模板"新建属于自己的模板。可自定义导出的字段、格式和排序方式。

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/774dc638-0e17-40f6-9984-77511c00bbc2.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6XCrFgoh25JyNEHxGr1RCOATDGE%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/48935247-cfc5-4c64-9bf8-3cfd52918022.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=BKBHLhbXq6Zotaw17XUtsISRWAM%3D "")

### 操作视频

为帮助仓库人员更直观地理解系统操作，提供了视频教程：

[仓库WMS实操培训.mp4](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/att/f632d7f7-0550-4b1e-8379-db8800496506.mp4?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=saBE%2FfDnihQYn6Cd62A7JlSz3%2BA%3D)

相同视频的优酷地址：[中通冷链WMS实操培训](https://v.youku.com/v_show/id_XNjQ0Njc3NTc0OA==.html)

建议仓库新员工先观看视频教程，再结合本文档进行实际操作练习。视频涵盖创建库位、创建SKU、入库收货上架、出库拣货复核称重发运全流程演示。

以下为操作视频及补充截图：

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ef981c48-ab75-4acc-adef-451da71869bf.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=KDTtPkJnLaILw3QOSNV5t8Yv1t8%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/24a3ee98-1e09-4e2c-86a1-90984b19a2cd.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=XOCuZ3E%2FEKGzF%2Ba2UL%2Fvxko%2BFOE%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/454994b6-846c-475d-9126-9626f7e2adfb.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=vphgV%2FTPMwtzfHDkElMSxCO5vjo%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/09d16d02-d46f-464e-b32c-8986132b5708.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=UWzKUTHGt2PhEkxDpAwgNUYS4%2B4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/66f8e6a9-535f-4f19-8a23-6ef5b02e9337.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=noY8nWzgnXtwW1MaIjzYFjcneXI%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/c648cff1-5b0c-487f-b4b3-91f2fe208c2a.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=gdEW710li21%2Fz%2BZk3ipq2M40fTA%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/c7daceab-526f-4bde-a2a8-5be961123f6b.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=IbDhLAHCrnJzs04EdOZpjjoObKw%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/4ec0366e-8752-4b77-b17d-fbbbff9f7956.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=oU7ws7xwAdxM8YLNREjlQ%2BHzNTM%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/f8dca7fa-3ab3-4d3e-81ab-5c9e5accf499.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=p%2FCP%2FvJ3zTiSlVo%2BweCqEbilsL4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/ee603b57-3bd6-487a-8802-8f57be84a2a5.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CMhOFqeAzZEqlFkCph%2BaRACbuN4%3D "")

![](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/1wvqrebRp41genak/img/9c054ff0-25f8-4d96-95c9-d273734e52dd.png?Expires=1783781689&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ZpHLqaCKYdp3S%2BcaoYYVyWZBEuI%3D "")

## 常见异常与兜底方案（卡住了怎么办？）

| <strong>序号</strong> | <strong>异常现象</strong> | <strong>常见原因</strong> | <strong>解决方案</strong> |
|----------|----------------|----------------|----------------|
| 1 | 收货时无法扫描货品条码 | SKU档案中未维护条码 / 操作配置中校验开关限制 | 检查SKU档案中条码字段；检查【配置-操作配置-收货】中扫描校验设置 |
| 2 | 收货后没有生成上架任务 | 定位规则未配置或定位条件未关联 | 检查【配置-定位规则】和【配置-定位条件】，确保入库单据类型关联了定位规则 |
| 3 | 上架任务无法领取 | 任务已被分配给其他用户 | 在PC端取消任务分配，或由已分配用户执行。也可取消任务后重新创建 |
| 4 | PDA收货无法批量完成扫描 | SKU需要采集批次/效期属性 | 需采集属性的SKU不允许批量完成扫描，需逐条录入属性信息后提交 |
| 5 | 上架时库位不足 | 库位容量已满且未开启忽略容量 | 在库位管理中开启"忽略容量"选项，或手动将库位类型切换为"库存"类型 |
| 6 | 出库包裹取号失败 | 承运商配置未生效 / 账号余额不足 / 物流产品未开通 | 在【包裹汇单】页面筛选取号失败原因，检查承运商配置后一键重新取号 |
| 7 | 波次无法释放 | 波次中订单状态异常 / 前置打单未完成 | 检查波次详情确认所有订单状态正常；如为前置打单波次需先完成打单 |
| 8 | 复核时无法扫描包裹 | 复核台未配置或状态异常 / 容器类型未关联工作台 | 检查容器类型→基本类型→工作台→使用环节→出库配置 |
| 9 | 称重读数不准确或无法读取 | 蓝牙秤未正确连接 / 称重设备未选择 | 重新连接蓝牙设备，在称重页面确认选择了正确的称重设备 |
| 10 | WCS打印客户端显示未连接 | WCS服务未启动 / 网络连接问题 | 重启WCS客户端，检查网络连接，确保防火墙未拦截WCS端口 |

## 高频常见问题（FAQ）

15. <strong>Q1：PC收货扫描和PDA普通收货有什么区别？</strong>

<strong>A</strong>：功能上基本一致，都支持按件/批量扫描。差异在于：PC端适合仓库办公桌旁的集中收货场景；PDA端适合移动收货，支持快速上架（收货后立即上架）。大仓库推荐PDA操作，小仓库PC端即可满足需求。

16. <strong>Q2：什么时候使用上游推单，什么时候手动建单？</strong>

<strong>A</strong>：上游OMS已对接的情况下统一使用接口推单，保证数据一致性和可追溯性。手动建单仅用于客户未对接系统的应急场景。

17. <strong>Q3：收货记录为什么会拆分成多条？</strong>

<strong>A</strong>：系统根据库存属性（批次、批号、效期）和SKU档案的一级单位托规自动拆分。同一SKU不同批次会拆成多条记录，对应多条上架任务和库位库存明细，保证库存维度精确。

18. <strong>Q4：取消上架任务后会怎样？</strong>

<strong>A</strong>：取消任务后，关联的收货明细被重置为"待定位"状态。可在"入库-收货记录"页面手动重新定位库位并创建上架任务。

19. <strong>Q5：批量波次和散单波次应该怎么选择？</strong>

<strong>A</strong>：先筛选货品结构一致的订单加入批量波次，可享受批量拣货/批量复核/批量称重的效率优势。剩余货品结构无规律的订单加入散单波次，走边拣边分流程。

20. <strong>Q6：什么情况下使用货找单复核？</strong>

<strong>A</strong>：适用于单品单件混品的散单波次 + 后置打单场景。每个包裹只有一品一件但SKU不同，扫描一件货品即出一个对应的面单。

21. <strong>Q7：出库包裹页面系统自动处理不准确怎么办？</strong>

<strong>A</strong>：所有自动操作均支持手动重置和变更：手动拆合包、指定承运商、变更作业流程、重新获取面单、指定包装方案。系统会记录手动指定的包装方案供后续推荐使用。

22. <strong>Q8：WCS打印配置中模板不指向打印机会怎样？</strong>

<strong>A</strong>：每次打印时会弹窗预览让用户手动选择打印机，影响效率。建议将所有使用的模板指向对应打印机并保存设置，实现一键打印。

23. <strong>Q9：PDA拣货时如何提升效率？</strong>

<strong>A</strong>：①在加入波次环节将批量单加入批量波次；②在PC端提前分配拣货任务给特定员工；③在"操作配置-拣货"中合理设置校验规则，避免不必要的校验步骤。

24. <strong>Q10：拦截后订单怎么处理？</strong>

<strong>A</strong>：拦截后订单进入异常单管理列表。异常确认后取消订单；如已下架（待复核/待称重拦截），则创建回库明细，回库确认后库存返架。
