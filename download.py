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

        # 获取现有的配置组（配置描述和路径的映射）
        existing_configs = {}
        for config in self.config.get('download_configs', []):
            desc = config.get('description', '').strip()
            path = config.get('download_path', '').strip()
            if desc and path:
                existing_configs[desc] = path

        if existing_configs:
            print("\n现有的配置组:")
            for i, (desc, path) in enumerate(existing_configs.items(), 1):
                print(f"{i}. {desc} -> {path}")

            choice = input("\n选择操作:\n1. 向现有配置组添加URL\n2. 创建新配置组\n请选择 (1/2): ").strip()

            if choice == '1':
                try:
                    config_index = int(input("请选择配置组编号: ")) - 1
                    configs_list = list(existing_configs.items())
                    if 0 <= config_index < len(configs_list):
                        selected_desc, selected_path = configs_list[config_index]
                        print(f"选择的配置组: {selected_desc}")
                        print(f"对应路径: {selected_path}")

                        # 找到对应的配置
                        target_config = None
                        for config in self.config.get('download_configs', []):
                            if config.get('description') == selected_desc:
                                target_config = config
                                break

                        if target_config:
                            urls_added = self._add_urls_to_config(target_config, selected_desc)
                            if urls_added > 0 and self._save_config():
                                print(f"成功向配置组 '{selected_desc}' 添加了 {urls_added} 个URL")
                            elif urls_added == 0:
                                print("未添加任何URL")
                        else:
                            print(f"未找到配置组: {selected_desc}")
                        return
                    else:
                        print("无效的配置组编号")
                        return
                except ValueError:
                    print("请输入有效的数字")
                    return
            elif choice == '2':
                # 继续创建新配置组
                pass
            else:
                print("无效选择")
                return

        # 创建新配置组
        description = input("请输入配置组名称: ").strip()

        # 检查配置组名称是否已存在
        if description in existing_configs:
            print(f"配置组 '{description}' 已存在，请使用不同的名称")
            return

        download_path = input("请输入下载路径: ").strip()

        # 检查路径是否已被其他配置组使用
        for existing_desc, existing_path in existing_configs.items():
            if existing_path == download_path:
                print(f"路径 '{download_path}' 已被配置组 '{existing_desc}' 使用")
                print("每个配置组必须对应唯一的下载路径")
                return

        # 创建新配置组
        new_config = {
            "download_path": download_path,
            "description": description,
            "urls": []
        }

        # 添加URL到新配置组
        urls_added = self._add_urls_to_config(new_config, description)

        if not download_path or not description or urls_added == 0:
            print("输入不完整，取消添加")
            return

        self.config['download_configs'].append(new_config)

        # 保存配置文件
        if self._save_config():
            print(f"配置组 '{description}' 已添加并保存到 {self.config_file}")
        else:
            # 如果保存失败，从配置中移除刚添加的配置组
            self.config['download_configs'].pop()

    def _save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _add_urls_to_config(self, target_config: dict, config_desc: str) -> int:
        """向指定配置添加URL，返回添加的URL数量"""
        print(f"\n向配置组 '{config_desc}' 添加URL:")
        print("请输入URL和描述（输入空行结束）:")
        urls_added = 0

        while True:
            url = input("URL: ").strip()
            if not url:
                break
            url_description = input("描述: ").strip()
            if not url_description:
                url_description = f"视频 {len(target_config['urls']) + urls_added + 1}"

            target_config['urls'].append({
                "url": url,
                "description": url_description
            })
            urls_added += 1

        return urls_added

    def list_configs(self) -> None:
        """列出所有配置组"""
        download_configs = self.config.get('download_configs', [])

        if not download_configs:
            print("没有找到任何配置组")
            return

        print(f"\n共找到 {len(download_configs)} 个配置组：")
        print("="*80)

        for i, config in enumerate(download_configs, 1):
            desc = config.get('description', '无描述')
            path = config.get('download_path', '无路径')
            url_count = len(config.get('urls', []))

            print(f"{i}. 配置组: {desc}")
            print(f"   对应路径: {path}")
            print(f"   URL数量: {url_count}")

            # 显示URL详情
            urls = config.get('urls', [])
            for j, url_config in enumerate(urls, 1):
                if isinstance(url_config, str):
                    print(f"   URL {j}: {url_config}")
                else:
                    print(f"   URL {j}: {url_config.get('description', '无描述')}")
                    print(f"         {url_config.get('url', '无URL')}")
            print("-"*80)
            
    def interactive_add_url(self) -> None:
        """交互式向现有配置组添加URL"""
        download_configs = self.config.get('download_configs', [])

        if not download_configs:
            print("没有找到任何配置组")
            return

        print("\n现有的配置组:")
        for i, config in enumerate(download_configs):
            desc = config.get('description', '无描述')
            path = config.get('download_path', '无路径')
            url_count = len(config.get('urls', []))
            print(f"{i+1}. {desc} -> {path} (已有{url_count}个URL)")

        try:
            config_index = int(input(f"\n请选择配置组 (1-{len(download_configs)}): ")) - 1

            if config_index < 0 or config_index >= len(download_configs):
                print("无效的配置组编号")
                return

            selected_config = download_configs[config_index]
            config_desc = selected_config.get('description', '无描述')

            print(f"\n选择的配置组: {config_desc}")
            urls_added = self._add_urls_to_config(selected_config, config_desc)

            if urls_added > 0 and self._save_config():
                print(f"成功向配置组 '{config_desc}' 添加了 {urls_added} 个URL")
            elif urls_added == 0:
                print("未添加任何URL")

        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"添加URL时发生错误: {e}")

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
        print("视频下载器 - 配置组管理系统")
        print("每个配置组对应唯一的下载路径，选择配置组即选择下载路径")
        print("\n使用方法:")
        print("  python download.py add      - 添加新的配置组或向现有配置组添加URL")
        print("  python download.py addurl   - 向现有配置组添加URL")
        print("  python download.py list     - 列出所有配置组")
        print("  python download.py download - 下载所有配置组的视频")
        print("  python download.py select   - 选择性下载特定视频")
        
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
