---
title: "单据-入库单"
description: "单据-入库单的操作说明。"
---

# 单据入库单

## 一、适用场景

本文适用于在 **OMS订单中心** 处理 **入库单** 的场景，包括：

- **ERP客户**：ERP完成对接后，在ERP创建入库单并同步到OMS。
- **非ERP客户**：在OMS中手动 **新增** 或 **导入** 入库单。

## 二、前置条件

- 已具备鲸天系统登录账号及对应菜单权限。
- 已确认入库相关基础资料可用，例如 **货主**、**仓库**、**商品** 等。
- ERP客户需已完成ERP与OMS对接。
- 非ERP客户需准备好入库单必填信息或导入文件。

**官方系统登录入口**：👉 [[入库单-鲸天系统](https://wms.ztocc.com/app/#/back/warehousing)]

## 三、操作入口

- **系统功能路径**：`登录系统` -> `进入左侧菜单栏` -> `[OMS订单中心]` -> `[入库管理]` -> `[入库单]`
- **快捷直达链接**：👉 [[入库单-鲸天系统](https://wms.ztocc.com/app/#/back/warehousing)]

## 四、操作步骤

### 4.1 单据业务流程图

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmb2GkDd6Om9/img/2771955b-2011-4def-9f78-7cb03188ae07.png?Expires=1783781780&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=FzAXZnRKw4gOgtC1t19IqEoKNeA%3D "")

### 4.2 场景一：ERP客户处理入库单

1. 在ERP中创建入库单，并同步入库单到OMS。

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmb2GkDd6Om9/img/1685a119-0241-4f1f-9c0d-a026b70e0bce.png?Expires=1783781780&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=WKYaZJpKFQSvpz0Y6jIh8%2F%2FsYXw%3D "")

2. OMS接收入库单后，系统会自动同步到WMS中。

3. WMS完成入库上架后，系统会自动回传入库信息到OMS中，再由OMS回传入库信息到ERP。

### 4.3 场景二：非ERP客户处理入库单

1. 进入 **入库单** 页面，点击 **新增** 或 **导入**。

2. 按要求填写入库单信息。

   - **头表信息**：**货主**、**仓库**、**单据类型**、**外部单号**、**物流公司**、**物流单号**、**备注**、**联系人**、**联系电话**、**寄件省**、**寄件是**、**寄件区**、**详细地址**
   - **明细信息**：**商品**、**商家系统编码**、**商家商品编码**、**总数量**、**二级单位**、**最小单位**

3. 新增或导入文件中的必填信息填写完成后，点击保存，返回入库单列表。

   ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmb2GkDd6Om9/img/245bfb37-3f27-4eb7-9644-c569daaf4251.png?Expires=1783781780&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=zQioHC0FFCm9DMGlTAxSYnsLZnU%3D "")

4. 在入库单列表中，根据需要进行以下操作：

   - 点击 **审核**：OMS审核入库单后，系统会自动同步到WMS中。

     ![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Lk3lbmb2GkDd6Om9/img/030d1a7a-b2ed-49af-8ecf-db8469bf4a9c.png?Expires=1783781780&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=3tTz1JcS0mYEX9JnFLXS5Qle2io%3D "")

   - 点击 **编辑**：新增完成后如需调整信息，可重新编辑入库单信息。
   - 点击 **复制**：如需创建相同类型的订单，可复制已新增或已导入的入库单。
   - 点击 **取消**：如创建的入库单有问题，可取消入库单。
   - 点击 **删除**：支持物理删除入库单。

5. WMS完成入库上架后，系统会自动回传入库信息到OMS中，再由OMS回传入库信息到ERP。

## 五、操作结果

- ERP客户：ERP创建的入库单同步到OMS，OMS自动同步到WMS；WMS入库上架完成后，入库信息自动回传至OMS和ERP。
- 非ERP客户：在OMS中完成入库单 **新增** 或 **导入**，并通过 **审核** 后自动同步到WMS；WMS入库上架完成后，入库信息自动回传至OMS。

## 六、注意事项

::: danger 重点提醒
- 导入入库单时，当前导入的 **货主单据号** 不能重复。
- 导入商品明细中的商品需属于当前导入的货主。
:::

::: warning 注意事项
- 如导入时提示商品二级单位未维护，需要先在WMS中维护商品单位。维护后，商品单位会自动同步到OMS中，再重新导入入库单。
- 点击 **删除** 会物理删除入库单，请谨慎操作。
:::

## 七、常见异常与兜底方案

| 序号 | ❌ 异常现象 / 报错提示 | 🔍 常见原因 | 🛠️ 解决方案 |
|------|-------------------------------|-----------------|--------------------|

## 八、常见问题

- **Q1：导入时提示商品二级单位未维护，怎么办？**
  **A**：需要在WMS中维护商品单位，维护后商品单位会自动同步到OMS中，可重新导入入库单。

- **Q2：导入时提示单据【xxx】已存在，怎么办？**
  **A**：当前导入的货主单据号已存在，不能够重复导入，需要更新单据号之后重新导入。

- **Q3：导入时提示商品【xxx】不属于货主【xxx】，怎么办？**
  **A**：导入的商品明细中的商品不是导入货主的商品，需要检查导入数据信息，更新后重新导入。