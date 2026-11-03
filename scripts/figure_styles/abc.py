"""从项目数据重建最终展示样式。"""
def run():
    from pathlib import Path
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(__file__).resolve().parents[2]
    d=pd.read_csv(root/'outputs/tables/abc_roles.csv')
    g=d.groupby('ABC').agg(roles=('岗位','size'),exits=('exits','sum')).reindex(['A','B','C'])
    vals=np.column_stack([100*g.roles/len(d),100*g.exits/d.exits.sum()]).ravel()
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':11})
    fig,ax=plt.subplots(figsize=(9.2,3.9),dpi=300)
    fig.subplots_adjust(left=.1,right=.98,top=.85,bottom=.26)
    colors=['#68C6EF','#8DD8CD','#F2BC8D'];bgs=['#24364F','#223B49','#34364B']
    for j,(color,bg) in enumerate(zip(colors,bgs)):
     ax.axvspan(2*j-.5,2*j+1.5,color=bg,zorder=0)
     for i in [2*j,2*j+1]:
      v=vals[i]
      ax.vlines(i,0,v,color=color,linewidth=1.35,alpha=.85,zorder=2)
      ax.scatter(i,v,s=115,facecolor='#1A1E43',edgecolor=color,linewidth=1.2,alpha=.90,zorder=3)
      ax.scatter(i,v,s=55,facecolor=color,edgecolor='none',alpha=.95,zorder=4)
      ax.text(i,v+4.2,f'{v:.1f}%',ha='center',va='bottom',fontsize=11,fontweight='bold',color='#202020')
    ax.set_ylim(0,100);ax.set_xlim(-.5,5.5);ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('占比（%）',fontsize=13,fontweight='bold')
    ax.set_xticks(range(6));ax.set_xticklabels([f'{c}类·{kind}' for c in ['A','B','C'] for kind in ['岗位数','离职案例']],rotation=25,ha='right',rotation_mode='anchor',fontsize=11)
    ax.set_title('ABC岗位数量与离职案例贡献',fontsize=15,fontweight='bold',pad=18)
    for spine in ax.spines.values():spine.set_linewidth(1.1);spine.set_color('#303030')
    ax.tick_params(width=1,length=4,color='#303030');ax.grid(False)
    out=root/'outputs/figures/fig12_ABC结构对照.png';fig.savefig(out,dpi=300,facecolor='white');plt.close(fig)
