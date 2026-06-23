#!/usr/bin/env python3
"""
打包工具 - 将HTML文件打包成培训系统可用的ZIP压缩包
"""

import sys
import os
import zipfile
from pathlib import Path

def package_html(html_path, output_name=None):
    """
    将HTML文件打包成ZIP压缩包
    
    Args:
        html_path: HTML文件路径
        output_name: 输出zip文件名（可选，默认使用HTML文件名）
    """
    html_path = Path(html_path)
    
    if not html_path.exists():
        print(f"[错误] 文件不存在: {html_path}")
        return False
    
    if not html_path.suffix == '.html':
        print(f"[错误] 不是HTML文件: {html_path}")
        return False
    
    # 确定输出文件名
    if output_name is None:
        output_name = html_path.stem + '.zip'
    else:
        if not output_name.endswith('.zip'):
            output_name += '.zip'
    
    output_path = html_path.parent / output_name
    
    # 创建ZIP压缩包
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 将HTML文件添加到压缩包根目录，命名为 index.html
            zf.write(html_path, 'index.html')
        
        print(f"[成功] 已创建压缩包: {output_path}")
        print(f"[信息] 文件大小: {output_path.stat().st_size / 1024:.1f} KB")
        return str(output_path)
    
    except Exception as e:
        print(f"[错误] 创建压缩包失败: {e}")
        return False

def package_folder(folder_path, output_name=None):
    """
    将整个文件夹打包成ZIP压缩包
    
    Args:
        folder_path: 文件夹路径
        output_name: 输出zip文件名（可选）
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"[错误] 文件夹不存在: {folder_path}")
        return False
    
    if not folder_path.is_dir():
        print(f"[错误] 不是文件夹: {folder_path}")
        return False
    
    # 检查是否有index.html
    index_html = folder_path / 'index.html'
    if not index_html.exists():
        print(f"[警告] 文件夹中没有 index.html 文件")
    
    # 确定输出文件名
    if output_name is None:
        output_name = folder_path.name + '.zip'
    else:
        if not output_name.endswith('.zip'):
            output_name += '.zip'
    
    output_path = folder_path.parent / output_name
    
    # 创建ZIP压缩包
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(folder_path)
                    zf.write(file_path, arcname)
        
        print(f"[成功] 已创建压缩包: {output_path}")
        print(f"[信息] 文件大小: {output_path.stat().st_size / 1024:.1f} KB")
        return str(output_path)
    
    except Exception as e:
        print(f"[错误] 创建压缩包失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 package_zip.py <html文件路径> [输出文件名]")
        print("  python3 package_zip.py --folder <文件夹路径> [输出文件名]")
        print("")
        print("示例:")
        print("  python3 package_zip.py summary.html")
        print("  python3 package_zip.py summary.html 门店收银培训")
        print("  python3 package_zip.py --folder ./training-output")
        sys.exit(1)
    
    if sys.argv[1] == '--folder':
        if len(sys.argv) < 3:
            print("[错误] 请指定文件夹路径")
            sys.exit(1)
        folder_path = sys.argv[2]
        output_name = sys.argv[3] if len(sys.argv) > 3 else None
        package_folder(folder_path, output_name)
    else:
        html_path = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else None
        package_html(html_path, output_name)
