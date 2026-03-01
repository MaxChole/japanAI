# 脚本说明

## test_advise.sh

在后端已启动的前提下，请求一次「日本价格/投资建议」并格式化输出。

```bash
# 默认请求 http://localhost:8000
./scripts/test_advise.sh

# 指定后端地址
./scripts/test_advise.sh http://127.0.0.1:8000
```

依赖：本机已安装 `curl`、`python3`。
