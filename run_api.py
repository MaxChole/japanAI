#!/usr/bin/env python3
"""
启动地产建议 API 服务：uvicorn japanai.api.app:app --reload
可直接执行: python run_api.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "japanai.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
