#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量合并ASS弹幕文件和SRT字幕文件
扫描指定目录及其子目录，找到所有.danmaku.ass文件，并与对应的.srt文件合并
"""

import re
import os
import glob
from datetime import datetime


def parse_srt_time(time_str):
    """将SRT时间格式转换为ASS时间格式"""
    # SRT格式: 00:00:07,560 --> 00:00:08,300
    # ASS格式: 0:00:07.56
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    # ASS格式不需要前导零的小时
    return f"{hours}:{minutes:02d}:{seconds:06.2f}"


def parse_srt_file(srt_path):
    """解析SRT文件"""
    subtitles = []
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            with open(srt_path, 'r', encoding='gbk') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"无法读取SRT文件: {srt_path}")
            return subtitles
    
    # 按空行分割字幕块
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # 序号
            index = lines[0]
            # 时间
            time_line = lines[1]
            # 字幕内容（可能有多行）
            subtitle_text = '\n'.join(lines[2:])
            
            # 解析时间
            time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
            if time_match:
                start_time = parse_srt_time(time_match.group(1))
                end_time = parse_srt_time(time_match.group(2))
                
                subtitles.append({
                    'index': index,
                    'start': start_time,
                    'end': end_time,
                    'text': subtitle_text
                })
    
    return subtitles


def read_ass_file(ass_path):
    """读取ASS文件"""
    try:
        with open(ass_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            with open(ass_path, 'r', encoding='gbk') as f:
                return f.read()
        except UnicodeDecodeError:
            print(f"无法读取ASS文件: {ass_path}")
            return ""


def merge_ass_srt(ass_path, srt_path, output_path):
    """合并ASS和SRT文件"""
    print(f"正在合并: {os.path.basename(ass_path)} + {os.path.basename(srt_path)}")
    
    # 读取ASS文件内容
    ass_content = read_ass_file(ass_path)
    if not ass_content:
        return False
    
    # 解析SRT文件
    srt_subtitles = parse_srt_file(srt_path)
    if not srt_subtitles:
        print(f"  警告: SRT文件中没有找到字幕内容")
        return False
    
    print(f"  SRT文件中找到 {len(srt_subtitles)} 条字幕")
    
    # 分析ASS文件结构
    lines = ass_content.split('\n')
    
    # 找到样式定义部分，添加新的字幕样式
    style_section_found = False
    events_section_found = False
    output_lines = []
    
    for line in lines:
        if line.strip() == '[V4+ Styles]':
            style_section_found = True
            output_lines.append(line)
        elif line.strip() == '[Events]':
            events_section_found = True
            # 在Events部分之前添加字幕样式
            if style_section_found:
                # 添加字幕样式 - 增大字体到42，提高字幕位置到90
                subtitle_style = "Style: Subtitle,黑体,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0.00,0.00,1,2.0,0,2,20,20,90,1"
                output_lines.append(subtitle_style)
            output_lines.append(line)
        elif line.strip().startswith('[') and events_section_found:
            # 在Events部分结束前添加SRT字幕
            # 添加SRT字幕作为对话
            for sub in srt_subtitles:
                # 清理字幕文本，移除换行符并转义特殊字符
                clean_text = sub['text'].replace('\n', '\\N').replace('{', '\\{').replace('}', '\\}')
                dialogue_line = f"Dialogue: 0,{sub['start']},{sub['end']},Subtitle,,0,0,0,,{clean_text}"
                output_lines.append(dialogue_line)
            
            output_lines.append(line)
        else:
            output_lines.append(line)
    
    # 如果没有找到其他部分，直接在最后添加SRT字幕
    if events_section_found and not any(line.strip().startswith('[') and line.strip() != '[Events]' for line in lines[lines.index('[Events]')+1:]):
        for sub in srt_subtitles:
            clean_text = sub['text'].replace('\n', '\\N').replace('{', '\\{').replace('}', '\\}')
            dialogue_line = f"Dialogue: 0,{sub['start']},{sub['end']},Subtitle,,0,0,0,,{clean_text}"
            output_lines.append(dialogue_line)
    
    # 写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"  合并完成: {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"  错误: 无法写入输出文件 {output_path}: {e}")
        return False


def find_matching_srt_files(ass_file_path):
    """根据ASS文件路径，查找匹配的SRT文件"""
    # 获取ASS文件的基本名称（去掉.danmaku.ass扩展名）
    base_name = ass_file_path.replace('.danmaku.ass', '')
    
    # 查找所有可能的SRT文件
    srt_patterns = [
        f"{base_name}.*.srt",  # 匹配所有类型的SRT文件
    ]
    
    matching_srt_files = []
    for pattern in srt_patterns:
        matching_files = glob.glob(pattern)
        matching_srt_files.extend(matching_files)
    
    # 去重并排序
    matching_srt_files = sorted(list(set(matching_srt_files)))
    
    return matching_srt_files


def scan_directory(root_dir):
    """扫描目录，找到所有.danmaku.ass文件"""
    ass_files = []
    
    print(f"正在扫描目录: {root_dir}")
    
    # 使用glob模式递归查找所有.danmaku.ass文件
    pattern = os.path.join(root_dir, '**', '*.danmaku.ass')
    ass_files = glob.glob(pattern, recursive=True)
    
    print(f"找到 {len(ass_files)} 个.danmaku.ass文件")
    
    return ass_files


def generate_output_filename(srt_file_path, ass_file_path):
    """生成输出文件名"""
    # 获取SRT文件名的特殊部分（如.zh-CN, .ai-zh等）
    srt_basename = os.path.basename(srt_file_path)
    ass_basename = os.path.basename(ass_file_path)
    
    # 提取ASS文件的基本名称
    ass_base = ass_basename.replace('.danmaku.ass', '')
    
    # 从SRT文件名中提取语言标识
    srt_base = srt_basename.replace('.srt', '')
    
    # 查找语言标识部分
    if ass_base in srt_base:
        lang_part = srt_base.replace(ass_base, '')
        if lang_part.startswith('.'):
            lang_part = lang_part[1:]  # 移除开头的点
        
        # 生成输出文件名
        output_filename = f"{ass_base}.{lang_part}.merged.ass"
    else:
        # 如果无法匹配，使用默认命名
        output_filename = f"{ass_base}.merged.ass"
    
    return os.path.join(os.path.dirname(ass_file_path), output_filename)


def main():
    """主函数"""
    # 扫描根目录
    root_directory = r"H:\video"
    
    print("=" * 60)
    print("批量合并ASS弹幕文件和SRT字幕文件")
    print("=" * 60)
    
    # 扫描目录，找到所有.danmaku.ass文件
    ass_files = scan_directory(root_directory)
    
    if not ass_files:
        print("未找到任何.danmaku.ass文件")
        return
    
    total_merged = 0
    total_skipped = 0
    
    # 处理每个ASS文件
    for ass_file in ass_files:
        print(f"\n处理文件: {os.path.basename(ass_file)}")
        
        # 查找匹配的SRT文件
        matching_srt_files = find_matching_srt_files(ass_file)
        
        if not matching_srt_files:
            print(f"  未找到匹配的SRT文件，跳过")
            total_skipped += 1
            continue
        
        print(f"  找到 {len(matching_srt_files)} 个匹配的SRT文件:")
        for srt_file in matching_srt_files:
            print(f"    - {os.path.basename(srt_file)}")
        
        # 与每个SRT文件合并
        for srt_file in matching_srt_files:
            # 生成输出文件名
            output_file = generate_output_filename(srt_file, ass_file)
            
            # 检查输出文件是否已存在
            if os.path.exists(output_file):
                print(f"  覆盖现有文件: {os.path.basename(output_file)}")
            
            # 执行合并
            if merge_ass_srt(ass_file, srt_file, output_file):
                total_merged += 1
            else:
                total_skipped += 1
    
    print("\n" + "=" * 60)
    print(f"处理完成！")
    print(f"成功合并: {total_merged} 个文件")
    print(f"跳过: {total_skipped} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
