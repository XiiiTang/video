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
            for j, url_config in enumerate(urls, 1):
                logger.info(f"\n下载 URL {j}/{len(urls)}")
                
                # 兼容旧格式（字符串）和新格式（字典）
                if isinstance(url_config, str):
                    url = url_config
                    url_description = f"{description} - {j}"
                else:
                    url = url_config.get('url', '')
                    url_description = url_config.get('description', f"{description} - {j}")
                
                if not url:
                    logger.error(f"URL配置 {j} 缺少URL")
                    fail_count += 1
                    continue
                    
                if self.download_url(url, download_path, url_description):
                    success_count += 1
                else:
                    fail_count += 1
                    
        logger.info(f"\n{'='*50}")
        logger.info(f"下载完成! 成功: {success_count}, 失败: {fail_count}")
        
    def interactive_add_config(self) -> None:
        """交互式添加配置"""
        print("\n=== 添加新的下载配置 ===")
        
        download_path = input("请输入下载路径: ").strip()
        description = input("请输入配置描述: ").strip()
        
        urls = []
        print("请输入URL和描述（输入空行结束）:")
        while True:
            url = input("URL: ").strip()
            if not url:
                break
            url_description = input("描述: ").strip()
            if not url_description:
                url_description = f"视频 {len(urls) + 1}"
            
            urls.append({
                "url": url,
                "description": url_description
            })
            
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
            
    def list_configs(self) -> None:
        """列出所有配置"""
        download_configs = self.config.get('download_configs', [])
        
        if not download_configs:
            print("没有找到任何配置")
            return
            
        print(f"\n共找到 {len(download_configs)} 个配置：")
        print("="*60)
        
        for i, config in enumerate(download_configs):
            print(f"{i}: {config.get('description', '无描述')}")
            print(f"   路径: {config.get('download_path', '无路径')}")
            print(f"   URL数量: {len(config.get('urls', []))}")
            
            # 显示URL详情
            urls = config.get('urls', [])
            for j, url_config in enumerate(urls):
                if isinstance(url_config, str):
                    print(f"   URL {j+1}: {url_config}")
                else:
                    print(f"   URL {j+1}: {url_config.get('description', '无描述')}")
                    print(f"         {url_config.get('url', '无URL')}")
            print("-"*60)
            
    def interactive_add_url(self) -> None:
        """交互式向现有配置添加URL"""
        self.list_configs()
        
        try:
            config_index = int(input("\n请输入要添加URL的配置索引: "))
            url = input("请输入URL: ").strip()
            url_description = input("请输入URL描述: ").strip()
            
            if not url or not url_description:
                print("输入不完整，取消添加")
                return
                
            if self.add_url_to_config(config_index, url, url_description):
                print("URL添加成功")
            else:
                print("URL添加失败")
                
        except ValueError:
            print("请输入有效的索引数字")
        except Exception as e:
            print(f"添加URL时发生错误: {e}")
            
    def add_url_to_config(self, config_index: int, url: str, url_description: str) -> bool:
        """向指定配置添加URL"""
        try:
            if config_index < 0 or config_index >= len(self.config['download_configs']):
                logger.error(f"配置索引超出范围: {config_index}")
                return False
                
            new_url = {
                "url": url,
                "description": url_description
            }
            
            self.config['download_configs'][config_index]['urls'].append(new_url)
            
            # 保存配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            logger.info(f"成功添加URL到配置 {config_index}")
            return True
            
        except Exception as e:
            logger.error(f"添加URL失败: {e}")
            return False
        
    def interactive_download(self) -> None:
        """交互式选择下载"""
        if not self.check_yt_dlp():
            return
            
        # 直接进入选择特定URL下载，不显示二级菜单
        self.interactive_select_download()
            
    def interactive_select_download(self) -> None:
        """交互式选择特定URL下载"""
        download_configs = self.config.get('download_configs', [])
        
        if not download_configs:
            print("没有找到任何配置")
            return
            
        # 显示所有配置和URL
        print("\n=== 可用的下载项目 ===")
        url_list = []
        
        for i, config in enumerate(download_configs):
            print(f"\n配置 {i+1}: {config.get('description', '无描述')}")
            print(f"路径: {config.get('download_path', '无路径')}")
            
            urls = config.get('urls', [])
            for j, url_config in enumerate(urls):
                url_index = len(url_list) + 1
                
                if isinstance(url_config, str):
                    url = url_config
                    url_description = f"视频 {j+1}"
                else:
                    url = url_config.get('url', '')
                    url_description = url_config.get('description', f"视频 {j+1}")
                
                url_list.append({
                    'config_index': i,
                    'url': url,
                    'description': url_description,
                    'download_path': config.get('download_path', '')
                })
                
                print(f"  {url_index}. {url_description}")
                
        if not url_list:
            print("没有找到任何URL")
            return
            
        print(f"\n共 {len(url_list)} 个下载项目")
        
        # 获取用户选择
        while True:
            try:
                selection = input(f"\n请输入要下载的项目编号 (1-{len(url_list)}), 用逗号分隔多个项目，或输入 'all' 下载全部: ").strip()
                
                if selection.lower() == 'all':
                    selected_indices = list(range(len(url_list)))
                    break
                elif selection.lower() == 'exit':
                    return
                else:
                    # 解析用户输入的编号
                    selected_indices = []
                    for num_str in selection.split(','):
                        num = int(num_str.strip())
                        if 1 <= num <= len(url_list):
                            selected_indices.append(num - 1)
                        else:
                            print(f"编号 {num} 超出范围")
                            continue
                    
                    if selected_indices:
                        break
                    else:
                        print("没有有效的选择")
                        continue
                        
            except ValueError:
                print("请输入有效的数字")
                continue
        
        # 下载选中的URL
        print(f"\n开始下载 {len(selected_indices)} 个项目...")
        success_count = 0
        fail_count = 0
        
        for i, url_index in enumerate(selected_indices, 1):
            url_info = url_list[url_index]
            print(f"\n下载进度: {i}/{len(selected_indices)}")
            
            if self.download_url(url_info['url'], url_info['download_path'], url_info['description']):
                success_count += 1
            else:
                fail_count += 1
                
        print(f"\n{'='*50}")
        print(f"选择性下载完成! 成功: {success_count}, 失败: {fail_count}")

def main():
    """主函数"""
    downloader = VideoDownloader()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'add':
            downloader.interactive_add_config()
        elif command == 'addurl':
            downloader.interactive_add_url()
        elif command == 'list':
            downloader.list_configs()
        elif command == 'download':
            downloader.download_all()
        elif command == 'select':
            downloader.interactive_download()
        else:
            print("未知命令，支持的命令: add, addurl, list, download, select")
    else:
        print("视频下载器")
        print("使用方法:")
        print("  python download.py add      - 添加新的下载配置")
        print("  python download.py addurl   - 向现有配置添加URL")
        print("  python download.py list     - 列出所有配置")
        print("  python download.py download - 开始下载全部")
        print("  python download.py select   - 选择性下载")
        
        choice = input("\n请选择操作 (add/addurl/list/download/select): ").strip().lower()
        if choice == 'add':
            downloader.interactive_add_config()
        elif choice == 'addurl':
            downloader.interactive_add_url()
        elif choice == 'list':
            downloader.list_configs()
        elif choice == 'download':
            downloader.download_all()
        elif choice == 'select':
            downloader.interactive_download()
        else:
            print("无效选择")

if __name__ == "__main__":
    main()
