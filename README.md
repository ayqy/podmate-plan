# Podmate 受管套餐策略

这个公开仓库只托管 Podmate 的非敏感套餐参数。发布地址是
`https://ayqy.github.io/podmate-plan/managed-policy.json`。

`plan-config.json` 是运营输入，`scripts/refresh_policy.py` 按 UTC 时间产生最长七天有效的
`docs/managed-policy.json`。GitHub Actions 每天更新并发布；价格仅为目录参考，实际
购买价格和订阅权益以 Apple StoreKit 的已核验结果为准。当前未配置 Apple 商品，
因此不会出现可购买订阅，也不授予订阅额度。

额度以 USD 的十亿分之一为单位，是用户自带 OpenAI 密钥的本机参考请求上限，
不是 Podmate 储值、服务商余额、实际成本或跨设备结算。
