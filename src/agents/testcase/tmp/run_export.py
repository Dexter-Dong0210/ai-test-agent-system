#!/usr/bin/env python3
import subprocess
import sys
import os

# 执行Python环境检查
print("=== Python Environment Check ===")
check_result = subprocess.run([sys.executable, "/tmp/check_python.py"], 
                             capture_output=True, text=True)
print(check_result.stdout)
if check_result.stderr:
    print("Stderr:", check_result.stderr)

print("\n=== Running Export Script ===")
# 执行导出脚本
cmd = [
    sys.executable,
    "/skills/test-case-excel-export/scripts/export_to_excel.py",
    "/test_login/test_cases_complete.json",
    "/test_login/06_test_cases.xlsx"
]

print(f"Command: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

print("Stdout:", result.stdout)
print("Stderr:", result.stderr)
print("Return code:", result.returncode)

# 检查输出文件是否存在
if os.path.exists("/test_login/06_test_cases.xlsx"):
    print(f"\n✓ Excel file created: /test_login/06_test_cases.xlsx")
    file_size = os.path.getsize("/test_login/06_test_cases.xlsx")
    print(f"  File size: {file_size} bytes")
else:
    print(f"\n✗ Excel file NOT created: /test_login/06_test_cases.xlsx")