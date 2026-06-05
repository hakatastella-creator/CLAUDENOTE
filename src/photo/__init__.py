"""保定オリエンテーション資料用 規格写真処理モジュール。

撮影した規格写真（8枚法）を AI で自動分類し、ミラー撮影の向きを補正して、
規格コラージュ・初診時/現在の Before/After 比較・保定オリエンテーション資料
（PPTX / PDF）を自動生成する。
"""

from .pipeline import run, process_timepoint, PipelineOutputs, TimepointResult

__all__ = ["run", "process_timepoint", "PipelineOutputs", "TimepointResult"]
