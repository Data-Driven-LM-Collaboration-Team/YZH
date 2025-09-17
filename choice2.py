from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import os
import nltk
import glob
import re
import json
import logging



class RAGResponder:
    _instance = None

    POLICY_MAP = {
        "fifo": 0,
        "finish_time_fairness": 1, "finish time fairness": 1, "ftf": 1,
        "gandiva": 2,
        "allox": 3,
        "min_total_duration": 4, "minimum total duration": 4,
        "max_min fairness": 5, "max_min_fairness": 5, "max_min_fairness_water_filling": 5, "max_min_fairness_water_filling_with_perf": 5, "max_min_fairness_with_perf": 5, "max_min_fairness_with_perf_slo": 5, "max_min_fairness_with_packing": 5, "max_min_fairness_with_packing_slo": 5,
         "max_sum_throughput_normalized_by_cost_perf_slo":6, "max_sum_throughput_normalized_by_cost_perf_with_packing":6, "max_sum_throughput_normalized_by_cost_perf_with_packing_slo":6, "max_sum_throughput_normalized_by_cost_perf":6,
    "isolated":7, "isolated":7,}
    def __init__(self, docs_folder: str, vectorstore=None):
        self._logger = logging.getLogger("RAGResponder")
        self._logger.setLevel(logging.INFO)

        os.environ["OPENAI_API_KEY"] = "sk-dWjrC12PnSdYHxSOS67ncwmwvaeacBYZSFAGB0BW1fBqslWE"
        # 只加载 txt 文件
        file_paths = glob.glob(os.path.join(docs_folder, "*.txt"))
        documents = []
        for path in file_paths:
            loader = TextLoader(path, encoding='utf-8')  #避免 Unstructured 引入 NLTK
            documents.extend(loader.load())

        # 切分文档
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        # 文本转向量
        embeddings = HuggingFaceEmbeddings(model_name="/home/l40/newdisk1/yzh/gavel2/rag/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(docs, embeddings)
        self.vectorstore = FAISS.from_documents(docs, embeddings)

        PROMPT = """
    你是一个GPU集群调度专家,擅长根据集群资源状态和任务特征选择最优调度策略。使用以下文档回答问题，但可以：
        1. 在涉及常识推理时使用通用知识
        2. 当文档不完整时进行合理推断
        3. 对技术术语保持专业

首先，请学习并模仿以下示例的分析过程：

【示例】
- 集群状态：集群资源紧张，利用率已达85%。当前任务队列中，70%的任务为训练任务（需要多卡，长耗时），30%为推理任务（需要低延迟，有SLO要求）。任务优先级差异较大。
- 推理过程：
  1.  **关键特征提取**：资源紧张（高利用率）、长任务占比高（70%）、存在SLO任务（30%推理任务）、优先级差异大。
  2.  **策略评估**：
      - Gandiva：擅长抢占和组合调度，在资源紧张、有长短任务混合的场景下性能好，优先考虑。
      - Max_sum...SLO：SLO任务占比为30% < 70%阈值，故不首选。
      - Max_min fairness：优先级差异大，单纯的最大最小公平可能无法满足高优先级任务的紧迫性。
      - Finish_Time_Fairness：优先级差异大，此策略可能不适用。
      - Allox：任务不全为单卡，有多卡需求，故排除。
      - Isolated：资源紧张，绝非“极度富裕”，故排除。
  3.  **决策**：综合来看，Gandiva最能应对当前资源紧张、任务异构的场景，通过抢占和组合调度来兼顾吞吐量和SLO。
- 最终策略选择：Gandiva
现在，请根据以下信息进行分析：
        文档片段：{context}
        当前集群状态：{question}

请你根据集群状态和文档信息，从以下策略
Allox、Finish_Time_Fairness、Gandiva、Isolated、Max_min fairness、Max_sum_throughput_normalized_by_cost_perf_slo
中选出最合适的调度策略(只能选一个),必须给出准确的策略名称并解释理由,并严格按照以下json格式回答，确保使用双引号并用代码块包裹：
"policy": "最终选择的策略"，"reason":
"1. 集群关键特征提取（包括资源状态、任务规模、优先级、SLO占比、短/长任务比例等）
2. 选择理由（模仿示例，展示推理过程，说明为何该策略最匹配当前状态，并简要说明其他策略为何不合适）"
        """


        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=PROMPT
        )

        # 创建检索式问答链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                model_name="gpt-5-mini",#gpt-3.5-turbo gpt-4o-mini
                openai_api_key="sk-dWjrC12PnSdYHxSOS67ncwmwvaeacBYZSFAGB0BW1fBqslWE",
                base_url="https://api.chatanywhere.tech/v1"
            ),
            chain_type="stuff",
            chain_type_kwargs={
                "prompt": self.prompt_template
            },
            retriever=vectorstore.as_retriever(),
            return_source_documents = False
        )

    def answer(self, cluster_state: str) -> str:
        """系统调用此方法进行问答"""
        # 1. 先执行检索获取相关文档
        retriever = self.vectorstore.as_retriever()
        source_documents = retriever.get_relevant_documents(cluster_state)

        # 2. 打印检索到的文档片段
        print("\n===== RAG 检索到的文档片段 =====")
        for i, doc in enumerate(source_documents):
            content = doc.page_content.replace("\n", " ")  # 简化换行符
            print(f"[片段 {i + 1}]: {content[:200]}...")  # 只打印前200字符
        print("=" * 50)

        # 3. 组装最终 prompt
        context = "\n".join([f"[片段 {i + 1}]: {doc.page_content}"
                             for i, doc in enumerate(source_documents)])

        prompt = self.prompt_template.format(
            context=context,
            question=cluster_state
        )

        # 4. 打印最终组装好的 prompt
        print("\n===== RAG 最终输入给大模型的完整 Prompt =====")
        print(prompt)
        print("=" * 50)

        result = self.qa_chain.invoke({"query": cluster_state})
        return result

    def _log_prompt_details(self, question: str, source_documents: list, prompt: str):
        """记录检索到的文档片段和最终 prompt"""
        self._logger.info("===== RAG 输入内容详情 =====")

        # 记录检索到的文档片段
        self._logger.info("检索到的文档片段:")
        for i, doc in enumerate(source_documents):
            content = doc.page_content.replace("\n", " ")  # 简化换行符
            self._logger.info(f"[片段 {i + 1}]: {content[:200]}...")  # 只记录前200字符

        # 记录最终组装好的 prompt
        self._logger.info("\n最终输入给大模型的完整 Prompt:")
        self._logger.info(prompt)
        self._logger.info("=" * 50)


    @classmethod
    def get_instance(cls, docs_folder):
        if cls._instance is None:
            print("Loading RAGResponder...")
            cls._instance = RAGResponder(docs_folder)
        return cls._instance

    @staticmethod
    def parse_policy(text: str) -> int:
        try:
            # 去掉 markdown 中的 ```json 或 ``` 标记
            cleaned = re.sub(r"```(?:json)?", "", text)
            cleaned = cleaned.strip("` \n")

            # 解析 JSON 内容
            policy_dict = json.loads(cleaned)

            policy_name = policy_dict.get("policy", "").strip().lower()

            if not policy_name:
                raise ValueError("策略名称为空")

            # 在策略映射中查找
            for alias, code in RAGResponder.POLICY_MAP.items():
                if alias.lower() in policy_name:
                    return code

            raise ValueError(f"未知策略名称: {policy_name}")

            # 返回 policy 字段
            #return policy_dict.get("policy", "")
        except Exception as e:
            print(f"[parse_policy error] 解析失败：{e}")
            return 2

    def test_parse_policy(self):

        #test_input = {'query': '根据当前集群状态总结，可以帮助工作人员选择调度策略的集群状态如下：\n\n当前集群的显卡资源处于充足状态，具备108块GPU，且可用率为100.0%。同时，任务所需节点类型呈现轻度异构特征，即具有异构性评级。任务队列中绝大多数任务需要多卡运行，且不同任务间优先级差异可忽略。系统内有较多需严格按时完成的紧急需求型任务，而待处理任务总量预计将造成轻度队列积压。\n\n综上所述，当前集群状态适合采取灵活的动态调度策略，优先考虑满足紧急需求型任务的执行，同时可以充分利用集群充足的GPU资源，实现任务的高效处理和资源的最大化利用。需要关注队列中的积压任务数量，及时进行任务调度和资源分配，以保证集群的高效运行。', 'result': '### 1. 集群关键特征提取\n根据提供的集群状态信息，可以提取以下关键特征：\n- **资源状态**：GPU资源充足（108块GPU，可用率100%），轻度异构\n- **任务规模**：绝大多数任务需要多卡运行（scale_factor > 1）\n- **优先级**：不同任务间优先级差异可忽略\n- **SLO占比**：系统内有较多需严格按时完成的紧急需求型任务（高SLO占比）\n- **任务类型**：待处理任务总量预计造成轻度队列积压（混合短/长任务）\n- **调度需求**：需要灵活的动态调度策略，优先满足紧急需求型任务\n\n### 2. 最终选择的策略名称\n**Max_sum_throughput_normalized_by_cost_perf_slo**\n\n### 3. 选择理由\n该策略在以下关键维度完美匹配当前集群状态，且显著优于其他候选策略：\n\n**核心优势维度：**\n1. **SLO保障能力**：\n   - 集群明确存在"较多需严格按时完成的紧急需求型任务"，该策略通过强制保障SLO任务的设计（约束条件含SLO限制）直接满足这一核心需求\n   - 相比Finish_Time_Fairness仅支持普通优先级权重，本策略专为SLO任务优化，提供严格时间保障\n\n2. **资源利用效率**：\n   - 在资源充足（108 GPU）但存在轻度积压的场景下，策略的"最大化吞吐量/成本比值总和"目标能充分利用富裕资源\n   - 相比Isolated的静态分配或Gandiva的组合限制，本策略通过动态调整实现更高利用率\n\n3. **异构适应性**：\n   - 支持集群的轻度异构特征（明确支持多worker_type配置）\n   - 相比Allox强制单卡限制或Gandiva的相同scale_factor配对要求，本策略无此类限制\n\n4. **动态响应能力**：\n   - 根据剩余步数动态调整的特性，非常适合存在队列积压和混合任务时长的场景\n   - 相比Max_min fairness的静态凸优化求解，能更好应对实时变化\n\n**其他策略排除原因：**\n- Allox：强制单卡任务不适用（当前多卡任务为主）\n- Gandiva：设计目标为资源紧张场景（当前资源充足），且组合限制会浪费资源\n- Isolated：资源利用率低且无SLO支持\n- Max_min fairness：公平性保障过度（当前优先级差异小），且计算开销大\n- Finish_Time_Fairness：虽支持多卡但SLO保障能力弱于本策略\n\n**结论**：\n在资源充足但存在高SLO任务占比、多卡任务为主的场景下，Max_sum_throughput_normalized_by_cost_perf_slo是唯一能同时满足严格SLO保障、高资源利用率、动态调整需求的三重目标的策略，其SLO敏感特性和成本效率优化在当前集群状态下具有不可替代性。'}

        test_input =  {'query': '能够帮助工作人员选择调度策略的集群状态：\n当前集群的显卡资源处于充足状态，任务所需节点类型呈现强异构特征。任务队列中少数任务需要多卡运行，不同任务间优先级差异可忽略。系统内需严格按时完成的紧急需求型任务不多，待处理任务总量预估将造成轻度队列积压。\n\n综合考虑到资源充足、任务异构性强、优先级差异可忽略、紧急需求型任务数量不多、轻度队列积压等因素，工作人员在选择调度策略时可以优先考虑均衡资源利用，灵活处理任务的异构性，合理安排任务的优先级，确保按时完成需求较为紧迫的任务，同时适时调整资源分配以缓解轻度队列积压的情况。', 'result': '### 1. 集群关键特征提取\n根据提供的集群状态信息，可以提取以下关键特征：\n- **资源状态**：显卡资源充足，节点类型呈现强异构特征\n- **任务规模**：多数任务为单卡运行，少数任务需要多卡（scale_factor不完全为1）\n- **优先级**：不同任务间优先级差异可忽略\n- **SLO占比**：紧急需求型任务不多（SLO需求占比低）\n- **任务长度**：轻度队列积压（暗示任务执行时间有一定差异，但未明确短/长任务比例）\n\n### 2. 最终选择的策略名称\n**Max_min fairness**\n\n### 3. 选择理由\n该策略在当前场景下具有以下优势：\n1. **异构资源适配性**：\n   - 支持异构GPU集群（匹配"节点类型呈现强异构特征"）\n   - 允许scale_factors可配置（能处理少数多卡任务需求）\n\n2. **公平性保障**：\n   - 最大化最小吞吐量的设计天然适合优先级差异小的场景（匹配"优先级差异可忽略"）\n   - 通过加权分配防止资源充足时的碎片化浪费\n\n3. **资源利用率优化**：\n   - 在资源充足时仍能保持合理分配（优于Gandiva的资源紧张优化倾向）\n   - 避免Isolated策略在异构环境下的资源碎片问题\n\n4. **动态适应性**：\n   - 支持低/中/高负载（覆盖"轻度队列积压"场景）\n   - 优于Allox的静态分配缺陷\n\n排除其他策略的原因：\n- **Allox**：强制要求scale_factor=1，无法处理多卡任务\n- **Finish_Time_Fairness**：优先级机制冗余（当前无显著优先级差异）\n- **Gandiva**：更适合资源紧张场景（当前资源充足）\n- **Isolated**：在强异构环境下会产生严重碎片\n- **Max_sum_throughput...**：SLO任务占比不足（需>65%）\n\n关键维度优势对比：\n| 维度               | Max_min fairness优势体现                                                                 |\n|--------------------|-----------------------------------------------------------------------------------------|\n| 异构资源支持       | 唯一同时支持：多worker_type配置+非单一scale_factor+动态调整                             |\n| 公平性             | 在无优先级差异时提供最均衡的分配（优于Finish_Time_Fairness的优先级敏感设计）            |\n| 计算开销           | 资源充足时O(m³)复杂度可接受（Allox同等复杂度但功能受限）                                |\n| 碎片控制           | 通过组合机制减少碎片（明显优于Isolated）                                                |'}

        # 提取策略文本（result字段）
        policy_text = test_input['result']

        # 调用解析函数
        policy_code = RAGResponder.parse_policy(policy_text)

        # 获取策略名称映射（反向查找）
        #policy_name = {v: k for k, v in RAGResponder.POLICY_MAP.items()}.get(policy_code, "unknown")

        # 打印结果
        print("=== 策略解析结果 ===")
        print(f"原始策略文本: {policy_text[:100]}... (截断显示)")
        print(f"解析出的策略代码: {policy_code}")
        #print(f"对应的策略名称: {policy_name}")
        print("===================")

if __name__ == "__main__":
    import os

    docs_folder = "/home/l40/newdisk1/yzh/gavel2/rag/"
    rag = RAGResponder(docs_folder)
    cluster_state = """能够帮助工作人员选择调度策略的集群状态：
资源方面，集群显卡资源充裕，可用率为100%，但存在异构性，需要考虑不同显卡类型的调度问题。
任务特征方面，任务规模分布一致，优先级差异可忽略，但具有SLO需求的任务占比30%。同时，短任务占比较高，需要高效调度。
负载压力方面，队列中有20个任务，待处理任务总量较多，造成了轻度的队列积压。

综上所述，当前集群的显卡资源处于充足状态，任务所需节点类型呈现轻微异构特征。任务队列中多数任务需要多卡运行，不同任务间优先级差异可忽略。系统内需严格按时完成的紧急需求型任务较多，待处理任务总量预估将造成轻度队列积压。在这种情况下，工作人员可以采取针对不同显卡类型的调度策略，优先处理具有SLO需求的紧急任务，并合理安排短任务以提高调度效率。 """
    test_output = rag.answer(cluster_state)
    print(test_output)
    policy_text = test_output['result']
    # 调用解析函数
    policy_code = RAGResponder.parse_policy(policy_text)
    # rag.test_parse_policy()
    print(f"解析出的策略代码: {policy_code}")

#57%，需求较为紧张，需及时处理 - 若任务需严格满足SLO且SLO需求占比较高（如超过80%），可考虑 Max_sum_throughput_normalized_by_cost_perf_slo。需严格满足SLO且SLO需求占比较高（如超过80%），