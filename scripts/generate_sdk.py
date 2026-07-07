#!/usr/bin/env python3
"""
OpenAPI SDK Generation Script

This script generates Python SDK code from the CODING OpenAPI specification.
使用说明:
    python scripts/generate_sdk.py

前置要求:
    pip install openapi-generator-cli
    或
    brew install openapi-generator (macOS)
"""

import subprocess
import sys
import os
from pathlib import Path


def generate_sdk():
    """Generate SDK from OpenAPI specification"""
    
    project_root = Path(__file__).parent.parent
    openapi_file = project_root / "docs" / "openapi_ref" / "document.yaml"
    output_dir = project_root
    
    if not openapi_file.exists():
        print(f"❌ OpenAPI 文件不存在: {openapi_file}")
        sys.exit(1)
    
    print(f"📋 OpenAPI 文件: {openapi_file}")
    print(f"📁 输出目录: {output_dir}")
    
    # OpenAPI Generator 命令
    cmd = [
        "openapi-generator-cli",
        "generate",
        "-g", "python",
        "-i", str(openapi_file),
        "-o", str(output_dir),
        "-c", str(project_root / "openapi-generator-config.yaml"),
    ]
    
    print(f"\n🚀 执行命令:\n{' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ SDK 生成成功！")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ SDK 生成失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ openapi-generator-cli 未找到")
        print("\n请先安装 openapi-generator:")
        print("  npm install @openapitools/openapi-generator-cli -g")
        print("  或")
        print("  brew install openapi-generator (macOS)")
        sys.exit(1)


if __name__ == "__main__":
    generate_sdk()
