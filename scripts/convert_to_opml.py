#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple


def parse_markdown_file(md_file_path: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    解析 markdown 文件，提取分类和公众号信息
    返回格式: {category: [(name, xml_url), ...]}
    """
    categories = {}
    current_category = None
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 检测分类标题 (## 开头)
        if line.startswith('## ') and not line.startswith('## '):
            continue
        elif line.startswith('## '):
            current_category = line[3:].strip()
            if current_category not in categories:
                categories[current_category] = []
        
        # 检测链接行 [name](url)
        elif current_category and line.startswith('[') and '](' in line and line.endswith('.xml)'):
            match = re.search(r'\[([^\]]+)\]\(([^)]+\.xml)\)', line)
            if match:
                name = match.group(1)
                xml_url = match.group(2)
                # 验证是否是有效的 wechat2rss XML 链接
                if 'wechat2rss.xlab.app/feed/' in xml_url:
                    categories[current_category].append((name, xml_url))
    
    return categories


def create_opml(categories: Dict[str, List[Tuple[str, str]]], output_file: str):
    """
    创建 OPML XML 文件
    """
    # 创建根元素
    opml = ET.Element('opml', version='1.0')
    
    # 创建 head 部分
    head = ET.SubElement(opml, 'head')
    title = ET.SubElement(head, 'title')
    title.text = '安全技术公众号 created by tmr [https://wechat2rss.xlab.app]'
    
    # 创建 body 部分
    body = ET.SubElement(opml, 'body')
    
    # 为每个分类创建 outline
    for category, feeds in categories.items():
        if not feeds:  # 跳过空分类
            continue
            
        category_outline = ET.SubElement(body, 'outline', 
                                       text=category, 
                                       title=category)
        
        # 为每个公众号创建 outline
        for name, xml_url in feeds:
            feed_outline = ET.SubElement(category_outline, 'outline',
                                       text=name,
                                       title=name,
                                       type='rss',
                                       xmlUrl=xml_url,
                                       htmlUrl=xml_url)
    
    # 创建 XML 树并写入文件
    tree = ET.ElementTree(opml)
    ET.indent(tree, space="    ")
    
    # 写入文件时添加 XML 声明
    with open(output_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding='utf-8', xml_declaration=False)


def main():
    if len(sys.argv) != 3:
        print("用法: python convert_to_opml.py <input_md_file> <output_opml_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # 解析 markdown 文件
        print(f"正在解析 {input_file}...")
        categories = parse_markdown_file(input_file)
        
        # 统计信息
        total_feeds = sum(len(feeds) for feeds in categories.values())
        print(f"发现 {len(categories)} 个分类，共 {total_feeds} 个公众号")
        
        if total_feeds == 0:
            print("警告: 没有发现有效的公众号链接！")
            sys.exit(1)
        
        # 生成 OPML 文件
        print(f"正在生成 {output_file}...")
        create_opml(categories, output_file)
        
        print("转换完成！")
        
        # 打印统计信息
        for category, feeds in categories.items():
            if feeds:
                print(f"  {category}: {len(feeds)} 个公众号")
                
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()