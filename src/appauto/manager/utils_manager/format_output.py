from typing import List


def format_time(seconds):
    """
    将给定的秒数转换为人类可读的时间格式, 注意: 超过 10 分钟才转换为分钟。
    """
    time_units = [
        ("年", 31536000),
        ("月", 2628000),
        ("周", 604800),
        ("天", 86400),
        ("小时", 3600),
        ("分钟", 60),
        ("秒", 1),
    ]

    for unit, unit_seconds in time_units:
        if seconds >= unit_seconds:
            value = seconds / unit_seconds
            if value >= 1:
                if unit == "分钟" and value < 10:
                    return f"{seconds:.0f} 秒"
                return f"{value:.1f} {unit}"
            else:
                remainder = seconds % unit_seconds
                if unit == "分钟" and value < 10:
                    return f"{seconds:.0f} 秒 {format_time(remainder)}"
                return f"{value:.1f} {unit} {format_time(remainder)}"

    return f"{seconds:.0f} 秒"


def str_to_list_by_split(content, singleLine=True) -> List:
    """
    单行: 分隔符是逗号
    多行: 分隔符是换行符
    """
    if singleLine:
        return list(filter(None, content.replace("\n", "").split(",")))
    else:
        return list(filter(None, content.split("\n")))
