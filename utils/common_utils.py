#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""通用工具函数模块"""

import os
import sys
import logging
import time
import hashlib
import json
import re
from datetime import datetime, timedelta
from config.config import LOG_DIR, DATA_DIR

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('common_utils')


def ensure_dir_exists(dir_path):
    """确保目录存在，如果不存在则创建"""
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"目录已创建: {dir_path}")
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {dir_path}, 错误: {e}")
        return False


def is_valid_email(email):
    """验证邮箱格式是否正确"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """验证手机号格式是否正确"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def generate_hash(text, salt=None):
    """生成文本的哈希值"""
    if salt is None:
        salt = os.urandom(32)
    else:
        salt = salt.encode('utf-8')
    
    hasher = hashlib.sha256()
    hasher.update(salt)
    hasher.update(text.encode('utf-8'))
    hash_value = hasher.hexdigest()
    
    return hash_value, salt.hex()


def verify_hash(text, hash_value, salt_hex):
    """验证文本的哈希值是否正确"""
    try:
        salt = bytes.fromhex(salt_hex)
        new_hash_value, _ = generate_hash(text, salt_hex)
        return new_hash_value == hash_value
    except Exception as e:
        logger.error(f"验证哈希值失败: {e}")
        return False


def write_json_file(file_path, data):
    """将数据写入JSON文件"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:
            ensure_dir_exists(dir_path)
        
        # 写入数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"数据已写入文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败: {file_path}, 错误: {e}")
        return False


def read_json_file(file_path):
    """从JSON文件读取数据"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"已从文件读取数据: {file_path}")
        return data
    except Exception as e:
        logger.error(f"读取JSON文件失败: {file_path}, 错误: {e}")
        return None


def get_current_time(format_str="%Y-%m-%d %H:%M:%S"):
    """获取当前时间，格式化为指定字符串"""
    return datetime.now().strftime(format_str)


def get_current_date(format_str="%Y-%m-%d"):
    """获取当前日期，格式化为指定字符串"""
    return datetime.now().strftime(format_str)


def format_time(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """将时间戳格式化为指定字符串"""
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime(format_str)
        return timestamp
    except Exception as e:
        logger.error(f"格式化时间失败: {e}")
        return timestamp


def get_time_difference(start_time, end_time=None):
    """计算时间差"""
    try:
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        
        if end_time is None:
            end_time = datetime.now()
        elif isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        
        return end_time - start_time
    except Exception as e:
        logger.error(f"计算时间差失败: {e}")
        return None


def get_logger(name, log_file=None, level=logging.INFO):
    """创建自定义日志记录器"""
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 添加控制台处理器
        logger.addHandler(console_handler)
        
        # 如果指定了日志文件，创建文件处理器
        if log_file:
            # 确保日志目录存在
            ensure_dir_exists(LOG_DIR)
            
            # 创建文件路径
            log_path = os.path.join(LOG_DIR, log_file)
            
            # 创建文件处理器
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            
            # 添加文件处理器
            logger.addHandler(file_handler)
    
    return logger


def truncate_string(s, max_length):
    """截断字符串到指定长度"""
    if len(s) <= max_length:
        return s
    return s[:max_length] + '...'


def is_number(s):
    """检查字符串是否为数字"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def safe_cast(value, to_type, default=None):
    """安全地转换类型"""
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default


def calculate_gpa(score):
    """根据分数计算GPA"""
    if score >= 90:
        return 4.0
    elif score >= 85:
        return 3.7
    elif score >= 82:
        return 3.3
    elif score >= 78:
        return 3.0
    elif score >= 75:
        return 2.7
    elif score >= 72:
        return 2.3
    elif score >= 68:
        return 2.0
    elif score >= 64:
        return 1.5
    elif score >= 60:
        return 1.0
    else:
        return 0.0


def calculate_weighted_average(scores, weights=None):
    """计算加权平均分"""
    try:
        if not scores:
            return 0
        
        # 如果没有提供权重，使用等权重
        if weights is None:
            weights = [1] * len(scores)
        
        # 确保权重长度与分数长度一致
        if len(weights) != len(scores):
            logger.error("权重长度与分数长度不一致")
            return 0
        
        # 计算加权和和权重和
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        # 避免除以零
        if total_weight == 0:
            return 0
        
        return weighted_sum / total_weight
    except Exception as e:
        logger.error(f"计算加权平均分失败: {e}")
        return 0


def get_file_size(file_path, human_readable=True):
    """获取文件大小"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return 0
        
        size = os.path.getsize(file_path)
        
        if human_readable:
            # 转换为人类可读格式
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024 or unit == 'TB':
                    return f"{size:.2f} {unit}"
                size /= 1024
        
        return size
    except Exception as e:
        logger.error(f"获取文件大小失败: {file_path}, 错误: {e}")
        return 0


def clean_string(s):
    """清理字符串，去除多余的空格和换行符"""
    if s is None:
        return ''
    
    # 去除首尾空格和换行符
    s = s.strip()
    
    # 去除中间多余的空格和换行符
    s = re.sub(r'\s+', ' ', s)
    
    return s


def backup_file(file_path, backup_dir=None):
    """备份文件"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return False
        
        # 如果没有指定备份目录，使用默认数据目录
        if backup_dir is None:
            backup_dir = os.path.join(DATA_DIR, 'backups')
        
        # 确保备份目录存在
        ensure_dir_exists(backup_dir)
        
        # 创建备份文件名
        file_name = os.path.basename(file_path)
        timestamp = get_current_time("%Y%m%d_%H%M%S")
        backup_file_name = f"{file_name}.{timestamp}.bak"
        backup_file_path = os.path.join(backup_dir, backup_file_name)
        
        # 复制文件
        import shutil
        shutil.copy2(file_path, backup_file_path)
        
        logger.info(f"文件已备份到: {backup_file_path}")
        return True
    except Exception as e:
        logger.error(f"备份文件失败: {file_path}, 错误: {e}")
        return False


def restore_file(backup_file_path, target_file_path):
    """从备份文件恢复"""
    try:
        if not os.path.exists(backup_file_path):
            logger.warning(f"备份文件不存在: {backup_file_path}")
            return False
        
        # 确保目标目录存在
        target_dir = os.path.dirname(target_file_path)
        if target_dir:
            ensure_dir_exists(target_dir)
        
        # 复制文件
        import shutil
        shutil.copy2(backup_file_path, target_file_path)
        
        logger.info(f"文件已从备份恢复到: {target_file_path}")
        return True
    except Exception as e:
        logger.error(f"恢复文件失败: {e}")
        return False


def get_system_info():
    """获取系统信息"""
    import platform
    import psutil
    
    try:
        # 获取系统基本信息
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_build': platform.python_build(),
            'python_compiler': platform.python_compiler(),
            'hostname': platform.node(),
        }
        
        # 获取CPU信息
        system_info['cpu_count_physical'] = psutil.cpu_count(logical=False)
        system_info['cpu_count_logical'] = psutil.cpu_count(logical=True)
        system_info['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        
        # 获取内存信息
        memory_info = psutil.virtual_memory()
        system_info['memory_total'] = get_file_size(memory_info.total, human_readable=True)
        system_info['memory_used'] = get_file_size(memory_info.used, human_readable=True)
        system_info['memory_percent'] = memory_info.percent
        
        # 获取磁盘信息
        disk_info = psutil.disk_usage('/')
        system_info['disk_total'] = get_file_size(disk_info.total, human_readable=True)
        system_info['disk_used'] = get_file_size(disk_info.used, human_readable=True)
        system_info['disk_percent'] = disk_info.percent
        
        logger.info("成功获取系统信息")
        return system_info
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return {'error': str(e)}


def get_network_info():
    """获取网络信息"""
    import socket
    
    try:
        # 获取主机名
        hostname = socket.gethostname()
        
        # 获取IP地址
        ip_address = socket.gethostbyname(hostname)
        
        # 尝试获取公网IP（可能不准确）
        try:
            public_ip = socket.gethostbyname(hostname)
        except Exception:
            public_ip = '无法获取'
        
        network_info = {
            'hostname': hostname,
            'ip_address': ip_address,
            'public_ip': public_ip
        }
        
        logger.info("成功获取网络信息")
        return network_info
    except Exception as e:
        logger.error(f"获取网络信息失败: {e}")
        return {'error': str(e)}


def retry_on_exception(func, max_retries=3, delay=1):
    """装饰器：在异常发生时重试函数"""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后失败: {e}")
                    raise
                logger.warning(f"函数 {func.__name__} 执行失败，{delay} 秒后重试 ({retries}/{max_retries}): {e}")
                time.sleep(delay)
    return wrapper


def measure_execution_time(func):
    """装饰器：测量函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.6f} 秒")
        return result
    return wrapper


def get_random_string(length=8):
    """生成随机字符串"""
    import random
    import string
    
    try:
        # 生成随机字符串
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return random_string
    except Exception as e:
        logger.error(f"生成随机字符串失败: {e}")
        return ''


def export_to_csv(data, file_path, headers=None):
    """将数据导出为CSV文件"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:
            ensure_dir_exists(dir_path)
        
        # 写入CSV文件
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            if headers:
                writer.writerow(headers)
            
            # 写入数据
            for row in data:
                writer.writerow(row)
        
        logger.info(f"数据已导出到CSV文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"导出CSV文件失败: {file_path}, 错误: {e}")
        return False


def import_from_csv(file_path):
    """从CSV文件导入数据"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"CSV文件不存在: {file_path}")
            return None
        
        # 读取CSV文件
        import csv
        data = []
        headers = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 读取表头
            try:
                headers = next(reader)
            except StopIteration:
                # 文件为空
                logger.warning(f"CSV文件为空: {file_path}")
                return {'headers': [], 'data': []}
            
            # 读取数据
            for row in reader:
                data.append(row)
        
        logger.info(f"已从CSV文件导入数据: {file_path}")
        return {'headers': headers, 'data': data}
    except Exception as e:
        logger.error(f"导入CSV文件失败: {file_path}, 错误: {e}")
        return None


def get_file_extension(file_path):
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1].lower()


def get_file_name_without_extension(file_path):
    """获取不带扩展名的文件名"""
    return os.path.splitext(os.path.basename(file_path))[0]


# 测试代码
if __name__ == '__main__':
    # 测试工具函数
    print("测试确保目录存在:")
    test_dir = os.path.join(DATA_DIR, 'test')
    ensure_dir_exists(test_dir)
    
    print("测试邮箱验证:")
    print(f"test@example.com: {is_valid_email('test@example.com')}")
    print(f"invalid-email: {is_valid_email('invalid-email')}")
    
    print("测试手机号验证:")
    print(f"13812345678: {is_valid_phone('13812345678')}")
    print(f"12345678901: {is_valid_phone('12345678901')}")
    
    print("测试哈希生成和验证:")
    hash_value, salt = generate_hash('test_password')
    print(f"哈希值: {hash_value}")
    print(f"盐值: {salt}")
    print(f"验证结果: {verify_hash('test_password', hash_value, salt)}")
    print(f"错误密码验证结果: {verify_hash('wrong_password', hash_value, salt)}")
    
    print("测试JSON文件读写:")
    test_data = {'name': 'test', 'value': 123}
    test_file = os.path.join(DATA_DIR, 'test.json')
    write_json_file(test_file, test_data)
    read_data = read_json_file(test_file)
    print(f"读取的数据: {read_data}")
    
    print("测试当前时间和日期:")
    print(f"当前时间: {get_current_time()}")
    print(f"当前日期: {get_current_date()}")
    
    print("测试获取系统信息:")
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    print("测试获取网络信息:")
    network_info = get_network_info()
    for key, value in network_info.items():
        print(f"{key}: {value}")
    
    print("测试重试装饰器:")
    @retry_on_exception
    def test_retry():
        raise Exception("测试异常")
    
    try:
        test_retry()
    except Exception as e:
        print(f"重试后仍然失败: {e}")
    
    print("测试执行时间测量装饰器:")
    @measure_execution_time
    def test_execution_time():
        time.sleep(0.5)
    
    test_execution_time()
    
    print("测试生成随机字符串:")
    print(f"随机字符串: {get_random_string(16)}")
    
    print("测试CSV文件导出和导入:")
    csv_data = [[1, 'test1', 100], [2, 'test2', 200], [3, 'test3', 300]]
    csv_headers = ['id', 'name', 'value']
    csv_file = os.path.join(DATA_DIR, 'test.csv')
    export_to_csv(csv_data, csv_file, csv_headers)
    imported_data = import_from_csv(csv_file)
    print(f"CSV表头: {imported_data['headers']}")
    print(f"CSV数据: {imported_data['data']}")
    
    print("工具函数测试完成")