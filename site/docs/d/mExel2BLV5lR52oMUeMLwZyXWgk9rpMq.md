---
title: "业务员码设置"
description: "业务员码设置的操作说明。"
---

# 业务员码设置

## 适用场景

当网点需要通过**业务员编码**区分派送区域、辅助司机识别“哪些运单由谁派送”时，可参考本文进行业务员围栏设置。

当前可解决：

- 派件太多时，司机可通过**业务员编码**区分派送运单。#本期内容
- 货太多时，司机合理规划先后排线。#即将上线[暗中观察]
- 揽件太多时，自动指派司机揽件。#即将上线[暗中观察]

## 前置条件

- 已具备系统登录账号，并有查看或维护**网点业务员围栏**的权限。
- 已确认需要设置业务员编码的网点范围。
- 建议提前规划网点派送区域需要拆分成几部分，以及每个区域对应的业务员编码。

::: warning 注意事项
当前系统中，**业务员编码未和司机任务强关联**，需要线下口头约定编码与司机的对应关系。

例如：**李四对应 02**。

后续会结合司机任务进行关联处理。
:::

## 操作入口

系统菜单路径：**经营管理中心 > 地址管理 > 网点业务员围栏**

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/e76340e6-3d3f-4961-9365-ac86676aae73.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=XwAbFpLalw1%2F4jsO5hm10qWtbqw%3D "")

## 业务员编码在哪里看

业务员编码可在以下位置查看。

### 三段码最后 1 位

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/4maOgk5G3b6XOWNX/img/de99dfc1-5afe-47b2-81f0-124a1e8b4a14.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=nIDj1ihY4YDhs8BngQ9groD2fOE%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/3122e8e8-d81c-440a-8df7-f8133369d412.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=NXiTpUtJcaf4c9bKCNoD0A8pHmU%3D "")

### 快件跟踪或运单详情中

可在**快件跟踪**或**运单详情**中查看业务员编码。

## 业务员编码怎么用

业务员编码主要用于线下识别司机与派送区域的对应关系。

::: tip 示例
可线下约定：**02** 对应司机**李四**。司机看到运单上的业务员编码后，根据约定判断是否由自己派送。
:::

::: warning 注意事项
当前系统中，业务员编码还未与司机任务强关联，需要线下判断。后续会结合司机任务进行关联处理。
:::

## 操作步骤

### 查看网点业务员围栏

1. 进入系统菜单：**经营管理中心 > 地址管理 > 网点业务员围栏**。
2. 点击**网点业务员围栏**。
3. 登录后，可查看**本网点及下属网点**的围栏信息。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/b9727ba3-eb3b-4478-88d1-530f834cb579.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=jNqMdpA5lgzGAuC5nDv5zXuHX8I%3D "")

图例说明：

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/e19e5541-6d67-435f-b41b-78c4eebfeca8.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=%2B7yaYtgs4qgyDdf%2Fn69MVUPmlGA%3D "")

交互说明：

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/4621cacc-d30b-45d0-9e7e-a4790364ddc0.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ONPdVa%2FYOTqPUtcj9gcZqDGs0P4%3D "")

### 进入围栏勾画页面

1. 点击**勾画业务围栏**图标。
2. 进入围栏勾画页面。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/19f82bec-2614-4444-a78d-07f1da7860f6.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=n84XzxiJhe2%2BRmjWC19PKqK3w1I%3D "")

### 添加派件业务员围栏

1. 在围栏勾画页面，点击**添加**按钮。
2. 进入派件业务员围栏初始化界面。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/f0f9707e-0fe7-4bbf-b392-cc6caee75c51.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=1B82Yw7Dsx98hbm635NFfsVenww%3D "")

::: tip 💪 初始化围栏方式
初始化围栏支持以下方式：

- **自由绘制**：在网点范围内，自由绘制业务员围栏。
- **复用网点围栏图层**：复用网点围栏图层，适用于之前网点在勾画围栏时，已经将区域用图层区分的场景，例如某些三方合作商。

网点可按需选择初始化方式，也可以结合使用。前期建议使用**自由绘制**。
:::

::: warning 注意事项
绘制前，建议先思考本网点大概要分为几部分。

如果司机不固定、人数不固定，需要先把变动区域的最小部分勾画出来。

例如：司机每日可约定配送不同编码的区域。
:::

### 自由绘制业务员围栏

1. 选择**自由绘制**方式。
2. 在网点范围内绘制业务员围栏。
3. 设置对应的业务员编码。
4. 完成后点击**应用**，使配置生效。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/33c914b7-9333-4938-b2ec-31dc907f91fb.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=K61j5IY4ltrx8lS41X0b5vt%2Bpc0%3D "")

::: danger 重点提醒
业务员编码**不允许重复**。上面图片中的重复编码示例是错误的。
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/70a3dd64-6c01-4cb0-97f7-dadb1ee4731e.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=WA9EAimuEQpvrntHCFaJvwTGVCM%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/83b60351-d6be-4393-996e-f864907f69e5.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=dTM4FWpPhOSdg3OB9UYvgbyUVgY%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/15fd4fd1-0c87-48d6-a6ff-4d1e88980052.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=8WBrAbiO570mRz1zTMyR54BpyHM%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/0d90f05f-b15b-4ca5-9299-05eac1826886.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=MOAc1jw1LZTX887NDLneK2GxdNs%3D "")

配置完成后，派件地址在此区域的订单，业务员编码为 **01**。

::: danger 重点提醒
点击**应用**后立即生效。

点击**重置**，会回到上次点击**应用**时的状态。
:::

### 复用网点围栏图层

1. 选择**复用网点围栏图层**方式。
2. 按页面提示选择需要复用的网点围栏图层。
3. 设置对应的业务员编码。
4. 完成后点击**应用**，使配置生效。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/6fac9f9e-1577-46f9-9475-d2063c277933.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=6YSOBq6ed%2FQs6N%2BkrjTMFyvbJWE%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/0114d2e9-f54c-4614-9c7a-cdc2744deb81.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=PxpmFMElSxlTlrBlXjVAhbRmIvU%3D "")

### 修改已有图层

1. 找到需要修改的业务员围栏。
2. 点击对应围栏的**编辑**图标。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/ced6fcaa-b528-4c18-9ee7-82d0a3d18935.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=xE%2BFXC39HjbSnPCB%2F2EFxx%2F4j28%3D "")

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/fca5c653-418b-4dfb-bad4-717414c635fd.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=pOxD1AiX5mz6gpk8WN53zQxXjh0%3D "")

3. 点击**开始绘制**，补充该业务员的围栏。
4. 完成后点击**应用**，使修改生效。

::: warning 注意事项
编辑已有图层时，仅支持**自由绘制**。
:::

### 修改编码

1. 找到需要修改编码的业务员围栏。
2. 修改业务员编码。
3. 点击**应用**，使修改生效。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/8d1461cd-de38-4e0f-adac-532839e56f0f.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=lw0O6UwHI76Lgei2MS5Tt6oOQ2Y%3D "")

::: danger 重点提醒
修改编码后，需点击**应用**才会生效。
:::

### 删除业务员围栏

1. 找到需要删除的业务员围栏。
2. 点击删除相关操作。
3. 点击**应用**，使删除生效。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/3fefe935-0b1b-4a27-9919-13779dee6bd5.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=CENgi0II56TOGbaCnhuyKMv8y5U%3D "")

::: danger 重点提醒
删除业务员围栏后，需点击**应用**才会生效。
:::

### 画错了或不想改了

如果画错了，或临时不想修改，可在未点击**应用**前点击**重置**。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/mxPOGyjaKvYQnKa9/img/7baa2bab-a547-4580-a0a6-eabf6161a094.png?Expires=1783781630&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=nAeSCCcrDivzIpUhP601qW2CF84%3D "")

::: warning 注意事项
前提是**没有点击应用**。

点击**重置**后，会回到上次点击**应用**时的数据。
:::

## 操作结果

设置完成并点击**应用**后：

- 派件地址落在对应业务员围栏内的订单，会匹配到对应的业务员编码。
- 例如：派件地址在编码 **01** 的区域内，则该订单的业务员编码为 **01**。
- 可在三段码最后 **1 位**、**快件跟踪**或**运单详情**中查看业务员编码。

## 注意事项

::: danger 重点提醒
- 请在对应的**网点围栏内**绘制业务员围栏。
- 建议绘制区域稍微大于网点围栏。系统会自动裁剪掉超过区域的部分，无需担心画超出，重点是保证网点范围内都覆盖。
- 如果绘制的围栏重叠，系统会删除先绘制的重叠部分，**后画的优先级更高！！**
- 编辑后不会立即生效，需点击**应用**才会生效。请在合理时间设置。
- 业务员编码**不允许重复**。
:::

::: warning 注意事项
- 当前业务员编码不强制配置，不勾画业务员围栏当前不影响。
- 后续将关联司机任务，并增加揽件业务员围栏。
- 如果网点围栏有新增，请及时修改业务员围栏。
- 如果网点围栏有删除，可不用修改，因为运单匹配不到。
:::

## 常见问题

### 一二级网点之间的业务员围栏是什么关系？

相互独立，没有关系，也没有关联。网点的业务围栏只和自己的网点围栏有关。

### 哪些情况不会打印业务员编码？

以下情况不会打印业务员编码：

- 指定网点录单的。
- 业务员围栏没有覆盖对应派件地址的。

### 业务员编码会不会存在错误的情况？

存在。

由于地址解析错误或地址不准确，可能导致解析错误，概率不大（**99.96%**）。建议在业务员编码的基础上，核对地址进行二次确认。

对于多次错误的地址，可上报工单进行校正处理。

### 不勾画业务员围栏，有没有影响？

当前不影响，非强制配置。

后续将关联司机任务，并增加揽件业务员围栏。

### 网点围栏有变化，需要及时修改业务员围栏吗？

- 如果网点围栏有新增，请及时修改业务员围栏。
- 如果网点围栏有删除，可不用修改，因为运单匹配不到。