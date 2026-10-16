# Podmate 受管套餐策略

这个公开仓库托管 Podmate 的非敏感套餐参数、隐私与支持说明和第三方库许可材料。策略发布地址是
`https://ayqy.github.io/podmate-plan/managed-policy.json`。

`plan-config.json` 是运营输入，`scripts/refresh_policy.py` 按 UTC 时间产生最长七天有效的
`docs/managed-policy.json`。GitHub Actions 每天更新并发布；价格仅为目录参考，实际
购买价格和订阅权益以 Apple StoreKit 的已核验结果为准。当前未配置 Apple 商品，
因此不会出现可购买订阅，也不授予订阅额度。

额度以 USD 的十亿分之一为单位，是用户自带阿里云百炼密钥的本机参考请求上限，
不是 Podmate 储值、服务商余额、实际成本或跨设备结算。

隐私说明：https://ayqy.github.io/podmate-plan/privacy.html

产品支持与第三方许可：https://ayqy.github.io/podmate-plan/support.html

English privacy and support: https://ayqy.github.io/podmate-plan/privacy-en.html and
https://ayqy.github.io/podmate-plan/support-en.html .

构建 1.0.0（5）的 LAME 对应源码与重链接材料：
https://ayqy.github.io/podmate-plan/relinking.html ，英文说明见
https://ayqy.github.io/podmate-plan/relinking-en.html 。材料公开不表示应用已在 App Store 上架。

`docs/privacy-policy.json` 与应用打包政策同源；修改后用 `python3 scripts/build_product_pages.py` 生成页面，再以 `--check` 校验。只发布非敏感说明及已集成 LGPL 库的源码，不包含私有应用仓库、用户数据或凭据。既有每日策略刷新与策略数据合同保持。
