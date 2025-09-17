import openai
import json
from set_queue import SetQueue
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-dWjrC12PnSdYHxSOS67ncwmwvaeacBYZSFAGB0BW1fBqslWE",
    base_url="https://api.chatanywhere.tech/v1"
)


def process_output(raw_output: str) -> int:
    for char in raw_output:
        if char.isdigit():
            num = int(char)
            if 0 <= num <= 4:
                return num

class SchedulerDecision:
    def __init__(self):
        openai.api_key = "sk-dWjrC12PnSdYHxSOS67ncwmwvaeacBYZSFAGB0BW1fBqslWE"
        openai.base_url = "https://api.chatanywhere.tech/v1"

    @staticmethod


    def get_choice(job_data):

        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "system", "content":
                """你是一个集群调度优化工作人员，负责帮助集群选择调度优化策略。 
                     可用的调度策略包括：
                          0: "fifo",
                          1: "finish_time_fairness",
                          2: "gandiva",
                          3: "allox",
                          4: "min_total_duration"
你要先根据集群状态对集群进行定性分析，比如：
根据任务紧急程度“urgency”: [“紧急任务（>90%）”, “高优先级任务(60-90%)”, “常规任务(<70%)"],
根据任务所需资源“resource_profile”: [“高资源需求(>64GB)”, “需求均衡(32-64GB)", "低资源需求(<32GB)"],
根据step区分任务所在阶段“progress_status”: [“启动阶段(0-10%)”, “中期阶段(10-80%)”, “完成阶段(80-100%)"],
"anomaly": ["资源饥饿", "低效任务"]

                    
                        请根据以下条件选择合适的调度策略：
                        任务的规模、优先级、时限要求
                        集群中不同类型 GPU 的数量和可用性
                        ## 输出规则
                        1. 必须且只能返回0-4的整数
                        2. 禁止任何解释性文字
                        3. 格式示例：3 
                        切记只返回调度策略标号，即所要求的数字。
                        切记只返回数字。"""},
                      {"role": "user", "content": json.dumps(job_data, indent=2)}],
            stream=False, )
        raw_output = response.choices[0].message.content.strip()
        return process_output(raw_output)
        # for chunk in response:
        #     if chunk.choices[0].delta.content is not None:
        #         print(chunk.choices[0].delta.content, end="")
        # return int(chunk.choices[0].delta.content)




    # def get_choice1(self):
    #
    #
    #     response = client.chat.completions.create(
    #         model='gpt-3.5-turbo',
    #         messages=[{"role": "system", "content":
    #             """你是一个集群调度优化工作人员，负责帮助集群选择调度优化策略。
    #                  可用的调度策略包括：
    #                     1. fifo
    #                     2. finish_time_fairness
    #                     3. gandiva
    #                     4. allox
    #                     5. min_total_duration_perf
    #
    #                     请根据以下条件选择合适的调度策略：
    #                     任务的规模、优先级、时限要求
    #                     集群中不同类型 GPU 的数量和可用性
    #
    #                     返回调度策略标号。"""},
    #                   {"role": "user", "content": "hello"}],
    #         stream=True, )
    #     for chunk in response:
    #         if chunk.choices[0].delta.content is not None:
    #             print(chunk.choices[0].delta.content, end="")
    #     return chunk.choices[0].delta.content





def main():
    sched=SchedulerDecision()
    a=sched.get_choice()
    print(a)

if __name__=='__main__':
    main()
