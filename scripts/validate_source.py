#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
from typing import List, Tuple


def validate_markdown_file(md_file_path: str) -> Tuple[bool, str, int]:
    """
    验证 markdown 文件内容
    返回: (是否有效, 错误信息, XML链接数量)
    """
    
    # 检查文件是否存在
    if not os.path.exists(md_file_path):
        return False, f"文件不存在: {md_file_path}", 0
    
    # 检查文件是否为空
    if os.path.getsize(md_file_path) == 0:
        return False, "文件为空", 0
    
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"读取文件失败: {e}", 0
    
    # 检查文件内容是否为空
    if not content.strip():
        return False, "文件内容为空", 0
    
    # 查找所有 XML 链接
    xml_links = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # 查找 markdown 链接格式: [name](url.xml)
        matches = re.findall(r'\[([^\]]+)\]\(([^)]+\.xml)\)', line)
        for name, url in matches:
            # 验证是否是 wechat2rss 链接
            if 'wechat2rss.xlab.app/feed/' in url:
                xml_links.append((line_num, name, url))
            else:
                print(f"警告: 第 {line_num} 行发现非标准链接: {url}")
    
    # 验证链接数量
    if len(xml_links) == 0:
        return False, "没有发现有效的 XML 链接", 0
    
    # 设置最小链接数量阈值，防止清零
    MIN_LINKS = 10  # 可以根据实际情况调整
    if len(xml_links) < MIN_LINKS:
        return False, f"XML 链接数量过少 ({len(xml_links)} < {MIN_LINKS})，可能是数据清零", len(xml_links)
    
    # 验证链接格式
    invalid_links = []
    for line_num, name, url in xml_links:
        # 检查链接格式是否正确
        if not re.match(r'https://wechat2rss\.xlab\.app/feed/[a-f0-9]{40}\.xml', url):
            invalid_links.append(f"第 {line_num} 行: {name} -> {url}")
    
    if invalid_links:
        error_msg = "发现格式错误的链接:\n" + "\n".join(invalid_links)
        return False, error_msg, len(xml_links)
    
    # 检查是否有分类标题
    categories = re.findall(r'^## (.+)$', content, re.MULTILINE)
    if not categories:
        return False, "没有发现分类标题 (## 开头的行)", len(xml_links)
    
    return True, f"验证通过: 发现 {len(categories)} 个分类，{len(xml_links)} 个有效链接", len(xml_links)


def main():
    if len(sys.argv) != 2:
        print("用法: python validate_source.py <markdown_file>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    
    print(f"正在验证文件: {md_file}")
    
    is_valid, message, link_count = validate_markdown_file(md_file)
    
    print(message)
    
    if is_valid:
        print("✅ 文件验证通过")
        sys.exit(0)
    else:
        print("❌ 文件验证失败")
        sys.exit(1)


if __name__ == '__main__':
    main()