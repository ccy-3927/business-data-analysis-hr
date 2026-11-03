"""在项目根目录执行 python run_all.py，重新计算全部结果和24张图。"""
import os,sys
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
from pipeline import run as analyze
from visuals import run as draw
analyze();draw()
import dashboard
print('分析与图表生成完成。论文需另运行 scripts/build_report.py。')
