"""从项目数据重建最终展示样式。"""
def run():
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter
    root=Path(__file__).resolve().parents[2]
    d=pd.read_csv(root/'data/clean/employees.csv')
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':11})
    fig,ax=plt.subplots(figsize=(7.8,5.25),dpi=300)
    fig.subplots_adjust(left=.16,right=.97,top=.87,bottom=.19)
    rng=np.random.default_rng(2026)
    centers=[.75,2.3];colors=['#7EABEB','#8BD7C5'];markers=['o','s'];groups=[]
    for j,(center,color,marker) in enumerate(zip(centers,colors,markers)):
     values=d.loc[d.Exited.eq(j),'MonthlyIncome'].to_numpy();groups.append(values)
     # 散点每组固定种子随机抽取100条；箱线与密度仍使用全部观测。
     shown=rng.choice(values,size=min(100,len(values)),replace=False)
     xx=center-.38+rng.uniform(-.16,.10,len(shown))
     ax.scatter(xx,shown,s=22,marker=marker,facecolor=color,edgecolor=color,linewidth=.6,alpha=.50,zorder=2)
     b=ax.boxplot([values],positions=[center],widths=.18,patch_artist=True,showfliers=False,whis=1.5,manage_ticks=False,
      boxprops={'facecolor':'white','edgecolor':color,'linewidth':1.6},medianprops={'color':color,'linewidth':1.8},whiskerprops={'color':color,'linewidth':1.4},capprops={'color':color,'linewidth':1.4})
     # KDE截于样本最小、最大值；保留右半侧小提琴。
     vp=ax.violinplot([values],positions=[center+.18],widths=.83,showmeans=False,showmedians=False,showextrema=False,points=240,bw_method='scott')
     for body in vp['bodies']:
      verts=body.get_paths()[0].vertices;verts[:,0]=np.maximum(verts[:,0],center+.18)
      body.set_facecolor(color);body.set_edgecolor(color);body.set_alpha(.27);body.set_linewidth(1.3)
    ax.set(xlim=(-.02,3.08),ylim=(0,22000),yticks=[0,5000,10000,15000,20000],xticks=centers,
     xticklabels=[f'留任标签\n（n={len(groups[0]):,}）',f'离职标签\n（n={len(groups[1]):,}）'])
    ax.set_title('月收入分布与离职标签',fontsize=16,fontweight='bold',pad=17)
    ax.set_ylabel('月收入（原始数值单位）',fontsize=12,fontweight='bold',labelpad=12)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y',linestyle='--',color='#B9BCC3',linewidth=.8,alpha=.7);ax.set_axisbelow(True)
    for sp in ax.spines.values():sp.set_color('#252525');sp.set_linewidth(1.1)
    ax.tick_params(axis='y',direction='in',length=6,width=1);ax.tick_params(axis='x',length=5,width=1,labelsize=12)
    fig.text(.16,.035,'散点：每组随机展示100条（种子2026）  箱线与半小提琴：使用全部样本',fontsize=9,color='#555555')
    fig.savefig(root/'outputs/figures/fig23_收入箱线分布.png',dpi=300,facecolor='white');plt.close(fig)
