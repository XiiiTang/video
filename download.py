#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频下载脚本
使用yt-dlp下载配置文件中指定的视频
"""

import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self, config_file: str = "config.json"):
        """
        初始化视频下载器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            sys.exit(1)
            
    def check_yt_dlp(self) -> bool:
        """检查yt-dlp是否已安装"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"yt-dlp版本: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("yt-dlp未安装或不在PATH中")
            logger.info("请先安装yt-dlp: pip install yt-dlp")
            return False
            
    def build_command(self, url: str, download_path: str) -> List[str]:
        """构建yt-dlp命令"""
        options = self.config.get('yt_dlp_options', {})
        
        cmd = ['yt-dlp']
        
        # 格式选择
        if options.get('format'):
            cmd.extend(['-f', options['format']])
            
        # 格式排序
        if options.get('format_sort'):
            cmd.extend(['--format-sort', options['format_sort']])
            
        # 合并输出格式
        if options.get('merge_output_format'):
            cmd.extend(['--merge-output-format', options['merge_output_format']])
            
        # 写入缩略图
        if options.get('write_thumbnail'):
            cmd.append('--write-thumbnail')
            
        # 嵌入缩略图
        if options.get('embed_thumbnail'):
            cmd.append('--embed-thumbnail')
            
        # 所有字幕
        if options.get('all_subs'):
            cmd.append('--all-subs')
            
        # 从浏览器获取cookies
        if options.get('cookies_from_browser'):
            cmd.extend(['--cookies-from-browser', options['cookies_from_browser']])
            
        # 输出模板
        if options.get('output_template'):
            output_path = os.path.join(download_path, options['output_template'])
            cmd.extend(['-o', output_path])
            
        # 添加URL
        cmd.append(url)
        
        return cmd
        
    def download_url(self, url: str, download_path: str, description: str) -> bool:
        """下载单个URL"""
        logger.info(f"开始下载: {description}")
        logger.info(f"URL: {url}")
        logger.info(f"下载路径: {download_path}")
        
        # 确保下载路径存在
        Path(download_path).mkdir(parents=True, exist_ok=True)
        
        # 构建命令
        cmd = self.build_command(url, download_path)
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行下载 - 实时显示yt-dlp输出
            print(f"\n{'='*60}")
            print(f"开始下载: {description}")
            print(f"{'='*60}")
            
            result = subprocess.run(cmd, cwd=download_path, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info(f"下载成功: {description}")
                return True
            else:
                logger.error(f"下载失败: {description}")
                return False
                
        except Exception as e:
            logger.error(f"下载异常: {description} - {str(e)}")
            return False
            
    def download_all(self) -> None:
        """下载所有配置的视频"""
        if not self.check_yt_dlp():
            return
            
        download_configs = self.config.get('download_configs', [])
        
        if not download_configs:
            logger.warning("配置文件中没有找到下载配置")
            return
            
        total_configs = len(download_configs)
        logger.info(f"共找到 {total_configs} 个下载配置")
        
        success_count = 0
        fail_count = 0
        
        for i, config in enumerate(download_configs, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"处理配置 {i}/{total_configs}")
            
            download_path = config.get('download_path', '')
            description = config.get('description', '未知')
            urls = config.get('urls', [])
            
            if not download_path:
                logger.error(f"配置 {i} 缺少下载路径")
                fail_count += 1
                continue
                
            if not urls:
                logger.warning(f"配置 {i} 没有URL")
                continue
                
            logger.info(f"配置描述: {description}")
            logger.info(f"URL数量: {len(urls)}")
            
            # 下载每个URL
            for j, url in enumerate(urls, 1):
                logger.info(f"\n下载 URL {j}/{len(urls)}")
                if self.download_url(url, download_path, f"{description} - {j}"):
                    success_count += 1
                else:
                    fail_count += 1
                    
        logger.info(f"\n{'='*50}")
        logger.info(f"下载完成! 成功: {success_count}, 失败: {fail_count}")
        
    def interactive_add_config(self) -> None:
        """交互式添加配置"""
        print("\n=== 添加新的下载配置 ===")
        
        download_path = input("请输入下载路径: ").strip()
        description = input("请输入描述: ").strip()
        
        urls = []
        print("请输入URL（每行一个，输入空行结束）:")
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
            
        if not download_path or not description or not urls:
            print("输入不完整，取消添加")
            return
            
        new_config = {
            "download_path": download_path,
            "description": description,
            "urls": urls
        }
        
        self.config['download_configs'].append(new_config)
        
        # 保存配置文件
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            print(f"配置已添加并保存到 {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")

def main():
    """主函数"""
    downloader = VideoDownloader()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'add':
            downloader.interactive_add_config()
        elif command == 'download':
            downloader.download_all()
        else:
            print("未知命令，支持的命令: add, download")
    else:
        print("视频下载器")
        print("使用方法:")
        print("  python download.py add      - 添加新的下载配置")
        print("  python download.py download - 开始下载")
        
        choice = input("\n请选择操作 (add/download): ").strip().lower()
        if choice == 'add':
            downloader.interactive_add_config()
        elif choice == 'download':
            downloader.download_all()
        else:
            print("无效选择")

if __name__ == "__main__":
    main()
