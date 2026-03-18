import json
import logging
import re
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_json_with_repair(
    json_str: str,
    max_repair_attempts: int = 5
) -> Tuple[Optional[dict], Optional[str]]:
    """
    尝试解析JSON，如果失败则自动修复
    
    Args:
        json_str: JSON字符串
        max_repair_attempts: 最大修复尝试次数
        
    Returns:
        (parsed_dict, error_message)
        - 成功: (dict, None)
        - 失败: (None, error_message)
    """
    if not json_str or not json_str.strip():
        return None, "JSON字符串为空"
    
    json_str = json_str.strip()
    
    # 第一次尝试直接解析
    try:
        data = json.loads(json_str)
        return data, None
    except json.JSONDecodeError as e:
        logger.warning(f"JSON解析失败（将尝试修复）: {e}")
    
    # 提取JSON内容（去除markdown代码块等）
    extracted = _extract_json(json_str)
    
    # 尝试修复
    current_json = extracted
    last_error = None
    
    for attempt in range(max_repair_attempts):
        try:
            data = json.loads(current_json)
            logger.info(f"JSON修复成功（尝试 {attempt + 1} 次）")
            return data, None
        except json.JSONDecodeError as e:
            last_error = e
            logger.debug(f"第 {attempt + 1} 次修复尝试: {e}")
            current_json = _repair_json_string(current_json, e)
    
    error_msg = f"JSON解析失败（已尝试 {max_repair_attempts} 次修复）: {last_error}"
    logger.error(error_msg)
    return None, error_msg


def _extract_json(text: str) -> str:
    """从文本中提取JSON内容"""
    text = text.strip()
    
    # 尝试提取markdown代码块中的JSON
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    # 尝试提取普通代码块中的JSON
    code_match = re.search(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    
    # 尝试提取花括号包裹的内容
    brace_match = re.search(r'\{[\s\S]*\}', text)
    if brace_match:
        return brace_match.group(0).strip()
    
    return text


def _repair_json_string(json_str: str, error: json.JSONDecodeError) -> str:
    """尝试修复JSON字符串"""
    lines = json_str.split('\n')
    
    if error.lineno <= 0 or error.lineno > len(lines):
        return json_str
    
    error_line_idx = error.lineno - 1
    error_line = lines[error_line_idx]
    error_col = max(0, error.colno - 1) if error.colno > 0 else 0
    
    if error_col > len(error_line):
        return json_str
    
    error_char = error_line[error_col] if error_col < len(error_line) else ''
    
    # 修复策略1：缺少逗号
    if "Expecting ',' delimiter" in error.msg or "Expecting ','" in error.msg:
        fixed_line = _fix_missing_comma(error_line, error_col)
        if fixed_line != error_line:
            lines[error_line_idx] = fixed_line
            logger.info(f"修复：在行 {error.lineno} 列 {error.colno} 添加了逗号")
            return '\n'.join(lines)
    
    # 修复策略2：未转义的引号
    if error_char == '"' or "Unterminated string" in error.msg:
        fixed_line = _fix_unescaped_quote(error_line, error_col)
        if fixed_line != error_line:
            lines[error_line_idx] = fixed_line
            logger.info(f"修复：在行 {error.lineno} 列 {error.colno} 处理了引号问题")
            return '\n'.join(lines)
    
    # 修复策略3：未结束的字符串
    if "Unterminated string" in error.msg or "Expecting property name" in error.msg:
        fixed_line = _fix_unterminated_string(error_line, error_col)
        if fixed_line != error_line:
            lines[error_line_idx] = fixed_line
            logger.info(f"修复：在行 {error.lineno} 处理了未结束的字符串")
            return '\n'.join(lines)
    
    return '\n'.join(lines)


def _fix_missing_comma(line: str, col: int) -> str:
    """修复缺少逗号的问题"""
    if col <= 0 or col >= len(line):
        return line
    
    # 检查是否在字符串值内
    quote_count = line[:col].count('"') - line[:col].count('\\"')
    
    # 偶数个引号说明在字符串外
    if quote_count % 2 == 0:
        # 在当前位置添加逗号
        return line[:col] + ',' + line[col:]
    else:
        # 在字符串内，可能是引号问题，尝试转义
        if line[col] == '"' and (col == 0 or line[col - 1] != '\\'):
            return line[:col] + '\\' + line[col:]
    
    return line


def _fix_unescaped_quote(line: str, col: int) -> str:
    """修复未转义的引号"""
    if col >= len(line):
        return line
    
    # 检查引号是否需要转义
    if line[col] == '"':
        if col == 0 or line[col - 1] != '\\':
            return line[:col] + '\\' + line[col:]
    
    return line


def _fix_unterminated_string(line: str, col: int) -> str:
    """修复未结束的字符串"""
    # 计算引号数量
    quote_count = line.count('"') - line.count('\\"')
    
    # 奇数个引号说明字符串未结束
    if quote_count % 2 == 1:
        # 在行尾添加引号
        return line + '"'
    
    return line


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全的JSON解析，失败时返回默认值
    
    Args:
        json_str: JSON字符串
        default: 失败时返回的默认值
        
    Returns:
        解析后的数据或默认值
    """
    data, error = parse_json_with_repair(json_str)
    if error:
        logger.warning(f"JSON解析失败，返回默认值: {error}")
        return default
    return data
