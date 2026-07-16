---
title: "维护对客报价"
description: "维护对客报价的操作说明。"
---

# 维护对客报价

## 一、适用场景

本文适用于网点维护客户报价时使用，包括以下场景：

- **大客户 / 协议客户**：网点可使用**对客报价**维护与客户约定好的价格。客户下单时可直接看到成本，下单后生成对应账单，减少沟通成本。
- **散客**：网点可提前按市场价维护一份揽货价格，客户下单后减少运费争议。

### 1.1 名词解释

- **对客报价**：网点面向外部客户制定的运输、派件、保价等服务收费标准，包含单价、计价规则、适用范围等，是生成对客账单的核心依据。
- **报价校验**：系统自动检测报价内容、配置是否合规，并拦截异常数据。
- **报价模式**：报价计费的方式，可以自定义价格，也可以在现有成本的基础上做加收。
- **报价对象**：可以对不同客户区分定价。
- **计费参数**：通常客户使用重量计费，部分特殊客户可按件数、票数计费，需选择对应的计费基础。

## 二、前置条件

- **账号与权限要求**：权限角色需包含 **`[ZTO网点管理员]`**。若无权限，请联系系统管理员。
- **物理 / 环境准备**：无特殊要求。
- **系统登录入口**：[点击进入系统](https://jt.ztocc.com/dashboard)

## 三、操作入口

- **系统功能路径**：**登录系统** -> **进入左侧菜单栏** -> **[财务管理]** -> **[一级网点内部报价]** -> **[对客报价]**
- **快捷直达链接**：[点击一键直达该页面](https://jt.ztocc.com/app/#/phecda/quote/quote-maintenance)

## 四、操作步骤

### 4.1 报价维护

1. 进入**对客报价**页面后，点击右上角 **【新增】**，打开新增表单。

2. 填写**报价名称**，依次选择**报价模式**、**产品类型**、**生效区间**，然后点击 **【下一步】**。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/7644660d-2006-4231-89ad-c4eb8151289a.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=fACwuQtXofbR%2BdbxF7Qqs1GcUqQ%3D "")

3. 进入客户基本信息页面后，填写**对象组名称**，依次选择**报价对象**、**计费参数**、**计费参数进位方式**。

4. 点击右上角操作列的 **【保存】**。

::: warning 注意事项
仅支持对**大客户、协议客户**单独定价，报价对象只显示**大客户、协议客户**。

维护散客报价时，报价对象选择 **“全部”**，用于维护兜底价格。
:::

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/6c99a7a8-5f7e-4ab1-8547-64c96e5fed42.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=8Kg1q37WUx7Q%2BpdFXCExV2w%2FfPI%3D "")

5. 点击右上角 **【设置费用项】**。

6. 在弹框中勾选需要配置的**结算费用项**。如果对成本为 **0** 的费用项也需要加收，可勾选**加收开关**后保存。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/bd8edae3-3455-44cb-8ff2-6a5b8c8d4871.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=MjOy9s6y5ZN8CR1sHXvLKGeT%2FNo%3D "")

7. 在报价详情列表中，点击**目的地**下方的空白区域，打开目的地维护弹框。

8. 在弹框中勾选**省市**，填写合适的**区域名称**后保存。

9. 如需维护多个目的地报价，点击报价详情模块操作列的 **【新增】**，按上述方法继续增加目的地。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/2d30098b-4f73-4f41-bcb4-4c35807bc492.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=im8qhR%2F6BnKQpkt%2BECADDaB7jz0%3D "")

10. 在**重量段**区域填写**结束重量**。

11. 如需维护多个重量段，填写结束重量后，依次点击重量段后的 **【保存】**、**【新增】**，按上述方法继续增加重量段。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/b88bef87-28a0-4e68-9213-6958249d504e.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=ZX49FKGYpx0On%2F5ICCOZrsJVcHQ%3D "")

12. 点击费用项下方的 **【填充计费公式】**。

13. 选择合适的模板，填写**价格标准**。

14. 如需设置**最低收费**、**最高收费**，勾选对应开关后填写最低、最高收费标准。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/309be816-eaeb-4672-b046-033734ece48a.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=gh%2FFVNvVFue%2Frm14c%2FNVs24UvKg%3D "")

15. 所有费用项价格维护完成后，点击右下角 **【保存】**。

16. 如果存在未勾选的费用项，系统会弹出提醒。确认无需添加费用项后，点击 **【确定】**，完成价格维护。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/f66db14f-83c2-4575-82f7-1b579e1b141e.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=aYq3Fp5RA5Qh0RGVm%2FfdyIOh714%3D "")

17. 返回报价列表，勾选报价，点击右上角 **【审核】**。

18. 审核通过后，价格生效。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/Pd6l2Z7P30z1Al7M/img/de14395a-defb-48b2-9cda-d343fa04a663.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=v1wPkUQYYj9jKLMCYwl%2FpH5U%2BVM%3D "")

## 五、操作结果

报价维护并审核通过后，系统会根据报价的**生效区间**判断是否可用：

- 生效日期**小于等于当天**：审核通过后立即生效，可应用于新订单。
- 生效日期在**次日及以后**：需等到对应生效日期后才可使用。
- 历史已结算账单价格不会随新报价变动。

## 六、注意事项

::: danger 重点提醒
- 同条件下已存在报价时，系统禁止重复创建。
- 报价对象包含 **“全部”** 时，为散客兜底价，需上级省区审核。
:::

::: warning 注意事项
维护价格前，请确认报价对象、计费参数、费用项、目的地、重量段、生效区间等信息填写正确。
:::

## 七、常见问题

### 7.1 Q1：保存报价提示报价重复，怎么办？

**常见原因**：同条件下已存在报价，系统禁止重复创建。

**解决方案**：编辑已有报价并更新内容，或作废旧报价后再重新新增。

### 7.2 Q2：新增的报价无法审核，怎么办？

**常见原因**：报价对象包含 **“全部”**，为散客兜底价，需上级省区审核。

**解决方案**：联系省区网管审核。

### 7.3 Q3：客户价格需要按目的地和重量段细分，明细段很多，有更高效的维护方式吗？

有。价格明细维护可使用 **【报价导入】** 功能。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/XNkOM5j9ykevKOY7/img/9d24ce05-4b7e-448c-9b80-f6ce15d8e59e.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4ZGeWvnYROYxmM6B%2Bvdc44hEW4M%3D "")

点击 **【报价导入】**，根据当前选择的**报价模式**，选择对应的导入模板。

![image.png](https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/XNkOM5j9ykevKOY7/img/9d24ce05-4b7e-448c-9b80-f6ce15d8e59e.png?Expires=1783781592&OSSAccessKeyId=LTAI5tKTjg4Kq1HCdBJ8qpSp&Signature=4ZGeWvnYROYxmM6B%2Bvdc44hEW4M%3D "")

根据实际情况填写对应的价格标准，可参照下图示例填写。

| <strong>区域名称</strong> | <strong>目的地</strong> | <strong>开始分段（>）</strong> | <strong>结束分段（\<=）</strong> | <strong>转运费</strong> | | | | | |
|---------------------------------------------------------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------------------|---|---|---|---|---|
| | | | | 首重 | 首价 | 续价 | 折扣 | 最低收费 | 最高收费 |
| 上海 | 上海市 | 0 | 300 | | | | 0.11 | | |
| 上海 | 上海市 | 300 | 600 | | | 1.2 | | | |
| 江苏 | 江苏省，浙江省（杭州市） | 0 | 1200 | 100 | 50 | 0.3 | | | |

### 7.4 Q4：新增报价后什么时候生效？

根据报价的**生效区间**判断：

- 生效日期**小于等于当天**：审核通过后立刻生效，可应用于新订单。
- 生效日期在**次日及以后**：需等次日才可使用。
- 历史已结算账单价格不会随之变动。