"""IBM HR教学数据：审计、ABC、KMeans及无泄漏分类评估。"""
from pathlib import Path
import json, zipfile, hashlib, sqlite3
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict, cross_validate
from sklearn.metrics import silhouette_score, adjusted_rand_score, roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, accuracy_score, brier_score_loss, confusion_matrix
from sklearn.inspection import permutation_importance

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; CLEAN=ROOT/'data/clean'; TABLE=ROOT/'outputs/tables'; FIG=ROOT/'outputs/figures'
SEED=2026
ROLES={'Sales Executive':'销售主管','Research Scientist':'研究科学家','Laboratory Technician':'实验室技术员','Manufacturing Director':'制造总监','Healthcare Representative':'医疗代表','Manager':'经理','Sales Representative':'销售代表','Research Director':'研究总监','Human Resources':'人力资源'}
DEPTS={'Sales':'销售','Research & Development':'研发','Human Resources':'人力资源'}
CLUSTER_FEATURES=['MonthlyIncome','TotalWorkingYears','YearsAtCompany','JobLevel','TrainingTimesLastYear','JobSatisfaction','WorkLifeBalance']
NUM=['DistanceFromHome','MonthlyIncome','NumCompaniesWorked','PercentSalaryHike','TotalWorkingYears','TrainingTimesLastYear','YearsAtCompany','YearsInCurrentRole','YearsSinceLastPromotion','YearsWithCurrManager']
CAT=['BusinessTravel','Department','Education','EducationField','EnvironmentSatisfaction','JobInvolvement','JobLevel','JobRole','JobSatisfaction','OverTime','PerformanceRating','RelationshipSatisfaction','StockOptionLevel','WorkLifeBalance']
def save(df,name):df.to_csv(TABLE/f'{name}.csv',index=False,encoding='utf-8-sig')
def wilson(k,n):
    p=np.asarray(k)/np.asarray(n);z=1.96;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return mid-half,mid+half
def grouped(d,col):
    t=d.groupby(col,observed=True).Exited.agg(n='size',exits='sum').reset_index();t['rate']=t.exits/t.n;t['low'],t['high']=wilson(t.exits,t.n);return t
def run():
    for p in [CLEAN,TABLE,FIG]:p.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(RAW/'ibm_hr.zip') as z:
        member='WA_Fn-UseC_-HR-Employee-Attrition.csv';payload=z.read(member);(RAW/member).write_bytes(payload)
    raw=pd.read_csv(RAW/member);d=raw.drop_duplicates().copy()
    assert d.EmployeeNumber.is_unique and len(d)>=500
    assert set(d.Attrition)=={'Yes','No'}
    assert ((d.YearsAtCompany>=d.YearsInCurrentRole)&(d.YearsAtCompany>=d.YearsSinceLastPromotion)&(d.YearsAtCompany>=d.YearsWithCurrManager)).all()
    assert (d.TotalWorkingYears>=d.YearsAtCompany).all()
    profile=pd.DataFrame({'field':raw.columns,'dtype':raw.dtypes.astype(str).values,'missing':raw.isna().sum().values,'unique':raw.nunique().values});save(profile,'schema_profile')
    save(raw.describe().T.rename_axis('field').reset_index(),'numeric_profile')
    save(pd.DataFrame([['原始记录',len(raw)],['完全重复删除',int(raw.duplicated().sum())],['缺失单元格',int(raw.isna().sum().sum())],['保留记录',len(d)]],columns=['step','count']),'cleaning_audit')
    d['Exited']=d.Attrition.eq('Yes').astype(int);d['岗位']=d.JobRole.map(ROLES);d['部门']=d.Department.map(DEPTS)
    d['司龄组']=pd.cut(d.YearsAtCompany,[-1,1,3,5,10,100],labels=['0—1年','2—3年','4—5年','6—10年','11年以上']).astype(str)
    d['加班']=d.OverTime.map({'Yes':'加班','No':'不加班'})
    for col,name in [('岗位','roles'),('部门','departments'),('加班','overtime'),('司龄组','tenure'),('JobSatisfaction','satisfaction')]:save(grouped(d,col),name)
    role=grouped(d,'岗位').sort_values(['exits','岗位'],ascending=[False,True]);role['share']=role.exits/role.exits.sum();role['cum']=role.share.cumsum();prior=role['cum']-role['share'];role['ABC']=np.select([prior<.8,prior<.95],['A','B'],default='C');save(role,'abc_roles')
    sensitivity=[]
    for a in [.75,.8,.85]:
        take=prior<a;sensitivity.append({'A_cutoff':a,'roles':int(take.sum()),'exits':int(role.loc[take,'exits'].sum()),'coverage':float(role.loc[take,'share'].sum())})
    save(pd.DataFrame(sensitivity),'abc_sensitivity')
    # 分群是全样本的描述分析；不接入预测管线，标签绝不进入聚类。
    Z=StandardScaler().fit_transform(d[CLUSTER_FEATURES]);ks=[];models={}
    for k in range(2,7):
        model=KMeans(n_clusters=k,n_init=30,random_state=SEED).fit(Z);models[k]=model
        ks.append({'k':k,'silhouette':silhouette_score(Z,model.labels_),'inertia':model.inertia_})
    kt=pd.DataFrame(ks);save(kt,'cluster_selection');k=int(kt.sort_values(['silhouette','k'],ascending=[False,True]).iloc[0].k);km=models[k]
    order=pd.Series(d.MonthlyIncome).groupby(km.labels_).mean().sort_values().index;mapping={int(v):i+1 for i,v in enumerate(order)}
    d['Cluster']=[mapping[int(v)] for v in km.labels_];d['分群']='群'+d.Cluster.astype(str)
    cp=d.groupby('分群')[CLUSTER_FEATURES].mean();save(cp.reset_index(),'cluster_profile');save(grouped(d,'分群'),'cluster_outcomes')
    pc=PCA(n_components=2).fit(Z);coords=pc.transform(Z);save(pd.DataFrame({'PC1':coords[:,0],'PC2':coords[:,1],'Cluster':d.Cluster,'EmployeeNumber':d.EmployeeNumber}),'cluster_pca')
    stability=[{'seed':s,'ARI':adjusted_rand_score(km.labels_,KMeans(n_clusters=k,n_init=30,random_state=s).fit_predict(Z))} for s in [1,42,2025]];save(pd.DataFrame(stability),'cluster_stability')
    d=d.merge(role[['岗位','ABC']],on='岗位',validate='many_to_one');d.to_csv(CLEAN/'employees.csv',index=False,encoding='utf-8-sig')
    with sqlite3.connect(CLEAN/'hr.sqlite') as con:d.to_sql('employees',con,index=False,if_exists='replace');role.to_sql('role_abc',con,index=False,if_exists='replace')
    # 隔离测试集，模型选择和阈值只使用训练集分层5折结果。
    X=d[NUM+CAT];y=d.Exited
    train,test=train_test_split(np.arange(len(d)),test_size=.25,stratify=y,random_state=SEED)
    prep=ColumnTransformer([('numeric',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUM),('category',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])
    estimators={'逻辑回归':LogisticRegression(C=1,solver='liblinear',max_iter=2000,random_state=SEED),'随机森林':RandomForestClassifier(n_estimators=300,min_samples_leaf=5,max_features='sqrt',random_state=SEED,n_jobs=1),'常数基线':DummyClassifier(strategy='prior')}
    cv=StratifiedKFold(5,shuffle=True,random_state=SEED);scores=[];fitted={};oofs={}
    for name,est in estimators.items():
        pipe=Pipeline([('preprocess',prep),('model',est)])
        s=cross_validate(pipe,X.iloc[train],y.iloc[train],cv=cv,scoring={'AP':'average_precision','AUC':'roc_auc'},n_jobs=1)
        scores.append({'model':name,'cv_AP':s['test_AP'].mean(),'cv_AP_sd':s['test_AP'].std(ddof=1),'cv_AUC':s['test_AUC'].mean()})
        oofs[name]=cross_val_predict(pipe,X.iloc[train],y.iloc[train],cv=cv,method='predict_proba',n_jobs=1)[:,1]
        # 独立预处理对象，避免跨模型共享已拟合状态。
        from sklearn.base import clone
        fitted[name]=clone(pipe).fit(X.iloc[train],y.iloc[train])
    scores=pd.DataFrame(scores).sort_values('cv_AP',ascending=False);save(scores,'cv_scores');best=scores.iloc[0]['model'];oof=oofs[best]
    thresholds=[]
    for t in np.arange(.05,.81,.01):
        pred=oof>=t;thresholds.append({'threshold':float(t),'F2':float((5*precision_score(y.iloc[train],pred,zero_division=0)*recall_score(y.iloc[train],pred))/(4*precision_score(y.iloc[train],pred,zero_division=0)+recall_score(y.iloc[train],pred)+1e-15)),'precision':precision_score(y.iloc[train],pred,zero_division=0),'recall':recall_score(y.iloc[train],pred),'flagged_share':pred.mean()})
    th=pd.DataFrame(thresholds);save(th,'thresholds');chosen=th.sort_values(['F2','threshold'],ascending=[False,False]).iloc[0];threshold=float(chosen.threshold)
    predictions=pd.DataFrame({'EmployeeNumber':d.iloc[test].EmployeeNumber.values,'actual':y.iloc[test].values});res=[]
    for name,pipe in fitted.items():
        prob=pipe.predict_proba(X.iloc[test])[:,1];pred=prob>= (threshold if name==best else .5);predictions[name]=prob
        res.append({'model':name,'threshold':threshold if name==best else .5,'ROC_AUC':roc_auc_score(y.iloc[test],prob),'AP':average_precision_score(y.iloc[test],prob),'precision':precision_score(y.iloc[test],pred,zero_division=0),'recall':recall_score(y.iloc[test],pred),'F1':f1_score(y.iloc[test],pred,zero_division=0),'accuracy':accuracy_score(y.iloc[test],pred),'Brier':brier_score_loss(y.iloc[test],prob)})
    save(pd.DataFrame(res),'test_metrics');save(predictions,'test_predictions')
    split=d[['EmployeeNumber']].copy();split['split']='train';split.loc[test,'split']='test';save(split,'split_membership')
    p=predictions[best].to_numpy();yt=y.iloc[test].to_numpy();cm=confusion_matrix(yt,p>=threshold);save(pd.DataFrame(cm,index=['actual_0','actual_1'],columns=['pred_0','pred_1']).reset_index(),'confusion')
    rng=np.random.default_rng(SEED);boots=[]
    for _ in range(1000):
        ix=rng.integers(0,len(yt),len(yt))
        if len(np.unique(yt[ix]))==2:boots.append([roc_auc_score(yt[ix],p[ix]),average_precision_score(yt[ix],p[ix])])
    interval=np.quantile(boots,[.025,.975],axis=0);save(pd.DataFrame({'metric':['ROC_AUC','AP'],'low':interval[0],'high':interval[1]}),'test_bootstrap_ci')
    imp=permutation_importance(fitted[best],X.iloc[test],yt,scoring='average_precision',n_repeats=15,random_state=SEED,n_jobs=1);save(pd.DataFrame({'feature':X.columns,'AP_drop':imp.importances_mean,'std':imp.importances_std}).sort_values('AP_drop',ascending=False),'permutation_importance')
    # 群体误差仅用于诊断，性别和年龄不进入预测特征。
    fair=d.iloc[test][['Gender']].copy();fair['actual']=yt;fair['pred']=p>=threshold
    rows=[]
    for gender,g in fair.groupby('Gender'):
        rows.append({'Gender':gender,'n':len(g),'positives':int(g.actual.sum()),'recall':recall_score(g.actual,g.pred,zero_division=0),'FPR':float(g.loc[g.actual==0,'pred'].mean())})
    save(pd.DataFrame(rows),'group_diagnostics')
    metrics={'rows':len(d),'raw_columns':len(raw.columns),'exits':int(y.sum()),'rate':float(y.mean()),'missing':int(raw.isna().sum().sum()),'duplicates':int(raw.duplicated().sum()),'constant_fields':[c for c in raw if raw[c].nunique()==1],'k':k,'silhouette':float(kt.loc[kt.k==k,'silhouette'].iloc[0]),'pca_variance':float(pc.explained_variance_ratio_.sum()),'best_model':best,'threshold':threshold,'train_n':len(train),'test_n':len(test),'train_exits':int(y.iloc[train].sum()),'test_exits':int(yt.sum()),'confusion':cm.tolist(),'features':NUM+CAT,'seed':SEED}
    (TABLE/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={'dataset':'IBM HR Analytics Employee Attrition & Performance','appendix_A':'UCI / Kaggle·IBM HR','page':'https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset','download':'https://www.kaggle.com/api/v1/datasets/download/pavansubhasht/ibm-hr-analytics-attrition-dataset','accessed':'2026-10-27','fictional':True,'license_platform_label':'Database: Open Database, Contents: Database Contents','sha256_zip':hashlib.sha256((RAW/'ibm_hr.zip').read_bytes()).hexdigest(),'sha256_csv':hashlib.sha256(payload).hexdigest()}
    (RAW/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(metrics,ensure_ascii=False))
if __name__=='__main__':run()
