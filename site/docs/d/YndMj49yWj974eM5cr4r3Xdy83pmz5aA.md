---
title: "差错如何申报-申诉？"
description: "差错如何申报-申诉？的操作说明。"
---

# 差错如何申报申诉？

## 一、适用场景

本文适用于网点或相关流程节点人员，在系统中进行**差错申报**、**差错申诉**、查询差错处理数据时参考。

## 二、前置条件

1. 已具备进入**服务质量**相关菜单的账号和权限。
2. 网点需具备**品控工作台 操作**权限，才可进行以下操作：
   - **新增**：发布差错。
   - **申诉**：责任方发起申诉。
3. 需要准备对应的**运单号/调度单号**及差错相关信息。

## 三、操作入口

**操作入口**：**服务质量**

- 流程节点人员：在**【操作】**中处理、查看数据。
- 非流程节点人员：在**【查询】**中查看数据。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZw5AzyJdlLX8/img/3657c25c-bd9a-46a7-97b5-2b4f2ec5ca7a.png?Expires=1783781587&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=UrifiKSv83tTtCbAXezLn2hDkes%3D "")

## 四、操作步骤

### 4.1 处理流程

1. 申报方发起申报后，**72H** 内如果被申报方未发起申诉，数据会自动流转至总部。
2. 总部处理时可选择**不受理**：
   - 若总部**不受理**，不产生相应罚款，申报方可针对该运单再次发起申报。
   - 若再次发起的申报数据被总部**受理**，则当前运单不可再次发起申诉。
3. 总部**受理**后，会产生相应罚款。
4. **已签收运单不可发起申报**。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/eYVOLwoo5AeGqpz2/img/2ee3b434-d927-4b92-a193-c7faf14b1e7f.png?Expires=1783781587&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=R3szncaDV89pjiQOUpoAOm6a9ik%3D "")

### 4.2 查询、申报、申诉处理

1. 进入差错处理页面后，可在此页面进行**差错发布**、**申诉**操作。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/eYVOLwoo5AeGqpz2/img/52692f78-3a85-4f7c-a269-38a690d72f47.png?Expires=1783781587&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=Dtcgl9hBmRLc0vSgeYojwLzxyoA%3D "")

2. 点击进入**差错发布**，按页面要求填写信息：

   - **差错编号**：系统自动生成。规则为**年月日时分秒各2位 + c + 随机数5位**。
   - **运单号/调度单号**：非总部填写时必填。
   - **异常数**：非必填。若**运单号/调度单号**填写的是运单号，系统会校验异常数不可大于运单号件数。
   - **差错类型**：必选。
   - **差错类别**：必选。
   - **问题描述**：非必填。
   - **附件**：非必填。

::: danger 重点提醒
1. **运单号已签收不可申报**。
2. 同一个运单若存在总部**不受理**的申报数据，则可再次申报；否则不可再次申报。
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/eYVOLwoo5AeGqpz2/img/42a80223-eb9f-490d-a69d-224c2b0c0e24.png?Expires=1783781587&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=fKXlJVzmdgotT0WhR7FbNcSYAaI%3D "")

3. 责任方发起**差错申诉**。

::: danger 重点提醒
只有当**申诉**按钮处于**待处理**时，才可以发起申诉。

系统会校验当前申报单状态：当前状态 **!= 已申报** 时，会提示：

“**申诉失败！当前差错已在,不可申诉，有疑问请联系总部运营-曲丽娜**”
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/eYVOLwoo5AeGqpz2/img/eaa32f8f-7b3d-45be-98b0-af554a142c37.png?Expires=1783781587&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ongIvd%2FdhfXZq1KTqYGq7NdQ44w%3D "")

## 五、操作结果

1. 差错发布成功后，系统生成对应的**差错编号**。
2. 被申报方在**72H** 内未申诉的，数据会自动流转至总部。
3. 总部处理结果可能为**不受理**或**受理**：
   - **不受理**：不产生相应罚款，符合条件时可再次申报。
   - **受理**：产生相应罚款。

## 六、注意事项

::: warning 注意事项
1. 流程节点人员请在**【操作】**中处理和查看数据；非流程节点人员请在**【查询】**中查看数据。
2. **已签收运单不可发起申报**。
3. **异常数**填写时，若填写的是运单号，异常数不可大于该运单号件数。
4. 同一个运单是否可再次申报，以总部是否存在**不受理**申报数据为准。
5. 发起申诉时，需关注申报单状态及**申诉**按钮是否处于**待处理**。
:::

## 七、常见问题

### 7.1 为什么无法发起申诉？

可能是当前申报单状态不满足申诉条件。系统校验当前状态 **!= 已申报** 时，会提示：

“**申诉失败！当前差错已在,不可申诉，有疑问请联系总部运营-曲丽娜**”

### 7.2 已签收运单还能申报差错吗？

不能。**已签收运单不可发起申报**。