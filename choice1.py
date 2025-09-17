import openai
import json
from set_queue import SetQueue
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-dWjrC12PnSdYHxSOS67ncwmwvaeacBYZSFAGB0BW1fBqslWE",
    base_url="https://api.chatanywhere.tech/v1"
)
#

class ClusterStateAnalyzer:

    @classmethod
    def analyze(self, cluster_report: str) -> str:
        """
        你是一个集群调度优化工作人员，负责帮助集群总结集群状态。
        输入:
        - cluster_report: preprocessing.generate_cluster_report生成的文本报告

        输出:
        - 结构化集群状态分析结果（JSON格式）
        """
        SYSTEM_PROMPT_ANALYZER = ("""你是一个集群调度优化工作人员，负责帮助集群总结集群状态。要在以下模板的基础上再加上自己的总结，输出:能够帮助工作人员选择调度策略的集群状态。
                                  当前集群的显卡资源处于[紧缺/平衡/充足]状态，任务所需节点类型呈现[同构/轻度异构/强异构]特征。任务队列中[全部/多数/少数]任务需要多卡运行，不同任务间优先级差异[可忽略/中等/显著]。系统内需严格按时完成的紧急需求型任务[较多/不多/适中]，待处理任务总量预估将造成[轻度/重度]队列积压""")

        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ANALYZER},
                {"role": "user", "content": cluster_report}
            ],
            stream=False
        )
        print()
        return (response.choices[0].message.content)


def main():
    sched = ClusterStateAnalyzer()
    cluster_report = """状态总结：
     资源态势：共96块GPU（k80(32), p100(32), v100(32)），当前可用率100.0%，同构性评级【异构】
     任务特征：1:100%的任务规模分布，优先级差异可忽略，具有SLO需求的任务占比100%需求比例如下，（需求宽松/适中需求/紧张需求：35%/0%/65%），任务时长差异显著，短任务占比30.0%
     负载压力：总剩余计算量23,665,188.2361 steps，队列积压20个任务"""
    a = sched.analyze(cluster_report)
    print(a)


if __name__ == '__main__':
    main()
