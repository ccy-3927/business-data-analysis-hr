def run():
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/figures'
    TARGET={15,16,21,22,24};BG='#1A1E43';FG='#EEF4FF';BLUE='#69C7EF';ORANGE='#F2B581'
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':11,'figure.facecolor':BG,'axes.facecolor':BG,'text.color':FG,'axes.labelcolor':FG,'xtick.color':'#CDDAEE','ytick.color':FG})
    def base(title,left=.14,bottom=.19):
     f,a=plt.subplots(figsize=(8.1,4.8),dpi=300);f.subplots_adjust(left=left,right=.94,top=.82,bottom=bottom)
     a.set_title(title,loc='left',fontsize=16,fontweight='bold',pad=22)
     a.spines[['top','right']].set_visible(False)
     for s in a.spines.values():s.set_color('#657694')
     a.set_axisbelow(True)
     return f,a
    def save(f,n):
     p=OUT/{16:'fig16_分群离职差异.png',21:'fig21_置换重要性.png',22:'fig22_加班关联区间.png',24:'fig24_群体误差诊断.png'}[n];f.savefig(p,dpi=300,facecolor=BG);plt.close(f)
    def grad(a,x0,x1,y0,y1,colors,horizontal=False):
     arr=np.linspace(0,1,256)[None,:] if horizontal else np.linspace(0,1,256)[:,None]
     a.imshow(arr,extent=[x0,x1,y0,y1],origin='lower',aspect='auto',cmap=LinearSegmentedColormap.from_list('bar',colors),zorder=2)
     if horizontal:a.plot([x0,x1],[y1,y1],color=colors[-1],lw=.6,alpha=.7,zorder=3)
     else:a.plot([x0,x1],[y1,y1],color='#E7F5FF',lw=.7,alpha=.5,zorder=3)
    co=pd.read_csv(ROOT/'outputs/tables/cluster_outcomes.csv')
    f,a=base('不同职业阶段群体的离职标签差异',left=.20,bottom=.22)
    f.subplots_adjust(right=.70)
    for i,r in co.iterrows():
     c=[BLUE,ORANGE][i];lo,hi,v=r.low*100,r.high*100,r.rate*100
     a.axhspan(i-.26,i+.26,color='#242D4C',zorder=0)
     a.plot([lo,hi],[i,i],color=c,lw=7,solid_capstyle='round',alpha=.4)
     a.plot([lo,hi],[i,i],color=c,lw=2)
     a.scatter(v,i,s=105,color=c,edgecolor='none',lw=0,zorder=3)
     a.text(1.06,i,f'{v:.2f}%\n[{lo:.2f}, {hi:.2f}]',transform=a.get_yaxis_transform(),va='center',ha='left',color=FG,fontsize=11,linespacing=1.6)
    a.set(xlim=(0,26),ylim=(1.65,-.65),xticks=[0,5,10,15,20,25],yticks=[0,1],yticklabels=[f'{r["分群"]}\nn={r.n:,}' for _,r in co.iterrows()],xlabel='离职标签占比 / %')
    a.grid(axis='x',color='#54617E',alpha=.3);a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0,pad=12)
    f.text(.20,.06,'圆点为样本比例，横线与方括号为95% Wilson区间。',fontsize=9,color='#BECCE0');save(f,16)
    ot=pd.read_csv(ROOT/'outputs/tables/overtime.csv');f,a=base('加班标签与离职标签的关联')
    rates=ot.rate.to_numpy()*100
    a.plot(rates,[0,0],color='#7182A0',lw=3,zorder=1)
    for i,r in ot.iterrows():
     c=[BLUE,ORANGE][i];v=r.rate*100
     a.plot([r.low*100,r.high*100],[0,0],color=c,lw=10,alpha=.35,solid_capstyle='round',zorder=2)
     a.scatter(v,0,s=150,color=c,edgecolor='none',zorder=4)
     a.text(v,.20,f'{r["加班"]}\n{v:.2f}%',ha='center',va='bottom',fontsize=14,fontweight='bold',color=c,linespacing=1.6)
     a.text(v,-.22,f'n={r.n:,} · 离职 {r.exits}人\n95%区间 [{r.low*100:.2f}%, {r.high*100:.2f}%]',ha='center',va='top',fontsize=10,color='#CDDAEE',linespacing=1.7)
    a.text(.5,.96,f'两组相差 {rates[1]-rates[0]:.2f} 个百分点',transform=a.transAxes,ha='center',va='top',fontsize=12,color=FG)
    a.set(xlim=(0,42),ylim=(-.65,.85),yticks=[],xlabel='离职标签占比 / %')
    a.spines['left'].set_visible(False);a.grid(axis='x',color='#54617E',alpha=.3)
    f.text(.14,.035,'圆点：样本比例；加粗短线：95% Wilson区间。横截面关联不代表因果关系。',fontsize=9,color='#BECCE0');save(f,22)
    imp=pd.read_csv(ROOT/'outputs/tables/permutation_importance.csv').head(8).iloc[::-1]
    labels={'OverTime':'加班','JobLevel':'职级','StockOptionLevel':'股票期权等级','JobInvolvement':'工作投入','YearsWithCurrManager':'现经理共事年数','EnvironmentSatisfaction':'环境满意度','TotalWorkingYears':'总工龄','NumCompaniesWorked':'曾任职公司数'}
    f,a=base('特征置换后AP的平均下降',left=.23,bottom=.20)
    for i,(_,r) in enumerate(imp.iterrows()):
     grad(a,0,r.AP_drop,i-.29,i+.29,['#286A9A','#6ACBF0'],True)
     a.errorbar(r.AP_drop,i,xerr=r['std'],fmt='none',ecolor='#D4E5F4',capsize=3,elinewidth=1,zorder=4)
     a.text(r.AP_drop+r['std']+.004,i,f'{r.AP_drop:.3f}',va='center',fontsize=9)
    a.set(yticks=np.arange(8),yticklabels=[labels.get(v,v) for v in imp.feature],ylim=(-.65,7.7),xlim=(0,.285),xlabel='测试集AP下降（15次置换的均值）')
    a.grid(axis='x',color='#54617E',alpha=.3);a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
    f.text(.23,.04,'误差棒为15次置换的标准差；重要性不等于因果效应。',fontsize=9,color='#BECCE0');save(f,21)
    fair=pd.read_csv(ROOT/'outputs/tables/group_diagnostics.csv');f,a=base('测试集性别分组的模型误差诊断')
    for i,r in fair.iterrows():
     for offset,value,colors in [(-.19,r.recall*100,['#286A9A',BLUE]),(.19,r.FPR*100,['#9C664E',ORANGE])]:
      x=i+offset;grad(a,x-.15,x+.15,0,value,colors)
      a.text(x,value+2,f'{value:.1f}%',ha='center',fontsize=11,color=colors[-1])
    a.set(xlim=(-.6,1.6),ylim=(0,103),xticks=[0,1],xticklabels=[f'{r.Gender}\nn={r.n}，正类={r.positives}' for _,r in fair.iterrows()],ylabel='比例 / %')
    a.grid(axis='y',color='#54617E',alpha=.3)
    a.legend(handles=[Patch(color=BLUE,label='召回率'),Patch(color=ORANGE,label='假正率')],loc='upper right',frameon=False,ncol=2,fontsize=10)
    f.text(.14,.03,'性别未输入模型；分组结果仅用于误差诊断。',fontsize=9,color='#BECCE0');save(f,24)
