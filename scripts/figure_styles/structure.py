"""从项目数据重建最终展示样式。"""
def run():
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Patch
    from matplotlib.offsetbox import OffsetImage,AnnotationBbox
    from matplotlib.colors import to_rgb
    root=Path(__file__).resolve().parents[2];out=root/'outputs/figures'
    targets={1:'fig01_渐变柱形图.png',2:'fig02_带均值柱形图.png',4:'fig04_标注柱形图.png',5:'fig05_层叠柱形图.png'}
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':11})
    BG='#1A1E43';BLUE='#F3F7FF';MID='#52B9EC';LIGHT='#83C8ED';ORANGE='#F3AD71'
    plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':BG,'text.color':BLUE,'axes.labelcolor':'#DEE8F7','xtick.color':'#D6E2F2','ytick.color':'#EAF1FB','legend.labelcolor':BLUE})
    def ball(a,x,y,color,zoom=.105):
     t=np.linspace(-1,1,96);xx,yy=np.meshgrid(t,t);rr=xx*xx+yy*yy;zz=np.sqrt(np.maximum(0,1-rr))
     light=np.clip(-.38*xx-.48*yy+.79*zz,0,1)
     img=np.zeros((96,96,4));rgb=np.array(to_rgb(color))
     img[:,:,:3]=np.clip(rgb*(.50+.50*light[:,:,None])+.36*light[:,:,None]**22,0,1);img[:,:,3]=(rr<=1)
     a.add_artist(AnnotationBbox(OffsetImage(img,zoom=zoom),(x,y),frameon=False,zorder=6))
    r=pd.read_csv(root/'outputs/tables/roles.csv');top=r.sort_values('n',ascending=False).head(6).reset_index(drop=True)
    def base(title,xlabel):
     f,a=plt.subplots(figsize=(8,4.8),dpi=300);f.subplots_adjust(left=.20,right=.94,top=.83,bottom=.20)
     a.set_title(title,loc='left',pad=22,fontsize=16,fontweight='bold',color=BLUE)
     a.set_xlabel(xlabel,labelpad=10);a.spines[['top','right','left']].set_visible(False);a.spines['bottom'].set_color('#677494')
     a.tick_params(axis='y',length=0,pad=12);a.grid(axis='x',color='#45516F',lw=.7,alpha=.55);a.set_axisbelow(True)
     return f,a
    def save(f,k):f.savefig(out/targets[k],dpi=300,facecolor=BG);plt.close(f)
    y=np.arange(6)
    f,a=base('主要岗位规模与六岗位均值','员工数 / 人');mean=top.n.mean()
    a.axvline(mean,color='#7D8BA9',ls='--',lw=1,zorder=1)
    for i,n in enumerate(top.n):
     a.plot([n,mean],[i,i],color='#7A9DB5',lw=3,zorder=2)
     a.text(n+(8 if n>=mean else -8),i,f'{n}',ha='left' if n>=mean else 'right',va='center',color=BLUE)
    a.scatter(np.repeat(mean,6),y,s=90,color=ORANGE,edgecolor='white',zorder=3,label=f'六岗位均值 {mean:.1f}')
    a.scatter(top.n,y,s=90,color=MID,edgecolor='white',zorder=4,label='该岗位人数')
    a.set(yticks=y,yticklabels=top['岗位'],xlim=(60,top.n.max()*1.15),ylim=(5.6,-.6))
    f.legend(*a.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.57,.005),ncol=2,frameon=False,fontsize=10)
    save(f,2)
    rr=r.sort_values('rate',ascending=False).head(6).reset_index(drop=True)
    f,a=base('离职标签比例较高的岗位','离职标签占比 / %')
    a.errorbar(rr.rate*100,y,xerr=[(rr.rate-rr.low)*100,(rr.high-rr.rate)*100],fmt='none',ecolor=LIGHT,elinewidth=2,capsize=4)
    a.scatter(rr.rate*100,y,s=90,color=MID,edgecolor='white',linewidth=.8,zorder=4)
    for i,row in rr.iterrows():a.text(row.high*100+1,i,f'{row.rate:.1%}  (n={row.n})',va='center',fontsize=10,color=BLUE)
    a.set(yticks=y,yticklabels=rr['岗位'],xlim=(0,rr.high.max()*100+19),ylim=(5.6,-.6))
    f.text(.20,.045,'点：样本比例；横线：95% Wilson区间。描述性比较，不代表因果影响。',fontsize=9,color='#B7C7DC');save(f,4)
    dep=pd.read_csv(root/'outputs/tables/departments.csv')
    f,axes=plt.subplots(1,len(dep),figsize=(9,4.8),dpi=300);f.subplots_adjust(left=.035,right=.98,top=.73,bottom=.23,wspace=.25)
    f.text(.04,.90,'各部门离职与留任标签构成',fontsize=17,fontweight='bold',color=BLUE)
    for a,(_,row) in zip(axes,dep.iterrows()):
     a.set(xlim=(0,10),ylim=(0,10),aspect='equal');a.axis('off');units=100*row.exits/row.n
     for k in range(100):
      x=k%10;y0=k//10
      a.add_patch(Rectangle((x+.11,y0+.025),.86,.86,facecolor='#0F122B',edgecolor='none',zorder=1))
      a.add_patch(Rectangle((x+.07,y0+.07),.86,.86,facecolor=LIGHT,edgecolor='none',zorder=2))
      fraction=np.clip(units-k,0,1)
      if fraction>0:a.add_patch(Rectangle((x+.07,y0+.07),.86*fraction,.86,facecolor=ORANGE,edgecolor='none',zorder=3))
      a.plot([x+.09,x+.91],[y0+.90,y0+.90],color='white',alpha=.38,lw=.65,zorder=4)
      a.plot([x+.90,x+.90],[y0+.09,y0+.88],color='#182C48',alpha=.25,lw=.7,zorder=4)
     a.set_title(f'{row["部门"]}  |  n={row.n:,}',fontsize=12,color=BLUE,pad=14)
     a.text(.5,-.10,f'离职 {row.exits}人 · {row.rate:.1%}',transform=a.transAxes,ha='center',fontsize=11,color=BLUE)
     a.text(.5,-.20,f'留任 {row.n-row.exits}人 · {1-row.rate:.1%}',transform=a.transAxes,ha='center',fontsize=10,color='#B7C7DC')
    f.legend(handles=[Patch(color=ORANGE,label='离职标签'),Patch(color=LIGHT,label='留任标签')],loc='lower center',bbox_to_anchor=(.5,.055),ncol=2,frameon=False)
    f.text(.5,.025,'每格代表部门内样本的1%；不足1%的部分用局部填充，部门人数以标注为准。',ha='center',fontsize=9,color='#B7C7DC')
    save(f,5)
