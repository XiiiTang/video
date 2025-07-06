import os
import subprocess

def main():
    """
    批量转换H:\video文件夹中的XML弹幕文件为ASS文件
    """
    # 固定处理H:\video文件夹
    folder_path = r"H:\video"
    
    # danmu2ass.exe 的路径
    danmu2ass_path = r"C:\Users\Xiiii\Downloads\danmu2ass-windows\danmu2ass.exe"
    
    # 检查danmu2ass.exe是否存在
    if not os.path.exists(danmu2ass_path):
        print(f"错误: 找不到 danmu2ass.exe 文件: {danmu2ass_path}")
        return
    
    # 检查输入文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹不存在: {folder_path}")
        return
    
    # 预设参数
    params = [
        "--width", "1920",
        "--height", "1080", 
        "--float-percentage", "0.35",
        "--font-size", "32",
        "--width-ratio", "1.2",
        "--horizontal-gap", "20",
        "--lane-size", "32",
        "--font", "黑体",
        "--bold",
        "--outline", "0.8",
        "--alpha", "0.76",
        "--duration", "15",
        "--no-web"  # 使用CLI模式
    ]
    
    # 查找所有XML文件
    xml_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    if not xml_files:
        print(f"在文件夹 {folder_path} 中没有找到XML文件")
        return
    
    print(f"找到 {len(xml_files)} 个XML文件，开始转换...")
    
    success_count = 0
    failed_count = 0
    
    for xml_file in xml_files:
        try:
            # 构建输出文件名（将.xml替换为.ass）
            output_file = xml_file.rsplit('.', 1)[0] + '.ass'
            
            # 构建完整的命令
            cmd = [danmu2ass_path] + params + ["-o", output_file, xml_file]
            
            print(f"正在转换: {os.path.basename(xml_file)}")
            
            # 执行转换命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print(f"✓ 成功转换: {os.path.basename(xml_file)} -> {os.path.basename(output_file)}")
                success_count += 1
            else:
                print(f"✗ 转换失败: {os.path.basename(xml_file)}")
                print(f"  错误信息: {result.stderr}")
                failed_count += 1
                
        except Exception as e:
            print(f"✗ 处理文件时出错 {os.path.basename(xml_file)}: {str(e)}")
            failed_count += 1
    
    print(f"\n转换完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {failed_count} 个文件")

if __name__ == "__main__":
    main()