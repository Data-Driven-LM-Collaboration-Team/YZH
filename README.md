<img width="3272" height="2163" alt="调度" src="https://github.com/user-attachments/assets/4b44c94b-770a-4ec4-81d7-927348a10b97" />
从五个层面对策略和集群状态进行特征总结

类似成本、完成时间等指标以用户需求的形式提出

最终指标以拼接的trace为标准

策略分层：选择策略，决定是否打包
<img width="3571" height="3092" alt="调度3" src="https://github.com/user-attachments/assets/bd220a88-a5ce-48d6-b55e-046685493b53" />

<img width="3571" height="4562" alt="调度4" src="https://github.com/user-attachments/assets/64cbe7f3-5294-470f-a7f6-ce2f6de47165" />

背景：在硬件资源异构化的场景下，根据需求对任务进行资源分配，实现高效率的资源利用和任务管理。面对任务资源需求的变化，单一调度策略无法满足需求，因此需要对调度策略进行动态的切换。  


动机：普通的阈值切换不能满足用户需求，需要引入大模型对调度策略进行切换


挑战：大模型对集群状态的理解能力不足  
     大模型对策略需求的理解


贡献：调度策略动态切换的多智能体框架
     

实验：性能需求 成本需求 SLO需求（调整SLO等级比例） 公平性需求   
     批处理任务测试  
     流式任务测试  
     消融实验  
 
     


