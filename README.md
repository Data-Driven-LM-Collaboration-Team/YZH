效率
[Experiment ID:  0] Configuration: cluster_spec=v100:36|p100:36|k80:36, policy=LLM, seed=0, num_total_jobs=100
[Experiment ID:  0] Results: average JCT=66309.602864, utilization=0.156150, makespan=616391.686433, total_cost=$1822.77, SLO_violations=2

[Experiment ID: 0] Configuration: cluster_spec=v100:36|p100:36|k80:36, policy=Autofolio, seed=0, num_total_jobs=100
[Experiment ID: 0] Results: average JCT=59325.259068, utilization=0.108994, makespan=503922.817010, total_cost=$1347.40, SLO_violations=5

SLO
[Experiment ID:  0] Configuration: cluster_spec=v100:36|p100:36|k80:36, policy=LLM, seed=0, num_total_jobs=100
[Experiment ID:  0] Results: average JCT=75828.056119, utilization=0.155046, makespan=616162.755717, total_cost=$1819.10, SLO_violations=32

[Experiment ID: 0] Configuration: cluster_spec=v100:36|p100:36|k80:36, policy=Autofolio, seed=0, num_total_jobs=100
[Experiment ID: 0] Results: average JCT=59325.259068, utilization=0.108994, makespan=503922.817010, total_cost=$1347.40, SLO_violations=36

成本 
[Experiment ID: 0] onfiguration: cluster_spec=v100:36|p100:36|k80:36, policy=LLM, seed=0, num_total_jobs=100
[Experiment ID: 0] esults: average JCT=71630.767037, utilization=0.098742, makespan=671477.416531, total_cost=$948.50, SLO_violations=49

[Experiment ID: 0] Configuration: cluster_spec=v100:36|p100:36|k80:36, policy=Autofolio, seed=0, num_total_jobs=100
[Experiment ID: 0] Results: average JCT=59325.259068, utilization=0.108994, makespan=503922.817010, total_cost=$1347.40, SLO_violations=36


<img width="3272" height="2163" alt="调度" src="https://github.com/user-attachments/assets/4b44c94b-770a-4ec4-81d7-927348a10b97" />
从五个层面对策略和集群状态进行特征总结

类似成本、完成时间等指标以用户需求的形式提出

最终指标以拼接的trace为标准

策略分层：选择策略，决定是否打包
<img width="3571" height="3092" alt="调度3" src="https://github.com/user-attachments/assets/bd220a88-a5ce-48d6-b55e-046685493b53" />

<img width="3571" height="4562" alt="调度4" src="https://github.com/user-attachments/assets/64cbe7f3-5294-470f-a7f6-ce2f6de47165" />

背景：在硬件资源异构化的场景下，根据需求对任务进行资源分配，实现高效率的资源利用和任务管理。面对任务资源需求的变化，单一调度策略无法满足需求，因此需要对调度策略进行动态的切换。  


动机：需要引入大模型对调度策略进行切换


挑战：大模型对集群状态的理解能力不足  
     大模型对策略需求的理解


贡献：调度策略动态切换的多智能体框架
     

实验：性能需求 成本需求 SLO需求（调整SLO等级比例） 公平性需求等不同需求组合成的trace进行测试  
     批处理任务测试  
     流式任务测试  
     消融实验  

<img width="960" height="540" alt="幻灯片1" src="https://github.com/user-attachments/assets/0ba5b27c-adb2-434d-ac38-a0e7119a6926" />
<img width="960" height="540" alt="幻灯片2" src="https://github.com/user-attachments/assets/330719f5-971e-4808-80bb-33da0052c6f3" />
<img width="960" height="540" alt="幻灯片3" src="https://github.com/user-attachments/assets/ccd66931-fda8-48bd-a75e-d019df93db08" />

 
     


