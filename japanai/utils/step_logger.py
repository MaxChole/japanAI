"""
步骤日志：供后端在控制台输出当前执行到哪一步，便于可观测与调试。
"""
import logging
import sys
from datetime import datetime

# 使用独立 logger，避免与第三方库混在一起；不向 root 传递，保证只输出一次
LOG = logging.getLogger("japanai.steps")
LOG.setLevel(logging.INFO)
LOG.propagate = False
if not LOG.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    LOG.addHandler(h)


def log_step(step_name: str, message: str = "开始执行", extra: str = "") -> None:
    """输出当前步骤，便于用户看到进度。"""
    line = f"[JapanAI] 步骤: {step_name} - {message}"
    if extra:
        line += f" | {extra}"
    LOG.info(line)


def log_step_done(step_name: str, elapsed_sec: float = 0) -> None:
    """输出步骤完成。"""
    if elapsed_sec > 0:
        LOG.info(f"[JapanAI] 步骤: {step_name} - 完成 (耗时 {elapsed_sec:.1f}s)")
    else:
        LOG.info(f"[JapanAI] 步骤: {step_name} - 完成")


def log_phase(phase: str, message: str = "") -> None:
    """输出阶段（如「分析师链」「多空辩论」）。"""
    LOG.info(f"[JapanAI] ========== {phase} ========== {message}")


def log_request_start(property_of_interest: str, user_profile_preview: str = "") -> None:
    """请求开始。"""
    LOG.info("[JapanAI] >>> 收到建议请求")
    LOG.info(f"[JapanAI] 标的: {property_of_interest[:80]}{'...' if len(property_of_interest) > 80 else ''}")
    if user_profile_preview:
        LOG.info(f"[JapanAI] 用户: {user_profile_preview[:80]}{'...' if len(user_profile_preview) > 80 else ''}")


def log_request_end(signal: str, elapsed_sec: float) -> None:
    """请求结束。"""
    LOG.info(f"[JapanAI] <<< 完成 | 信号: {signal} | 耗时: {elapsed_sec:.1f}s")
