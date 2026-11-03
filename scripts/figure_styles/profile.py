"""从项目数据重建最终展示样式。"""
def run():
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, SymLogNorm
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.cm import ScalarMappable
    
    root=Path(__file__).resolve().parents[2]
    target=root/'outputs/figures/fig15_分群画像.png'
    d=pd.read_csv(root/'data/clean/employees.csv')
    cp=pd.read_csv(root/'outputs/tables/cluster_profile.csv').set_index('分群')
    z=(cp-d[cp.columns].mean())/d[cp.columns].std(ddof=0)
    assert z.shape==(2,7) and np.isfinite(z.to_numpy()).all()
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':11})
    cmap=LinearSegmentedColormap.from_list('blue_apricot',[(0,'#264B6B'),(.23,'#699DCA'),(.37,'#9AB3CE'),(.47,'#ACD1E6'),(.5,'#FAF8F3'),(.60,'#EAD0A9'),(.78,'#EBB690'),(1,'#EFA268')])
    norm=SymLogNorm(linthresh=.01,linscale=1,vmin=-2,vmax=2,base=10)
    fig=plt.figure(figsize=(7.8,4.0),dpi=300)
    ax=fig.add_axes([.085,.20,.79,.60])
    for i in range(2):
     for j in range(7):
      value=z.iloc[i,j]
      rgba=cmap(norm(value))
      ax.add_patch(FancyBboxPatch((j+.035,i+.035),.93,.93,boxstyle='round,pad=0,rounding_size=.17',facecolor=rgba,edgecolor='none',linewidth=0))
      lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
      ax.text(j+.5,i+.5,f'{value:+.3f}',ha='center',va='center',fontsize=10,color='white' if lum<.53 else '#253B4C')
    ax.set(xlim=(0,7),ylim=(2,0),xticks=np.arange(7)+.5,yticks=[.5,1.5],xticklabels=['月收入','总工龄','司龄','职级','培训次数','满意度','工作生活平衡'],yticklabels=z.index)
    ax.set_xticklabels(['月收入','总工龄','司龄','职级','培训次数','满意度','工作生活\n平衡'])
    ax.tick_params(length=0,pad=10,labelcolor='#344B60',labelsize=10)
    for s in ax.spines.values(): s.set_color('#DFE7ED')
    fig.text(.085,.90,'员工分群画像的标准化均值',fontsize=16,fontweight='bold',color='#264B6B')
    cax=fig.add_axes([.90,.20,.018,.60])
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,ticks=[-2,-.5,-.05,0,.05,.5,2])
    cb.ax.set_yticklabels(['−2','−0.5','−0.05','0','0.05','0.5','2'])
    cb.ax.tick_params(labelsize=8,length=2,color='#9AB3CE')
    cb.outline.set_visible(False)
    fig.savefig(target,dpi=300,facecolor='white')
    plt.close(fig)
