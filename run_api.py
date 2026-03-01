#!/usr/bin/env python3
"""
启动地产建议 API 服务：uvicorn japanai.api.app:app --reload
可直接执行: python3 run_api.py
请求 /advise 时控制台会输出步骤日志（当前执行到哪一步、耗时等）。
"""
import logging
import sys

import uvicorn

# 确保 JapanAI 步骤日志输出到控制台，便于观察进度
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
    force=True,
)
logging.getLogger("japanai.steps").setLevel(logging.INFO)

if __name__ == "__main__":
    print("JapanAI 后端启动中，步骤日志将在此输出…", flush=True)
    uvicorn.run(
        "japanai.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
