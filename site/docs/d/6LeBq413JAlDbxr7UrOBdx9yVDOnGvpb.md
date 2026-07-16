---
title: "大客户-个人下单"
description: "大客户-个人下单的操作说明。"
---

# 大客户个人下单

## 一、适用场景

本文适用于中通冷链运营人员、合作大客户，通过 **鲸天系统**、**中通冷链客户服务平台**、**中通冷链微信小程序** 完成大客户个人下单相关操作。

主要支持以下场景：

- 开通、绑定、管理 **电子面单账户**
- 申购 **客户主单**
- 为电子面单账户 **充值**
- 客户服务平台单个下单、批量导入订单、面单打印
- 微信小程序下单、查件、订单跟踪
- 查询订单、物流轨迹、打印日志、回单状态等信息

## 二、前置条件

1. **账号与权限**
   - 已拥有 **鲸天系统**、**中通冷链客户服务平台** 的登录账号。
   - 账号需具备 **大客户操作权限**、**电子面单管理权限**。
   - 如无权限，请联系系统管理员开通。

2. **电子面单账户准备**
   - 客户需已开通或可创建 **电子面单账户**。
   - 需提前向线下网点获取 **客户编码**、**客户密钥**，用于绑定电子面单账户。
   - 未绑定电子面单账户时，可能无法正常下单或打印面单。

3. **打印环境准备**
   - 电脑端需提前安装 **打印组件**，否则无法打印电子面单。
   - 需配备常规打印机，并支持电子面单打印。
   - 打印组件可在页面内点击 **【下载组件】** 安装。

4. **系统与入口**
   - 鲸天系统登录入口：**中通冷链后台系统**
   - 客户服务平台入口：**中通冷链官网客户端**
   - 小程序入口：微信搜索 **「中通冷链」**

## 三、操作入口

- **鲸天系统 > 经营管理中心 > 商户电子面单账户管理**
- **鲸天系统 > 经营管理中心 > 电子面单申购**
- **鲸天系统 > 经营管理中心 > 商户电子面单账户**
- **中通冷链客户服务平台 > 首页 > 大客户下单**
- **中通冷链客户服务平台 > 基础配置 > 电子面单账户管理**
- 微信搜索 **「中通冷链」** 小程序

## 四、名词解释

- **电子面单账户**：客户在系统内用于绑定、使用冷链电子运单的专属账户。下单、打印面单需依赖该账户。
- **客户主单**：大客户统一申购的基础电子面单额度。完成主单申购后，才可给对应客户账户充值面单。
- **批量导入下单**：针对大量订单，通过 Excel 模板批量上传完成下单，**单次最多支持 500 条订单**。
- **待处理订单**：已提交或导入，但未完成下单、打印的订单，可执行 **仅下单**、**下单并打印** 操作。

## 五、操作步骤

### 5.1 电子面单账户新增与管理

操作路径：**鲸天系统 > 经营管理中心 > 商户电子面单账户管理**

#### (1) 绑定现有客户电子面单账户

1. 进入 **商户电子面单账户管理** 页面。
2. 根据 **商家ID** 或客户信息检索客户。
3. 找到对应客户后，点击 **【绑定客户】**。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/a629441c-ee78-43ef-9a52-682d26e31e95.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=NICHSR8u%2BNgJu1L8MPFg7y5kvqA%3D "")

::: tip 说明
单个客户可绑定多个电子面单账户，客户手机号可与开户手机号不一致。
:::

#### (2) 绑定其他客户

1. 输入 **商家ID**、**客户名称/手机号** 查询客户信息。
2. 选中目标客户。
3. 完成绑定。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/a2d2990a-18d6-43d5-896d-a8d8c540253a.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=p0D145SA7Skjcr0FkHLFK5JEm8Q%3D "")

#### (3) 创建新客户和电子面单账户

1. 在页面选择 **【创建新客户】**。
2. 填写客户基础资料。
3. 保存后，系统将同步生成全新电子面单账户。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/4a4792d7-9a0d-4e4e-92d9-e1eb28e73eda.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=2EVyePwIL1syaLwyeBlmH9nCeAs%3D "")

### 5.2 申购客户主单

操作路径：**鲸天系统 > 经营管理中心 > 电子面单申购**

::: danger 重点提醒
**必须先申购客户主单，才能为客户电子面单账户充值。**
:::

1. 进入 **电子面单申购** 页面。
2. 选择 **客户主单**。
3. 按页面要求提交申购。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/4b4e9744-58ad-4515-bdca-c9fd44efa606.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=QL%2F2CqZu%2F6mIGT6e3Cdxkx6vtY0%3D "")

### 5.3 电子面单账户充值

操作路径：**鲸天系统 > 经营管理中心 > 商户电子面单账户**

1. 检索目标客户账户。
2. 在操作栏点击 **【充值】**。
3. 填写充值数量。
4. 核对信息无误后，点击 **【保存】** 完成充值。

::: tip 说明
订购来源为 **中通冷链** 时，充值额度均为 **客户主单**。
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/5b3474c9-25ba-4a82-b345-89c64a374bff.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=TBV5ISj7Is3u3ItdFEKILZ7q1IA%3D "")

### 5.4 多端绑定电子面单账户

::: danger 重点提醒
绑定前需从线下网点获取 **客户编码**、**客户密钥**。未绑定账户可能无法正常下单。
:::

#### (1) 客户服务平台绑定

1. 登录 **客户服务平台**。
2. 进入 **【基础配置】>【电子面单账户管理】**。
3. 点击 **【绑定电子面单】**。
4. 填写编码与密钥。
5. 提交绑定。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/256a6fc8-ff49-43b0-b840-bc029a1c23f0.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=260uapzY3d0PGV514bss3uvB8Bo%3D "")

#### (2) 微信小程序绑定

1. 微信搜索进入 **「中通冷链」** 小程序。
2. 进入 **【电子面单账户管理】**。
3. 选择 **【绑定电子面单账户】**。
4. 输入 **客户编码**、**密码**。
5. 确认绑定。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/93a1085c-1c8c-4896-8e8a-73cd74127313.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=fi2zA4XdB%2Bfg5Kcq4xPZVajttKk%3D "")![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/10a1d4ae-09c9-4642-b384-b60efc0e2ffc.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=2c8nbXUoCSnrmr6Ikh07XNLaM18%3D "")

### 5.5 客户服务平台大客户下单

操作路径：**中通冷链客户服务平台 > 首页 > 大客户下单**

页面模块包括：**新增下单**、**批量导入**、**待处理**、**已处理**、**全部订单**。

#### (1) 单个订单下单

1. 进入 **【新增下单】**。
2. 填写寄件人、收件人信息，可选择以下方式：
   - 从 **地址簿** 选择已有地址，系统自动填充。
   - 粘贴完整地址，系统智能识别姓名、电话、省市区。
   - 手动录入全部信息，可勾选 **“保存到地址簿”**，方便下次使用。
3. 如需长期使用同一寄件地址，可设置 **默认寄件地址**，后续下单自动填充。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/795a39f6-522d-4221-808d-7156f5cc5b1c.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=5aYZwe0sBNA06nL%2BrOP8zSi1mek%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/5ef7bdba-2220-4e4b-b58f-7cf607372546.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=A5WV2pmEyFjkPV6hVisE4OYXVXw%3D "")

4. 填写托寄物信息：
   - 选择物品类型，也可自定义新增品类。
   - 选择温区：**冷藏(0-10℃)/冷冻**。
   - 选择是否为 **进口货物**。
   - 填写货物件数、总重量、总体积。
   - 按需填写收派员留言。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/f34e295d-6b16-4da7-96bf-405ad4e7e145.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=0%2FZoB7mxjQ1jJ2JElM%2FAH1E%2BCCQ%3D "")

5. 选择产品与增值服务：
   - 选择产品类型、寄派方式、派送方式。
   - 按需选择保价、增值服务。
   - 选择付款方式，默认 **寄付月结**，支持 **寄付现结**、**到付**。
   - 如有可用优惠券，可选择优惠券。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/b0ef7147-c8af-458d-96fc-8ff40aae6440.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Vy0ORJQO6dc%2FNaDpIErSvarSVAg%3D "")

6. 查看费用并提交订单：
   - 在页面查看预估费用及费用明细。
   - 勾选同意 **《电子运单契约条款》**。
   - 点击 **【保存】** 完成下单。
   - 如暂不提交，可点击 **【保存草稿】**，后续在草稿箱修改后再提交。
   - 下单成功后，可选择 **再寄一件** 或查看订单详情。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/8e11a4ae-07c9-4e33-aeac-3e3ebb6e21e6.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CoKtwVSLGUHBwt79rBN%2Biz%2FJ07E%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/6cc96c78-29d5-4fb1-a28e-c5d947741c51.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=T9iRKQLZLSyiZhDwnytY14ZsbTc%3D "")

#### (2) 批量导入订单

适用场景：订单数量较多，需要批量统一处理。

1. 进入 **【批量导入】** 模块。
2. 点击 **【下载模板】**，获取标准 Excel 表格。
3. 按模板要求填写订单信息。

::: danger 重点提醒
**单次最多导入 500 单**。超过数量时，请分批导入。
:::

4. 点击上传文件，或将文件拖拽至上传区域。
5. 点击 **【开始导入】**。
6. 导入完成后查看结果：
   - 导入失败：可下载失败列表，按提示排查并修正。
   - 导入成功：成功订单进入 **【待处理】** 列表。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/9a3ccefc-e2b9-4b34-ae93-1ba1201b54d6.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=b7UmvZoaX8IJzbNO9%2BomGRYQ3FQ%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/c9ec0f32-eece-4ec2-9c44-ae97e3b46099.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=26XzuIRuReGV3MbAyCALRlxYnr0%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/b45ea771-0598-43d8-8a9b-709de528e681.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=AFZGEHPQE8FjlZ%2FHq9fW7P6ncGg%3D "")

#### (3) 待处理订单操作

批量导入或单个下单保存后的订单，会进入 **【待处理】** 列表。

1. 如只需下单：
   - 选中订单。
   - 选择可用电子面单账户。
   - 点击 **仅下单** 完成下单。
   - 后续可到 **【已处理】** 列表打印。

2. 如需下单并打印：
   - 选中订单。
   - 选择电子面单账户。
   - 选择面单模板。
   - 选择打印机。
   - 点击 **下单并打印**，直接完成下单和打印。

::: warning 注意事项
如提示无可用余额，需前往 **鲸天系统** 为账户充值。

如提示未检测到打印组件，需点击页面 **【下载组件】** 并完成安装。
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/73a044b1-25e3-4522-b239-b6ea9c4c9322.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Lwu%2BKdk6fjQ05blZ1LZ2Btfkmqs%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/c39a8754-0420-465f-9e22-97231f0c0a7b.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=xRQScJFN3DXIEvDYUPmbAxd0APw%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/0ff80c31-da4d-4f2e-9eda-b47a6ad5cab6.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=8IlBoHLjMnMYEUZ9w%2FLlUiB5uTk%3D "")

#### (4) 已处理订单操作

1. 进入 **【已处理】** 列表。
2. 查看所有已下单订单的打印状态、运单号、费用等信息。
3. 如订单 **打印失败**：
   - 选中打印失败的订单。
   - 重新选择模板和打印机。
   - 再次执行打印操作，流程同 **下单并打印**。
4. 可按需执行订单导出、撤销操作。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/c63b3770-eb2e-4706-90ce-f869db97c31f.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=hbutf5g%2BODMrzN%2BoSYg%2BwxqclCE%3D "")

#### (5) 全部订单与查询

1. 点击 **【全部订单】**，跳转至 **【物流跟踪-订单查询】**。
2. 可查看 **订单基础信息**、**实时物流轨迹**、**回单状态**、**打印日志**。
3. 可依据运单号、时间、收件人等条件筛选订单。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/e5cc8c90-11d6-474e-886c-9edfc659fa03.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2BkMCfv5dpIcuoFgOSai2dYEAIqA%3D "")![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/30d590a2-b225-482a-8c0a-fd50ade652de.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=AGT6MywMMIiej%2BleFhGgAnhNTFk%3D "")![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/290e5956-5ac2-42f7-bf8b-729f0e392153.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=niAFu83vL6pLwMAcrAS%2Bs%2FZAH5c%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/88428df9-ffad-4bcc-8fa3-ff9a4a3ca9dd.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=w8K1tkrTlqgh%2FQpXhw%2FdK%2BfD4qw%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/351fcdaa-677a-4f47-993d-858d07125b5c.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zf0Fr6y%2BxDyT3RjQNOzSkqVTeBo%3D "")

### 5.6 中通冷链微信小程序下单

1. 微信搜索 **「中通冷链」** 小程序。
2. 使用手机号登录。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/6a5b27aa-bd16-418d-aee5-48fdfe7fef83.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=dvU8DuT2dlN0ETmpdiOZYxRRlBA%3D "")

3. 进入 **【冷链快运】**。
4. 选择寄件地址、收件地址。
5. 选择物品类型、温区、是否进口。
6. 填写件数、重量、体积。
7. 选择保价、增值服务、付款方式、期望上门时间。
8. 阅读并同意 **《电子运单契约条款》**。
9. 点击 **【立即下单】**。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/ba4f9a44-8582-40bc-87e2-cf556293e34e.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zauxm7JCtD0Y7AzJoUMNPy7Rbj0%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/01464faa-d346-4df3-bbc8-26ed8693a747.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=W9N1bLPPcapq9%2F%2BQMF2YGEAnJJE%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/68b7741c-54ab-450e-8810-305767e99c6e.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=8vPZiCQMmfMXfu5CZoK1mFUKWKk%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/54a15472-1394-4515-9ccd-1f5beb04bc59.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2BnFbuAxvDLlePfauv6M37Nw5ooY%3D "")

10. 如需跟踪订单，进入小程序 **【查件】** 页面。
11. 查看所有寄件、收件订单状态。
12. 打开运单详情，可查看物流轨迹、签收信息。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/QvjnA3jZX8D14OXo/img/697bc7ce-76c4-4805-ac1f-afd723b85198.png?Expires=1783781514&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=obZrrNhd76v%2Bf%2FVihNt%2Bz3KxV%2Bg%3D "")

## 六、操作结果

完成以上操作后，可获得以下结果：

- 电子面单账户已完成创建、绑定或充值。
- 客户主单已提交申购，并可在状态满足要求后用于充值。
- 客户可通过客户服务平台或微信小程序完成下单。
- 批量导入成功的订单进入 **【待处理】** 列表。
- 已完成下单的订单进入 **【已处理】** 列表，并可查看运单号、费用、打印状态等信息。
- 可通过 **【全部订单】** 或小程序 **【查件】** 查看订单状态、物流轨迹、回单状态、打印日志等信息。

## 七、注意事项

::: danger 重点提醒
- **必须先申购客户主单，才能为客户电子面单账户充值。**
- 电子面单申购存在审核流程，需等待状态变为 **「审核通过」** 后，再执行充值操作。
- 批量导入订单 **单次最多支持 500 条订单**，超出数量请分批上传。
- 未绑定电子面单账户，可能无法正常下单。
:::

::: warning 注意事项
- 客户编码、客户密钥需向线下网点获取，填写错误会导致无法绑定。
- 电脑端打印前需安装并启动 **打印组件**。
- 如提示无可用电子面单账户余额，需前往鲸天系统为账户充值。
- 如提示未检测到打印组件，需点击页面 **【下载组件】** 安装，安装后刷新页面重试。
:::

## 八、常见问题

### 8.1 常见异常与处理方案

| 序号 | ❌ 异常现象 / 报错提示 | 🔍 常见原因 | 🛠️ 解决方案 |
|------|-------------------------------|-----------------|--------------------|
| 1 | 下单提示：没有可用电子面单账户余额 | 电子面单账户额度已用完 | 1. 进入鲸天系统商户电子面单账户管理；2. 找到对应账户执行充值操作 |
| 2 | 下单并打印：未检测到打印组件 | 未安装/未启动打印组件 | 1. 点击页面【下载组件】完成安装；2. 启动组件后刷新页面重试，仍异常则重启电脑 |
| 3 | 批量导入失败 | 1. 表格格式与模板不符；2. 填写信息有误；3. 单次订单超500条 | 1. 下载失败列表核对错误项，修正表格；2. 订单过多时分批导入 |
| 4 | 无法绑定电子面单账户 | 客户编码、密钥填写错误，或账户未开通 | 1. 联系线下网点核对正确的编码与密钥；2. 确认账户已正常开通 |
| 5 | 找不到目标客户/商家ID | 账号权限不足、信息输入错误 | 1. 核对商家ID、手机号、客户名称；2. 联系管理员补充查询权限 |

### 8.2 为什么申购完主单，还是无法给客户账户充值？

电子面单申购存在审核流程，需等待状态变为 **「审核通过」** 后，再执行充值操作。

### 8.3 小程序和电脑端的订单数据是否互通？

数据完全互通，两端均可查询订单、物流轨迹与打印记录。

### 8.4 批量导入订单有数量限制吗？

有。单次批量导入最多支持 **500 条订单**，超出数量请分多次上传。

### 8.5 面单打印失败后，如何重新打印？

进入 **【已处理】** 订单列表，选中打印失败的订单，重新选择模板和打印机后再次打印即可。

### 8.6 忘记客户编码和密钥该如何处理？

直接联系为您开通电子面单的线下网点工作人员查询。

### 8.7 客户可自主下单的方式有哪些？

客户可通过 **中通冷链小程序**、**客户服务平台 PC 端**、**扫码下单小程序** 自主下单。