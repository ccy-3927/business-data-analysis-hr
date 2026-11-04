"""生成无需第三方浏览器脚本的离线交互大屏，预置SVG首屏。"""
from pathlib import Path
import json
from html import escape
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
d=pd.read_csv(ROOT/'data/clean/employees.csv')
fields=['部门','岗位','加班','分群','YearsAtCompany','MonthlyIncome','JobSatisfaction','Exited']
BLUE='#59BCEB';PEACH='#F0AD7C'
def text(x,y,label,anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" fill="#C9D9ED">{escape(str(label))}</text>'
def svg(body):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 230" role="img" preserveAspectRatio="none">'+body+'</svg>'
def grouped(field):
    g=d.groupby(field).Exited.agg(n='size',exits='sum').reset_index()
    g['rate']=100*g.exits/g.n
    return g

def bars(g,field,stack=False):
    maximum=max(g.n) if stack else max(10,max(g.rate))
    maximum=((maximum+9)//10)*10
    b=''
    for i in range(5):
        y=192-i*178/4
        b+=f'<path d="M46 {y}H590" stroke="#3E4A6B"/>'+text(39,y+4,round(maximum*i/4,1),'end')
    for i,(_,r) in enumerate(g.iterrows()):
        step=538/len(g);x=46+step*(i+.5);w=min(step*.56,66)
        if stack:
            h=178*(r.n-r.exits)/maximum;hh=178*r.exits/maximum
            b+=f'<rect x="{x-w/2}" y="{192-h}" width="{w}" height="{h}" fill="{BLUE}"/><rect x="{x-w/2}" y="{192-h-hh}" width="{w}" height="{hh}" fill="{PEACH}"/>'
        else:
            h=178*r.rate/maximum
            b+=f'<rect x="{x-w/2}" y="{192-h}" width="{w}" height="{h}" rx="3" fill="{BLUE}"/>'+text(x,187-h,f'{r.rate:.1f}%')
        b+=text(x,214,r[field])
    return svg(b)
def scatter():
    b=''
    for i in range(5):
        y=190-168*i/4
        b+=f'<path d="M60 {y}H584" stroke="#3E4A6B"/>'+text(53,y+4,i*5000,'end')+text(60+524*i/4,213,i*10)
    for r in d.itertuples():
        b+=f'<circle cx="{60+524*r.YearsAtCompany/40}" cy="{190-168*r.MonthlyIncome/20000}" r="2.5" fill="{PEACH if r.Exited else BLUE}" fill-opacity=".48"/>'
    return svg(b)
values=[('筛选样本',f'{len(d):,} 人'),('离职标签',f'{d.Exited.sum():,} 人'),('离职标签占比',f'{d.Exited.mean():.2%}'),('月收入中位数',f'{d.MonthlyIncome.median():,.0f}')]
cards=''.join(f'<div class="kpi"><small>{k}</small><b>{v}</b></div>' for k,v in values)
g=d.groupby(['部门','岗位']).Exited.agg(n='size',exits='sum').reset_index()
table=''.join(f'<tr><td>{escape(r.部门)}</td><td>{escape(r.岗位)}</td><td>{r.n}</td><td>{r.exits}</td><td>{100*r.exits/r.n:.1f}%</td></tr>' for r in g.itertuples())
options=lambda col:''.join(f'<option>{escape(v)}</option>' for v in ['全部']+sorted(d[col].unique()))
replacements={'__DATA__':d[fields].to_json(orient='records',force_ascii=False).replace('</','<\\/'),'__DEPARTMENTS__':options('部门'),'__CLUSTERS__':options('分群'),'__KPIS__':cards,'__ROLES__':bars(grouped('岗位').sort_values('rate',ascending=False),'岗位'),'__DEPT_CHART__':bars(grouped('部门'),'部门',True),'__SAT__':bars(grouped('JobSatisfaction'),'JobSatisfaction'),'__SCATTER__':scatter(),'__TABLE__':table}
html=(ROOT/'scripts/dashboard_template.html').read_text(encoding='utf-8')
for k,v in replacements.items():html=html.replace(k,v)
assert '__DATA__' not in html and html.split('<script')[0].count('<svg ')==4
out=ROOT/'outputs/dashboard/员工离职管理.html'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(html,encoding='utf-8')
print(out)
