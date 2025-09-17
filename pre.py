import numpy as np
from collections import Counter
import time


def generate_cluster_report(data):
    # 提取任务列表和集群信息
    jobs = data["jobs"]
    cluster_dict = data["cluster"]

    # 资源态势指标
    total_gpus = sum(cluster_dict.values())
    gpu_types_str = ", ".join(f"{gpu_type}({count})" for gpu_type, count in cluster_dict.items())

    # 计算已分配GPU（从任务分配信息中汇总）
    allocated_gpus = {}
    for job in jobs:
        if "worker_types" in job:
            for gpu_type, specs in job["worker_types"].items():
                allocated = specs.get("allocated", 0)
                allocated_gpus[gpu_type] = allocated_gpus.get(gpu_type, 0) + allocated


    available_gpus_dict = {}
    for gpu_type, total_count in cluster_dict.items():
        allocated_count = allocated_gpus.get(gpu_type, 0)
        available_gpus_dict[gpu_type] = max(0, total_count - allocated_count)

    total_available = sum(available_gpus_dict.values())

    # 资源态势指标
    resource_metrics = {
        "gpu_total": total_gpus,
        "gpu_available": total_available,
        "gpu_types": gpu_types_str,
        "homogeneity_score": 1.0 if len(cluster_dict) == 1 else 0.0
    }

    # 任务特征指标
    scale_factors = [job["scale_factor"] for job in jobs]
    priorities = [job["priority"] for job in jobs]
    total_steps = [job["total_steps"] for job in jobs]
    remaining_steps = [job["remaining_steps"] for job in jobs]

    # SLO计算 - 基于剩余时间
    slo_covered = [1 if job.get("SLO") is not None and job.get("SLO", 0) > 0 else 0 for job in jobs]

    # 计算优先级差异的变异系数
    priority_cv = np.std(priorities) / np.mean(priorities) if len(priorities) > 1 else 0.0

    # 计算任务时长差异的变异系数
    duration_cv = np.std(total_steps) / np.mean(total_steps) if len(total_steps) > 1 else 0.0

    # 计算短任务占比（定义：任务时长 < 中位时长的50%）
    median_duration = np.median(total_steps) if total_steps else 0
    short_job_ratio = sum(1 for steps in total_steps if steps < median_duration * 0.5) / len(jobs) if jobs else 0

    # 任务规模分布统计
    scale_dist = Counter(scale_factors)
    dist_str = ", ".join(f"{k}:{v / len(jobs):.0%}" for k, v in scale_dist.most_common(3))
    if len(scale_dist) > 3:
        dist_str += f" 及其他(共{len(scale_dist)}种)"

    #SLO计算
    slo_status = {"宽松": 0, "适中": 0, "紧张": 0}

    for job in jobs:
        if not job.get("SLO") or job["SLO"] <= 0:
            # 跳过没有SLO的任务
            continue

        # 计算任务剩余时间（小时）
        steps_remaining = job["remaining_steps"]
        if "worker_types" in job:
            steps_remaining = job["remaining_steps"]
            if "worker_types" in job:
                # 使用最大吞吐量类型（保守估算）
                max_throughput = 0
                for specs in job["worker_types"].values():
                    throughput = specs.get("throughput", 1)  # 默认1 step/s
                    # 仅考虑单卡吞吐量，不乘以allocated
                    if throughput > max_throughput:
                        max_throughput = throughput
                # 使用最佳GPU类型的吞吐量
                remaining_seconds = steps_remaining / max_throughput if max_throughput > 0 else float('inf')
        else:
            # 无GPU分配信息时使用默认估算
            remaining_time = steps_remaining * 1e-6 / 3600  # 默认1e-6 steps/s

        # 计算SLO紧迫度
        slo_seconds = job["SLO"]  # SLO秒转小时
        # 计算时间比例
        time_ratio = remaining_seconds / slo_seconds

        # 分级标准：基于时间比例
        if time_ratio <= 0.5:  # 可以在SLO一半时间内完成
            slo_status["宽松"] += 1
        elif time_ratio <= 1.0:  # 可以在SLO时间内完成
            slo_status["适中"] += 1
        else:  # 不能在SLO时间内完成
            slo_status["紧张"] += 1

    total_slo_jobs = sum(slo_covered)
    if total_slo_jobs > 0:
        slo_loose_ratio = slo_status["宽松"] / total_slo_jobs
        slo_moderate_ratio = slo_status["适中"] / total_slo_jobs
        slo_tight_ratio = slo_status["紧张"] / total_slo_jobs
        slo_status_str = f"{slo_loose_ratio:.0%}/{slo_moderate_ratio:.0%}/{slo_tight_ratio:.0%}"
    else:
        slo_status_str = "无SLO任务"

    task_metrics = {
        "scale_factor_distribution": dist_str,
        "priority_cv": priority_cv,
        "slo_coverage": sum(slo_covered) / len(jobs) if jobs else 0,
        "duration_cv": duration_cv,
        "short_job_ratio": short_job_ratio,
        "slo_status": slo_status_str
    }

    # 负载压力指标
    total_remaining = sum(remaining_steps)

    # 估算计算时间（基于各任务GPU类型的吞吐量）
    estimated_hours = 0
    for job in jobs:
        steps_remaining = job["remaining_steps"]
        # 如果有GPU分配信息，使用具体吞吐量估算
        if "worker_types" in job:
            # 计算该任务所有GPU类型的平均吞吐量
            throughputs = []
            for specs in job["worker_types"].values():
                throughput = specs.get("throughput", 1)  # 默认1 step/s
                allocated = specs.get("allocated", 1)  # 默认1 GPU
                throughputs.append(throughput * allocated)
            avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 1
            # 计算该任务的剩余时间（小时）
            job_time_seconds = steps_remaining / avg_throughput
            estimated_hours += job_time_seconds / 3600
            job_time_seconds = steps_remaining / avg_throughput
            estimated_hours += job_time_seconds / 3600
        else:
            # 无GPU分配信息时使用默认估算
            estimated_hours += steps_remaining * 1e-6 / 3600

    workload_metrics = {
        "total_remaining": total_remaining,
        "estimated_hours": estimated_hours,
        "job_queue_length": len(jobs)
    }

    # 生成最终报告模板
    report = f"""
    你是一个集群调度优化工作人员，负责帮助集群总结集群状态。
        输入:状态总结
        输出:能够帮助工作人员选择调度策略的集群状态。
状态总结：
 资源态势：共{resource_metrics['gpu_total']}块GPU（{resource_metrics['gpu_types']}），当前可用率{resource_metrics['gpu_available'] / resource_metrics['gpu_total'] * 100:.1f}%，同构性评级【{'同构' if resource_metrics['homogeneity_score'] >= 0.9 else '异构'}】
 任务特征：{task_metrics['scale_factor_distribution']}的任务规模分布（任务规模分布代表任务显卡使用数量），优先级差异{'可忽略' if task_metrics['priority_cv'] <= 0.2 else '显著'}，具有SLO需求的任务占比{task_metrics['slo_coverage']:.0%}需求比例如下，（需求宽松/适中需求/紧张需求：{task_metrics['slo_status']}），任务时长差异{'显著' if task_metrics['duration_cv'] > 0.4 else '微小'}，短任务占比{task_metrics['short_job_ratio'] * 100:.1f}%
 负载压力：总剩余计算量{workload_metrics['total_remaining']:,} steps（约合{workload_metrics['estimated_hours']:.1f}小时），队列积压{workload_metrics['job_queue_length']}个任务
"""
    return report


# 示例使用 - 符合新的JSON格式
if __name__ == "__main__":
    # 示例数据，符合新格式
    data = {
        "jobs": [
            {
                "job_id": "JobIdPair(5, None)",
                "scale_factor": 1,
                "priority": 1.0,
                "remaining_steps": 1080135,
                "total_steps": 3842187,
                "SLO": 0,
                "worker_types": {
                    "v100": {"throughput": 10.5, "allocated": 0.75},
                    "p100": {"throughput": 6.8, "allocated": 0.25}
                }
            },
            {
                "job_id": "JobIdPair(7, None)",
                "scale_factor": 2,
                "priority": 1.5,
                "remaining_steps": 2500000,
                "total_steps": 5000000,
                "worker_types": {
                    "k80": {"throughput": 3.2, "allocated": 1.0}
                }
            }
        ],
        "cluster": {"v100": 8, "p100": 12, "k80": 16},
        "timestamp": 1680000000,
        "round": 12
    }

    print(generate_cluster_report(data))