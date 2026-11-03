"""打开可离线交互的HTML，不启动服务器。"""
from pathlib import Path
import webbrowser,subprocess,sys
root=Path(__file__).resolve().parent
page=root/'outputs/dashboard/员工离职管理驾驶舱.html'
if not page.exists():subprocess.run([sys.executable,str(root/'scripts/dashboard.py')],check=True)
webbrowser.open(page.as_uri())
