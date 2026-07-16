---
title: "网络货运货主下单"
description: "网络货运货主下单的操作说明。"
---

# 网络货运货主下单

## 一、适用场景

货主注册后，需要在**中通冷运网络货运平台**下整车订单时，可参考本文完成录单操作。

## 二、前置条件

- **账号与权限要求**：权限角色需包含**中通冷运租户权限**，例如：**网点/省公司**。若无权限，请联系系统管理员。
- **设备与环境准备**：准备一台可以联网的电脑，建议使用 **chome 浏览器**。
- **系统登录入口**：[https://zc.ztocc.com/dashboard](https://zc.ztocc.com/dashboard)

## 三、操作入口

登录系统后，按以下路径进入：

**顶部 tab 切换至【中通冷运】 -> 左侧边栏【货源管理】 -> 【货源订单】 -> 【整车订单】**

## 四、操作步骤

1. 填写**发件信息**和**收件信息**。

   需要填写发件/收件的**联系人**、**联系方式**、**省市区**和**详细地址**。

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/a2QnV4jGdGYZ8O4X/img/2b752b5c-446d-4eba-9515-49bedbed69e5.png?Expires=1783781797&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=9RlYVFRvGaN%2FQAjMYVqNKX5d4As%3D "")

2. 填写**服务信息**。

   主要填写**装货时间**和**卸货时间**，用于考核司机到达装货地和到达卸货地的时间；同时填写需要的**车型**以及**温度要求**。

   - **司机调度**：如果有常用司机，或线下已约定好司机，可直接派单给司机，不需要等待司机抢单。
   - **移动设备**：主要用于司机没有温控设备的场景。货主如果能提供便携温控设备，也可以提供给司机绑定，用于监控温度和轨迹。
   - **保证金**：用于货主担心司机爽约、要求司机缴纳保证金的场景。保证金一般在 **20-500 元**之间，运单完成后会退还给司机。

   ::: warning 注意事项
   货主自己的温控设备需要进行单独授权。
   :::

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/a2QnV4jGdGYZ8O4X/img/06e02932-fb11-40cd-84d0-d056119e756c.png?Expires=1783781797&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zpRLVQdrQqpRnSgQdQBqA5z5Uls%3D "")

3. 填写**货物信息**。

   需要填写**货物类型**、**包装类型**、**重量**、**体积**和**件数**。

   ::: danger 重点提醒
   **货物重量不要超过所选车型的最大额定载重重量**（**4 米 2**除外）。
   :::

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/a2QnV4jGdGYZ8O4X/img/cbf7a431-d0a8-460c-af71-3eb94b6b70eb.png?Expires=1783781797&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Vybkw8GudgDp4JCklMHvF7kaB7M%3D "")

4. 填写**财务信息**。

   - **支付类型**：目前仅支持**预付款**，后续会开启**现付**。
   - **开票**：由于目前承运平台不管货主开不开票，平台都会开票，所以目前仅支持**开票业务**。
   - **运费录入**：请录入**不含税运费**。
   - **平台服务费**：平台向货主收取的服务费，根据货主单量不同，比例不同，目前最大为 **5%**。
   - **保价**：平台会给每一单购买货险，按照保价金额（即货物价值）的**万分之五**收取。

   ::: danger 重点提醒
   **运费录入请录入不含税运费！！！**

   为了保障货主货物的安全，请足额按照货物价值填写**保价金额**。
   :::

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/a2QnV4jGdGYZ8O4X/img/953d8d13-11d4-451e-86ce-41714a6480f8.png?Expires=1783781797&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=45d9Rm6Kx%2FhrOXjrl89xJLttRJE%3D "")

5. 点击**【保存】**完成下单。

   系统会自动扣除**预付款账户余额**，并生成一份运输合同，视为平台确定承运。下单成功后会生成**订单号**。

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/a2QnV4jGdGYZ8O4X/img/d256c613-6ddf-4bbd-8165-254ef5bc5e17.png?Expires=1783781797&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=47pm2JIj0%2BFuagfdBbZr059l9tI%3D "")

## 五、操作结果

点击**【保存】**后：

- 系统自动扣除**预付款账户余额**。
- 系统生成一份**运输合同**，视为平台确定承运。
- 下单成功，并生成**订单号**。

## 六、注意事项

- **货物重量**不要超过所选车型的最大额定载重重量（**4 米 2**除外）。
- **支付类型**目前仅支持**预付款**，后续会开启**现付**。
- **开票**目前仅支持**开票业务**。
- **运费录入请录入不含税运费！！！**
- **平台服务费**根据货主单量不同，比例不同，目前最大为 **5%**。
- **保价**按照保价金额（即货物价值）的**万分之五**收取，请足额按照货物价值填写。
- **保证金**一般在 **20-500 元**之间，运单完成后会退还给司机。
- 货主自己的温控设备需要进行单独授权。

## 七、常见问题

| 序号 | ❌ 异常现象 / 报错提示 | 常见原因 | 解决方案 |
|------|----------------------------------|------------|--------------|
| 1 | 提示“货物重量超过车辆载重" | 货物重量＞所选择车型的最大载重 | 请更改货物重量 |
| 2 | 提示“余额不足" | 预付款账户余额不足，扣费失败 | 前往账户管理进行充值 |

- **Q1：我的便携式温控设备如何授权？**
- **A**：详情请点击[三方温度设备授权方法](https://docs.qq.com/doc/DZW5IbnJETXhqdlpP)