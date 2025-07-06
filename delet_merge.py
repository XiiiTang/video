import os
import glob

def delete_merged_ass_files(directory):
    """
    扫描指定目录及其子目录，删除所有.merged.ass文件
    
    Args:
        directory (str): 要扫描的目录路径
    """
    # 使用glob递归搜索所有.merged.ass文件
    pattern = os.path.join(directory, "**", "*.merged.ass")
    merged_ass_files = glob.glob(pattern, recursive=True)
    
    if not merged_ass_files:
        print("未找到任何.merged.ass文件")
        return
    
    print(f"\n找到 {len(merged_ass_files)} 个.merged.ass文件")
    
    # 询问是否显示文件列表
    show_list = input("是否显示所有文件列表? (y/N): ").lower().strip()
    
    if show_list == 'y' or show_list == 'yes':
        print("\n文件列表:")
        for i, file in enumerate(merged_ass_files, 1):
            print(f"  {i}. {file}")
    
    # 询问用户确认删除
    confirm = input(f"\n是否确认删除这 {len(merged_ass_files)} 个文件? (y/N): ").lower().strip()
    
    if confirm == 'y' or confirm == 'yes':
        deleted_count = 0
        for file_path in merged_ass_files:
            try:
                os.remove(file_path)
                print(f"已删除: {file_path}")
                deleted_count += 1
            except OSError as e:
                print(f"删除失败 {file_path}: {e}")
        
        print(f"\n成功删除 {deleted_count} 个文件")
    else:
        print("取消删除操作")

def main():
    # 设置要扫描的目录
    video_directory = r"H:\video"
    
    # 检查目录是否存在
    if not os.path.exists(video_directory):
        print(f"错误: 目录 {video_directory} 不存在")
        return
    
    print(f"正在扫描目录: {video_directory}")
    print("搜索所有.merged.ass文件...")
    
    # 执行删除操作
    delete_merged_ass_files(video_directory)

if __name__ == "__main__":
    main()