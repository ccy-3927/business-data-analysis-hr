"""十种教材图形迁移及十四张模型/诊断图；不伪造时间轴。"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from sklearn.metrics import roc_curve,precision_recall_curve
from pipeline import ROOT,TABLE,FIG,CLEAN,CLUSTER_FEATURES
plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,'font.size':9.5,'axes.titlesize':12,'axes.labelsize':9.5,'savefig.dpi':220,'axes.prop_cycle':plt.cycler(color=['#0072B2','#D55E00','#009E73']),'legend.framealpha':.94,'legend.edgecolor':'#E2E8EF','axes.labelcolor':'#34465A','xtick.color':'#425367','ytick.color':'#425367'})
BG='#1A1E43';BLUE='#0070C0';CYAN='#00B0F0';PINK='#E74E69';GOLD='#FFC000'
INDEX=[]
def read(n):return pd.read_csv(TABLE/f'{n}.csv')
def canvas(title,unit='',dark=False):
    f,a=plt.subplots(figsize=(6.1,3.65),layout='constrained');a.set_title(title,loc='left',pad=13,fontweight='bold',color='white' if dark else '#111');a.set_ylabel(unit)
    if dark:
        f.set_facecolor(BG);a.set_facecolor(BG);a.tick_params(colors='white');a.title.set_color('white');a.xaxis.label.set_color('white');a.yaxis.label.set_color('white')
        for s in a.spines.values():s.set_color('#606780')
    else:
        f.set_facecolor('white');a.set_facecolor('#FBFCFE');a.spines[['top','right']].set_visible(False)
        a.spines['left'].set_color('#CDD6E0');a.spines['bottom'].set_color('#CDD6E0')
        a.grid(axis='y',color='#DCE4EC',lw=.65,alpha=.75);a.set_axisbelow(True);a.tick_params(length=3)
    return f,a
def finish(f,n,name,ref,note):
    filename=f'fig{n:02d}_{name}.png';f.savefig(FIG/filename,dpi=220,facecolor=f.get_facecolor());plt.close(f)
    INDEX.append({'编号':f'fig{n:02d}','文件':filename,'类别':'教材模板' if n<=10 else '业务模型','对应模板或模型':ref,'解读':note})
def leg(a):a.legend(facecolor=BG,labelcolor='white',fontsize=8)
def lab(a,b,dark=True,fmt='%.0f'):a.bar_label(b,fmt=fmt,color='white' if dark else '#222',padding=3,fontsize=8)
def _base_run():
    INDEX.clear();d=pd.read_csv(CLEAN/'employees.csv');r=read('roles').sort_values('n',ascending=False);m=json.loads((TABLE/'metrics.json').read_text(encoding='utf-8'));x=np.arange(6);top=r.head(6);v=top.n.to_numpy();names=top['岗位'].tolist()
    cmap=LinearSegmentedColormap.from_list('book',[BLUE,CYAN])
    f,a=canvas('主要岗位的员工规模','员工数 / 人',True)
    for i,y in enumerate(v):a.imshow(np.linspace(0,1,256).reshape(-1,1),extent=[i-.28,i+.28,0,y],origin='lower',aspect='auto',cmap=cmap);a.text(i,y+10,str(y),ha='center',color='white')
    a.set(xlim=(-.6,5.6),ylim=(0,v.max()*1.2),xticks=x,xticklabels=names);a.tick_params(axis='x',labelsize=8)
    finish(f,1,'渐变柱形图','前15：1 渐变柱形图','展示人数最多的六个岗位；未展示其余岗位不等于样本删除。')
    f,a=canvas('主要岗位规模与图内均值','员工数 / 人',True);lab(a,a.bar(x,v,color=BLUE,width=.55));a.axhline(v.mean(),ls='--',color=GOLD,label=f'六岗位均值 {v.mean():.1f}');a.set(xticks=x,xticklabels=names,ylim=(0,v.max()*1.35));a.tick_params(axis='x',labelsize=8);leg(a)
    finish(f,2,'带均值柱形图','前15：2 带均值柱形图','参考线仅代表图内六岗位，不是全体九岗位均值。')
    f,a=canvas('主要岗位规模的圆角展示','员工数 / 人',True)
    for i,y in enumerate(v):
        patch=FancyBboxPatch((i-.3,0),.6,y,boxstyle='round,pad=0,rounding_size=0.15',facecolor='none',edgecolor='none',mutation_aspect=60);a.add_patch(patch)
        im=a.imshow(np.linspace(0,1,256).reshape(-1,1),extent=[i-.3,i+.3,0,y],origin='lower',aspect='auto',cmap=cmap);im.set_clip_path(patch);a.text(i,y+10,str(y),color='white',ha='center')
    a.set(xlim=(-.6,5.6),ylim=(0,v.max()*1.2),xticks=x,xticklabels=names);a.tick_params(axis='x',labelsize=8)
    finish(f,3,'渐变圆角柱形图','前15：3 渐变圆角柱形图','保持深色底、渐变与圆角；精确数值以柱顶标签为准。')
    rr=r.sort_values('rate',ascending=False).head(6);vv=rr.rate.to_numpy()*100
    f,a=canvas('离职标签比例较高的岗位','离职标签占比 / %',True);lab(a,a.bar(x,vv,color=[GOLD]+[BLUE]*5),fmt='%.1f');a.set(xticks=x,xticklabels=rr['岗位'],ylim=(0,vv.max()*1.4));a.tick_params(axis='x',labelsize=8);a.text(.02,.94,'描述性比较，不代表岗位的因果影响',transform=a.transAxes,color='white',fontsize=8)
    finish(f,4,'标注柱形图','前15：4 标注柱形图','按比例排序；不把离职人数最多与比例最高混为一谈。')
    dep=read('departments');xx=np.arange(len(dep))
    f,a=canvas('各部门离职与留任标签构成','员工数 / 人',True);a.bar(xx,dep.n-dep.exits,color=BLUE,label='留任标签');a.bar(xx,dep.exits,bottom=dep.n-dep.exits,color=PINK,label='离职标签');a.set(xticks=xx,xticklabels=dep['部门'],ylim=(0,dep.n.max()*1.25));leg(a)
    finish(f,5,'层叠柱形图','前15：5 层叠柱形图','两种标签互斥且合计为部门样本数。')
    tab=pd.crosstab(d['岗位'],d.Gender).reindex(names).fillna(0)
    f,a=canvas('主要岗位的男女样本构成','',True);a.barh(x,-tab.Female,color=BLUE,label='女性');a.barh(x,tab.Male,color=PINK,label='男性');a.axvline(0,color='white',lw=.5);a.set(yticks=x,yticklabels=names,xlabel='员工数 / 人（镜像轴均为正数）');a.xaxis.set_major_formatter(FuncFormatter(lambda val,pos:f'{abs(val):.0f}'));leg(a)
    finish(f,6,'蝴蝶图','前15：6 蝴蝶图','性别仅用于样本结构及误差诊断，不进入分类模型。')
    f,a=canvas('部门内离职与留任标签占比','',True);a.barh(xx,100*(1-dep.rate),color=BLUE,label='留任');a.barh(xx,100*dep.rate,left=100*(1-dep.rate),color=PINK,label='离职')
    for i,row in dep.iterrows():a.text(50*(1-row.rate),i,f'{100*(1-row.rate):.1f}%',ha='center',va='center',color='white');a.text(100-50*row.rate,i,f'{100*row.rate:.1f}%',ha='center',va='center',color='white')
    a.set(yticks=xx,yticklabels=dep['部门'],xlim=(0,100),xlabel='部门内样本占比 / %')
    finish(f,7,'数值百分比图','前15：8 数值百分比','分母为各部门员工数，不是总体离职人数。')
    ot=pd.crosstab(d['岗位'],d['加班']).reindex(names)
    f,a=canvas('主要岗位的加班标签人数对比','员工数 / 人',True);lab(a,a.bar(x-.18,ot['不加班'],width=.36,color=BLUE,label='不加班'));lab(a,a.bar(x+.18,ot['加班'],width=.36,color='#82ADD7',label='加班'));a.set(xticks=x,xticklabels=names,ylim=(0,ot.max().max()*1.35));a.tick_params(axis='x',labelsize=8);leg(a)
    finish(f,8,'对比柱形图','前15：9 对比柱形图','加班为二元标签，不是每周工作时长。')
    sat=read('satisfaction');xx=np.arange(4);vv=sat.rate*100
    f,a=canvas('不同工作满意度的离职标签比例','离职标签占比 / %',True);a.vlines(xx,0,vv,color=PINK);a.scatter(xx,vv,marker='D',facecolor=BG,edgecolor=PINK,s=50)
    for i,y in enumerate(vv):a.text(i,y+1,f'{y:.1f}%',ha='center',color='white')
    a.set(xticks=xx,xticklabels=['1 低','2 中','3 高','4 很高'],ylim=(0,max(vv)*1.3),xlabel='工作满意度等级')
    finish(f,9,'菱形走势展示','前15：12 菱形走势图','横轴为有序等级，不是时间；不连接无序岗位类别。')
    f,a=canvas('离职与留任标签的总体构成','',True);a.pie([m['exits'],m['rows']-m['exits']],colors=[PINK,BLUE],startangle=90,wedgeprops={'width':.25,'edgecolor':BG});a.text(0,.05,f"{m['rate']:.1%}",ha='center',color='white',fontsize=25);a.text(0,-.23,'离职标签占比',ha='center',color='white');a.legend(['离职 237人','留任 1233人'],loc='lower right',facecolor=BG,labelcolor='white')
    finish(f,10,'单环图','前15：14 单环图','为教材复现保留两类单环；业务比较采用柱形图和区间。')
    abc=read('abc_roles');xx=np.arange(len(abc))
    f,a=canvas('四个重点岗位覆盖83.97%的离职案例','累计离职案例占比 / %');a.plot(xx,100*abc['cum'],'o-',color=BLUE,lw=2);a.fill_between(xx,0,100*abc['cum'],color=BLUE,alpha=.07);a.axhline(80,color='#D18A00',ls='--',label='80%参考线');a.set(xticks=xx,xticklabels=[s.replace('实验室技术员','实验室\n技术员').replace('研究科学家','研究\n科学家').replace('销售主管','销售\n主管').replace('销售代表','销售\n代表').replace('人力资源','人力\n资源').replace('制造总监','制造\n总监').replace('医疗代表','医疗\n代表').replace('研究总监','研究\n总监') for s in abc['岗位']],ylim=(0,113));a.tick_params(axis='x',labelsize=8);a.annotate('A类覆盖 83.97%',xy=(3,83.97),xytext=(1.7,104),color='#8A5A00',arrowprops={'arrowstyle':'->','color':'#B47A00'},fontsize=9);a.legend(loc='lower right');finish(f,11,'ABC累计贡献','ABC','岗位按离职人数排序；跨越阈值的岗位纳入前一类。')
    ag=abc.groupby('ABC').agg(roles=('岗位','size'),exits=('exits','sum')).reindex(['A','B','C'],fill_value=0)
    f,a=canvas('ABC岗位数量与案例贡献','占比 / %');xx=np.arange(3);lab(a,a.bar(xx-.18,100*ag.roles/len(abc),.36,color=BLUE,label='岗位数占比'),False,'%.1f');lab(a,a.bar(xx+.18,100*ag.exits/m['exits'],.36,color='#E69F00',label='离职案例占比'),False,'%.1f');a.set(xticks=xx,xticklabels=ag.index,ylim=(0,105));a.legend();finish(f,12,'ABC结构对照','ABC','只衡量已观察离职案例集中度，不评价个人价值。')
    ks=read('cluster_selection');f,a=canvas('K-Means群数的轮廓系数比较','平均轮廓系数');a.plot(ks.k,ks.silhouette,'o-',color=BLUE);a.set(xticks=ks.k,xlabel='候选群数 K',ylim=(0,max(ks.silhouette)*1.2));finish(f,13,'群数选择','K-Means','只用特征距离选择K，不用离职标签调参。')
    pc=read('cluster_pca');f,a=canvas('员工分群的二维投影','第二主成分')
    for k,g in pc.groupby('Cluster'):a.scatter(g.PC1,g.PC2,s=10,alpha=.4,label=f'群{k}')
    a.set_xlabel('第一主成分');a.legend();a.text(.01,.02,f"两轴解释方差 {m['pca_variance']:.1%}；不是完整距离",transform=a.transAxes,fontsize=8);finish(f,14,'分群散点','K-Means','PCA仅展示，聚类使用七维标准化特征。')
    cp=read('cluster_profile').set_index('分群');z=(cp-d[CLUSTER_FEATURES].mean())/d[CLUSTER_FEATURES].std(ddof=0)
    f,a=canvas('员工分群画像的标准化均值','');a.grid(False);im=a.imshow(z,cmap='coolwarm',vmin=-2,vmax=2,aspect='auto');a.set(yticks=np.arange(len(z)),yticklabels=z.index,xticks=np.arange(7),xticklabels=['月收入','总工龄','司龄','职级','培训次数','满意度','工作生活平衡']);a.tick_params(axis='x',rotation=25,labelsize=8);f.colorbar(im,ax=a,label='相对全样本均值的标准差')
    for i in range(len(z)):
        for j in range(7):a.text(j,i,f'{z.iloc[i,j]:.2f}',ha='center',va='center',fontsize=8)
    finish(f,15,'分群画像','K-Means','不将群编号解释为天然高低等级。')
    co=read('cluster_outcomes');f,a=canvas('不同职业阶段群体的离职标签差异','离职标签占比 / %');a.errorbar(np.arange(len(co)),100*co.rate,yerr=[100*(co.rate-co.low),100*(co.high-co.rate)],fmt='o',capsize=6,ms=8,lw=1.8,color=BLUE);a.set(xticks=np.arange(len(co)),xticklabels=[f'{r["分群"]}  |  n={r.n}' for _,r in co.iterrows()],ylim=(0,27),xlim=(-.6,len(co)-.4))
    for i,row in co.iterrows():a.text(i,row.high*100+1.3,f'{row.rate:.2%}',ha='center',fontweight='bold',color='#1D4E73')
    a.text(.02,.96,'误差棒：95% Wilson比例区间',transform=a.transAxes,va='top',fontsize=8,color='#607184');finish(f,16,'分群离职差异','K-Means','95% Wilson区间；仅描述该虚构样本的二项比例不确定性。')
    pred=read('test_predictions');f,a=canvas('独立测试集ROC曲线','真正率 / 召回率')
    for name in ['逻辑回归','随机森林','常数基线']:
        fp,tp,_=roc_curve(pred.actual,pred[name]);a.plot(fp,tp,label=name)
    a.set(xlabel='假正率',xlim=(0,1),ylim=(0,1.02));a.legend();finish(f,17,'分类ROC','离职预测','全部模型使用相同隔离测试集；不在测试集选模型。')
    f,a=canvas('独立测试集精确率召回率曲线','精确率')
    for name in ['逻辑回归','随机森林']:
        pr,re,_=precision_recall_curve(pred.actual,pred[name]);a.plot(re,pr,label=name)
    a.axhline(pred.actual.mean(),ls='--',color='gray',label='测试集正类比例');a.set(xlabel='召回率',xlim=(0,1),ylim=(0,1.03));a.legend();finish(f,18,'分类PR','离职预测','AP衡量正类排序质量，不用总体准确率掩盖少数类。')
    cm=np.array(m['confusion']);f,a=canvas('训练期选定阈值下的测试集混淆矩阵','实际标签');a.grid(False);im=a.imshow(cm,cmap='Blues');a.set(xticks=[0,1],xticklabels=['预测留任','预测离职'],yticks=[0,1],yticklabels=['实际留任','实际离职'])
    for i in range(2):
        for j in range(2):a.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=20,color='white' if cm[i,j]>cm.max()/2 else '#111')
    finish(f,19,'混淆矩阵','离职预测','阈值由训练集折外F2选择；呈现误报代价。')
    th=read('thresholds');f,a=canvas('训练集折外阈值的取舍','指标值')
    for col,label in [('precision','精确率'),('recall','召回率'),('F2','F2')]:a.plot(th.threshold,th[col],label=label)
    a.axvline(m['threshold'],color='gray',ls='--',label=f"选定 {m['threshold']:.2f}");a.set(xlabel='预测概率阈值',ylim=(0,1));a.legend();finish(f,20,'阈值敏感性','离职预测','F2更重视召回，属于教学情景假设，不是企业已知成本最优。')
    imp=read('permutation_importance').head(8).iloc[::-1];translations={'JobLevel':'职级','NumCompaniesWorked':'曾任职公司数','OverTime':'加班','MonthlyIncome':'月收入','TotalWorkingYears':'总工龄','YearsAtCompany':'司龄','StockOptionLevel':'股票期权等级','JobRole':'岗位','JobSatisfaction':'工作满意度','EnvironmentSatisfaction':'环境满意度','YearsWithCurrManager':'现经理共事年数','BusinessTravel':'出差','JobInvolvement':'工作投入','YearsSinceLastPromotion':'距上次晋升年数','WorkLifeBalance':'工作生活平衡','DistanceFromHome':'居住距离'}
    f,a=canvas('特征置换后AP的平均下降','');a.barh(np.arange(len(imp)),imp.AP_drop,color=BLUE,xerr=imp['std'],capsize=3);a.set(yticks=np.arange(len(imp)),yticklabels=[translations.get(t,t) for t in imp.feature],xlabel='测试集AP下降（误差棒为15次置换标准差）');finish(f,21,'置换重要性','离职预测','相关特征可能分摊重要性；不等于因果效应。')
    ot=read('overtime');f,a=canvas('加班标签与离职标签的关联','离职标签占比 / %');a.errorbar([0,1],100*ot.rate,yerr=[100*(ot.rate-ot.low),100*(ot.high-ot.rate)],fmt='o',capsize=5,color=BLUE);a.set(xticks=[0,1],xticklabels=[f'{r["加班"]}\nn={r.n}' for _,r in ot.iterrows()],ylim=(0,45),xlim=(-.6,1.6));finish(f,22,'加班关联区间','结构分析','95% Wilson区间；横截面关联不能证明加班造成离职。')
    f,a=canvas('月收入分布与离职标签','月收入 / 原始数值单位');a.boxplot([d.loc[d.Exited==0,'MonthlyIncome'],d.loc[d.Exited==1,'MonthlyIncome']],tick_labels=['留任标签','离职标签'],patch_artist=True,boxprops={'facecolor':'#82ADD7'});finish(f,23,'收入箱线分布','结构分析','币种未由来源明确，故不标美元；离群点保留。')
    fair=read('group_diagnostics');f,a=canvas('测试集性别分组的模型误差诊断','比例 / %');xx=np.arange(len(fair));a.bar(xx-.18,100*fair.recall,.36,color=BLUE,label='召回率');a.bar(xx+.18,100*fair.FPR,.36,color='#E69F00',label='假正率');a.set(xticks=xx,xticklabels=[f'{r.Gender}\nn={r.n}, 正类={r.positives}' for _,r in fair.iterrows()],ylim=(0,100));a.legend();finish(f,24,'群体误差诊断','离职预测','性别未输入模型；小样本差异不构成公平性保证。')
    pd.DataFrame(INDEX).to_csv(TABLE/'figure_index.csv',index=False,encoding='utf-8-sig')



def run():
    """重建全部24张最终样式图；不读取或复制已有PNG。"""
    from figure_styles import structure, models, abc, profile, raincloud, diagnostics
    from figure_styles.theme import dark_theme
    FIG.mkdir(parents=True, exist_ok=True)
    with plt.rc_context():
        with dark_theme({14,17,18,20}):
            _base_run()
        with plt.rc_context():
            plt.rcParams.update({"axes.labelsize": "medium"})
            structure.run()
        with dark_theme({11,12,13,15,19,23}):
            plt.rcParams.update({"axes.labelsize": "medium"})
            models.run()
            abc.run()
            profile.run()
            raincloud.run()
        plt.rcParams.update({"axes.labelsize": "medium"})
        diagnostics.run()
    index = pd.DataFrame(INDEX)
    descriptions = {
        2: ('哑铃图：岗位规模与六岗位均值', '圆点比较岗位人数与六岗位均值。'),
        4: ('点图：岗位比例与Wilson区间', '点表示样本比例，横线表示95% Wilson区间。'),
        5: ('华夫图：部门标签构成', '每格表示部门样本的1%，局部填充表示不足1%的部分。'),
        12: ('ABC棒棒糖图', '对照岗位数占比与离职案例占比。'),
        19: ('扇形混淆矩阵', '百分比按实际类别（行）计算，扇形面积与样本数成正比。'),
        22: ('加班关联哑铃图', '圆点为样本比例，加粗短线为95% Wilson区间。'),
        23: ('收入雨云图', '箱线与密度使用全样本；散点每组固定种子抽取最多100条。'),
    }
    for number, (kind, note) in descriptions.items():
        mask = index['编号'].eq(f'fig{number:02d}')
        index.loc[mask, '对应模板或模型'] = kind
        index.loc[mask, '解读'] = note
    index.loc[index['编号'].isin(['fig02','fig04','fig05']), '类别'] = '图型改进'
    index.to_csv(TABLE/'figure_index.csv', index=False, encoding='utf-8-sig')
    print('24张最终样式PNG已从数据重新生成。')

if __name__=='__main__':run()
