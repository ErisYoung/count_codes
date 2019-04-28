import logging
import os
from pathlib import Path
from collections import namedtuple
from operator import attrgetter
import argparse

logging.basicConfig(filename="./log.txt", level=logging.DEBUG)
File = namedtuple("file", "name total blank code note size")


def parse_args():
    parser = argparse.ArgumentParser(usage="统计代码行数信息", description="统计行数信息")
    parser.add_argument("-s", "--sort", help="指定key排序", default="total")
    parser.add_argument("-r", "--reverse", help="是否逆序,默认是", action="store_false", default=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="输入文件名", default="")
    group.add_argument("-p", "--path", help="输入文件夹地址", default="")
    logging.debug("正在解析参数")
    args = parser.parse_args()
    logging.debug("解析完成,返回")
    return args


def get_file_path():
    args = parse_args()
    file, path = args.file, args.path
    if os.path.exists(path):
        logging.debug("获取路径")
        # 返回符合pattern的生成器
        pys = Path(path).glob("*.py")
        return list(pys)
    if Path(file).match("*.py"):
        logging.debug("文件存在，获取文件路径")
        return [file]

    raise OSError("输入路径错误")


def process_note_num(lines, symbol):
    note = 0
    for line in lines:
        note += 1
        if line.strip().startswith(symbol):
            break
    return note


def get_file_info():
    for path in get_file_path():
        path = str(path)
        name = os.path.split(str(path))[-1]
        total = blank = code = note = 0
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            temp_note = 0
            for i, line in enumerate(lines):
                logging.debug("读取文件行中")
                total += 1
                if temp_note > 1:
                    temp_note -= 1
                    continue
                line = line.strip()
                if not len(line):
                    blank += 1
                elif line.startswith("#"):
                    note += 1
                elif line.startswith("'''") or line.startswith('"""'):
                    temp_note = process_note_num(lines[i:], line[:3])
                    note += temp_note
                elif line.startswith("'") or line.startswith('"'):
                    temp_note = process_note_num(lines[i:], line[0])
                    note += temp_note
                else:
                    code += 1
        size = os.path.getsize(path)
        yield File(name, total, blank, code, note, size)


def sorted_file_info():
    args = parse_args()
    sort_key, is_reverse = args.sort, args.reverse
    # 按照指定的key来进行排序
    sorted_info = sorted(get_file_info(), key=attrgetter(sort_key), reverse=is_reverse)
    return sorted_info


def size_converse(size):
    KB = 1024
    MB = KB ** 2
    GB = KB ** 3
    unit = "B"
    if size < MB:
        size /= KB
        unit = "KB"
    elif MB <= size < GB:
        size /= MB
        unit = "MB"
    elif size >= GB:
        size /= GB
        unit = "GB"

    return size, unit


def show_file_info():
    total = blank = code = note = size = 0
    header = f'name{" "*8}total{" "*5}blank{" "*5}code{" "*6}note{" "*6}size'
    print(header)
    for i in sorted_file_info():
        converse_size = size_converse(i.size)
        size_format = "{:.2f}{}".format(*converse_size)
        print(f"{i.name:<12}{i.total:<10}{i.blank:<10}{i.code:<10}{i.note:<10}{size_format}")
        total += i.total
        blank += i.blank
        code += i.code
        note += i.note
        size += i.size
    converse_size = size_converse(size)
    size_format = "{:.2f}{}".format(*converse_size)
    print(f"total{' '*7}{total:<10}{blank:<10}{code:<10}{note:<10}{size_format}")


if __name__ == '__main__':
    show_file_info()
