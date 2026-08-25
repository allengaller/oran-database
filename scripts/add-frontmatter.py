#!/usr/bin/env python3
"""批量为 Markdown 文件添加 frontmatter 元数据"""

import os
import re
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path(__file__).parent.parent
EXCLUDE_DIRS = {'.git', '.qoder', '.trae', 'node_modules', '.claude'}

def get_category(filepath: Path) -> str:
    """根据文件路径推断分类"""
    parts = filepath.parts
    
    # 根目录文件
    if len(parts) == 1:
        name = parts[0].lower()
        if 'readme' in name:
            return 'project_overview'
        elif 'glossary' in name:
            return 'reference'
        elif 'head-first' in name:
            return 'guide'
        else:
            return 'documentation'
    
    # 编号目录
    if parts[0].startswith(('0', '1', '2', '3')):
        dir_name = parts[0]
        # 提取目录描述
        dir_map = {
            '01': 'architecture',
            '02': 'core_components',
            '03': 'interface_standards',
            '04': 'disaggregation',
            '05': 'cloud_integration',
            '06': 'working_groups',
            '07': 'ric_development',
            '08': 'deployment',
            '09': 'standards_compliance',
            '10': 'application_scenarios',
            '11': 'academic_papers',
            '12': 'security_privacy',
            '13': 'testing_validation',
            '14': 'operations_management',
            '15': 'future_development',
            '16': 'industry_solutions',
            '17': 'open_source',
            '18': 'cost_analysis',
            '19': 'talent_development',
            '20': 'ecosystem',
            '21': 'case_studies',
            '22': 'tool_platforms',
            '23': 'international',
            '24': 'sustainability',
            '25': 'legal_regulations',
            '26': 'performance_optimization',
            '27': 'troubleshooting',
            '28': 'monitoring_alerting',
            '29': 'security_threats',
            '30': 'best_practices',
            '31': 'ai_ran_convergence',
            '32': 'ai_ran_security',
            '33': 'oran_for_dummies',
            '34': 'vendor_profiles',
        }
        prefix = dir_name[:2]
        return dir_map.get(prefix, 'documentation')
    
    return 'documentation'


def get_language(filepath: Path) -> str:
    """推断文档语言"""
    name = filepath.name.lower()
    if '-zh' in name:
        return 'zh-CN'
    return 'en-US'


def has_frontmatter(content: str) -> bool:
    """检查是否已有 frontmatter"""
    return content.startswith('---\n')


def generate_frontmatter(filepath: Path, content: str) -> str:
    """生成 frontmatter"""
    category = get_category(filepath)
    language = get_language(filepath)
    
    # 提取标题（第一个 # 标题）
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem.replace('-', ' ').title()
    
    # 提取描述（第一个段落）
    desc_match = re.search(r'^(?!#)(.+?)$', content, re.MULTILINE)
    description = desc_match.group(1).strip()[:100] if desc_match else f"Documentation for {title}"
    
    # 生成关键词
    keywords = []
    if 'oran' in content.lower():
        keywords.append('O-RAN')
    if 'ai' in content.lower() and 'ran' in content.lower():
        keywords.append('AI-RAN')
    if 'ric' in content.lower():
        keywords.append('RIC')
    if '5g' in content.lower():
        keywords.append('5G')
    if not keywords:
        keywords.append(category.replace('_', '-'))
    
    frontmatter = f"""---
title: "{title}"
description: "{description}"
category: "{category}"
language: "{language}"
version: "1.0"
last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
keywords: {keywords}
---

"""
    return frontmatter


def process_file(filepath: Path) -> bool:
    """处理单个文件"""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        if has_frontmatter(content):
            return False
        
        frontmatter = generate_frontmatter(filepath, content)
        new_content = frontmatter + content
        
        filepath.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """主函数"""
    print("🔍 扫描 Markdown 文件...")
    
    md_files = []
    for root, dirs, files in os.walk(WORKSPACE):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith('.md'):
                filepath = Path(root) / file
                md_files.append(filepath)
    
    print(f"📁 找到 {len(md_files)} 个 Markdown 文件")
    
    # 检查哪些需要添加 frontmatter
    need_frontmatter = []
    for filepath in md_files:
        try:
            content = filepath.read_text(encoding='utf-8')
            if not has_frontmatter(content):
                need_frontmatter.append(filepath)
        except:
            pass
    
    print(f"📝 需要添加 frontmatter: {len(need_frontmatter)} 个文件")
    
    # 批量处理
    processed = 0
    for filepath in need_frontmatter:
        if process_file(filepath):
            processed += 1
            if processed % 50 == 0:
                print(f"  ✅ 已处理 {processed}/{len(need_frontmatter)}")
    
    print(f"\n✅ 完成！已为 {processed} 个文件添加 frontmatter")


if __name__ == '__main__':
    main()
