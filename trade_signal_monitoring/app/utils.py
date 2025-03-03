import numpy as np


def convert_numpy_types(obj):
    """
    NumPy 타입을 Python 기본 타입으로 변환하는 재귀 함수

    Args:
        obj: 변환할 객체 (딕셔너리, 리스트, NumPy 값 등)

    Returns:
        변환된 객체
    """

    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj
