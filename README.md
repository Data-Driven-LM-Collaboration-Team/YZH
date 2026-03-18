1、主表：逐类别 AUC 模块没有破坏初始检测能力

2、Object-level Attribution

   对象目标选中率
   
   异常原因解释质量
   <img width="224" height="224" alt="wa_input" src="https://github.com/user-attachments/assets/7d301c56-9910-4f7c-81b2-d07b3e8feda2" />
   <img width="224" height="224" alt="wa_out" src="https://github.com/user-attachments/assets/9983424b-9556-4117-9310-04a6fca52a71" />









****<img width="1503" height="871" alt="image" src="https://github.com/user-attachments/assets/3b5a1abe-01ee-4e86-89a7-9ad2af2f5693" />


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

 


<img width="2257" height="943" alt="image" src="https://github.com/user-attachments/assets/5eb3af14-9334-4b98-a1dc-1b3baead933e" />
<img width="1488" height="813" alt="image" src="https://github.com/user-attachments/assets/b7d4444a-bace-4688-b801-c47b8b6130a0" />
<img width="1505" height="807" alt="image" src="https://github.com/user-attachments/assets/e09f1b5c-c5fb-4f17-bb08-93f89d4fb02e" />





