"""从项目数据重建最终展示样式。"""
def run():
    from pathlib import Path
    import json
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.patches import Wedge, Rectangle
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    from matplotlib.cm import ScalarMappable
    root=Path(__file__).resolve().parents[2]
    out=root/'outputs/figures'
    names=['fig11_ABC累计贡献.png','fig13_群数选择.png','fig19_混淆矩阵.png']
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':10})
    blue='#60C9EE'
    def base(title,ylabel):
     f,a=plt.subplots(figsize=(8.2,4.8),dpi=300)
     f.subplots_adjust(left=.12,right=.96,top=.84,bottom=.20)
     a.set_title(title,loc='left',pad=20,fontsize=16,fontweight='bold',color='#264B6B')
     a.set_ylabel(ylabel);a.spines[['top','right']].set_visible(False)
     a.spines[['left','bottom']].set_color('#BCCBD6')
     a.grid(axis='y',color='#DBE4EC',lw=.7);a.set_axisbelow(True)
     return f,a
    abc=pd.read_csv(root/'outputs/tables/abc_roles.csv');x=np.arange(len(abc));y=abc['cum'].to_numpy()*100
    f,a=base('四个重点岗位覆盖83.97%的离职案例','累计离职案例占比 / %')
    a.plot(x,y,'o-',color=blue,lw=2,ms=5,zorder=3)
    a.axhline(80,color='#C28A32',ls='--',lw=1.2,label='80%参考线',zorder=2)
    labels=[s[:2]+'\n'+s[2:] if len(s)>3 else s for s in abc['岗位']]
    a.set(xticks=x,xticklabels=labels,ylim=(0,113),xlim=(-.15,8.15))
    a.annotate('A类覆盖 83.97%',xy=(3,y[3]),xytext=(1.7,105),color='#936423',arrowprops={'arrowstyle':'->','color':'#B47A00'},fontsize=10)
    a.legend(loc='lower right',frameon=False)
    f.savefig(out/names[0],dpi=300);plt.close(f)
    
    ks=pd.read_csv(root/'outputs/tables/cluster_selection.csv')
    f,a=base('K-Means群数的轮廓系数比较','平均轮廓系数')
    a.plot(ks.k,ks.silhouette,color=blue,lw=1.8,zorder=2)
    # Per-pixel sphere lighting; marker centers remain at the exact observed values.
    t=np.linspace(-1,1,100);xx,yy=np.meshgrid(t,t);rr=xx**2+yy**2;zz=np.sqrt(np.maximum(0,1-rr))
    light=np.clip(-.45*xx-.55*yy+.7*zz,0,1)
    rgb=np.array([.376,.788,.933]);sphere=np.zeros((100,100,4))
    sphere[:,:,:3]=np.clip(rgb[None,None,:]*(.60+.40*light[:,:,None])+.40*light[:,:,None]**18,0,1)
    sphere[:,:,3]=(rr<=1).astype(float)
    for k,v in zip(ks.k,ks.silhouette):
     a.add_artist(AnnotationBbox(OffsetImage(sphere,zoom=.10), (k,v),frameon=False,zorder=4))
     a.annotate(f'{v:.3f}',(k,v),xytext=(0,15),textcoords='offset points',ha='center',color='#264B6B',fontsize=10)
    a.set(xticks=ks.k,xlabel='候选群数 K',ylim=(0,.46),xlim=(1.75,6.25))
    f.savefig(out/names[1],dpi=300);plt.close(f)
    
    m=json.loads((root/'outputs/tables/metrics.json').read_text(encoding='utf-8'))
    cm=np.array(m['confusion']);tn,fp,fn,tp=cm.ravel()
    f=plt.figure(figsize=(7.8,7),dpi=300);a=f.add_axes([.14,.16,.66,.70]);a.set_aspect('equal')
    a.set(xlim=(-.23,2),ylim=(0,2.23));a.axis('off')
    cmap=LinearSegmentedColormap.from_list('night_blues',['#36577B','#4D91BD','#7BD5EF']);norm=Normalize(0,int(cm.max()))
    # Sector area is proportional to count; reordered positive-first layout.
    for value,ang in [(tp,90),(fn,0),(fp,180),(tn,270)]:
     a.add_patch(Wedge((1,1),.95*np.sqrt(value/cm.max()),ang,ang+90,facecolor=cmap(norm(value)),edgecolor='none'))
    for j,label in enumerate(['预测离职（正类）','预测留任（负类）']):
     a.add_patch(Rectangle((j,2),1,.22,facecolor='#EFF4F8',edgecolor='#264B6B',lw=1.4))
     a.text(j+.5,2.11,label,ha='center',va='center',fontsize=10)
    for yy,label in [(1,'实际离职'),(0,'实际留任')]:
     a.add_patch(Rectangle((-.22,yy),.22,1,facecolor='#EFF4F8',edgecolor='#264B6B',lw=1.4))
     a.text(-.11,yy+.5,label,ha='center',va='center',rotation=90,fontsize=11)
    for pos in [0,1,2]:
     a.plot([pos,pos],[0,2],color='#264B6B',lw=1.5)
     a.plot([0,2],[pos,pos],color='#264B6B',lw=1.5)
    cells=[(.25,1.80,'TP',tp,tp/(tp+fn)),(1.75,1.80,'FN',fn,fn/(tp+fn)),(.25,.20,'FP',fp,fp/(fp+tn)),(1.75,.20,'TN',tn,tn/(fp+tn))]
    for xx,yy,tag,n,pct in cells:
     a.text(xx,yy,f'{tag}\n{pct:.1%}',ha='center',va='center',fontsize=13,color='#152E42')
    for xx,yy,n in [(.78,1.15,tp),(1.15,1.15,fn),(.78,.82,fp),(1.20,.78,tn)]:
     a.text(xx,yy,str(n),ha='center',va='center',fontsize=17,color='white' if n>cm.max()*.65 else '#152E42',fontweight='bold')
    cax=f.add_axes([.85,.22,.025,.57]);cb=f.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax);cb.set_label('样本数 / 人');cb.outline.set_visible(False)
    f.text(.14,.93,'独立测试集混淆矩阵',fontsize=17,fontweight='bold',color='#264B6B')


    from matplotlib.transforms import Bbox
    f.savefig(out/names[2],dpi=300,bbox_inches=Bbox.from_bounds(0,254/300,7.8,1846/300));plt.close(f)
