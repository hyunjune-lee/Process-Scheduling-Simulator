from scheduler import Scheduler


class RR(Scheduler):
    def __init__(self, process_input_list, cpu_count, quantum):
        super().__init__(process_input_list, cpu_count)
        self.quantum = quantum

    def run(self):
        cur_time = 0
        finish_processes_count = 0
        at_idx = 0
        sorted_processes = sorted(self.processes, key=lambda x: x.at)
        # 끝난 프로세스가 총 프로세스의 수와 같아질때까지 작동
        while finish_processes_count < self.process_count:
            # 현재 시간에 도착할 프로세스 대기열 큐에 넣어주기
            for process_idx in range(at_idx, self.process_count):
                process = sorted_processes[process_idx]
                if process.at == cur_time:
                    print("processe arrived - cur_time:", cur_time, " p_id :", process.id)
                    self.ready_queue.append(process)
                elif process.at > cur_time:
                    at_idx = process_idx
                    break

            # history 기록하기
            self.record_history(self.ready_queue[:], self.cpus, self.processes)

            cpu_keep_working_count = self.get_cpu_keep_working_count(self.quantum)
            # cpu들을 돌면서
            for cpu in self.cpus:
                # cpu의 일이 끝났으면
                if cpu.is_finished(self.quantum):
                    # 만약 프로세스가 실행시간이 남아있으면 다시 대기열 큐에 넣어준다.
                    # 대기열의 프로세스 개수가 놀고 있는 CPU 개수 이하이면 그대로 둔다. 아니면 진행
                    if cpu.process.remain_bt > 0:
                        # 일을 계속할 수 있으면 계속하게 한다.
                        if cpu_keep_working_count > 0:
                            cpu_keep_working_count -= 1
                            cpu.work_time = 0
                            continue
                        self.ready_queue.append(cpu.process)
                        print("processe arrived again - cur_time:", cur_time, " p_id :", cpu.process.id)
                    else:
                        # 프로세스가 완전히 끝나면 현재시간을 기준으로 각 time을 계산
                        # 끝난 프로세스의 개수 1 증가
                        print("processe finished - cur_time:", cur_time, " p_id :", cpu.process.id)
                        cpu.process.calculate_finished_process(cur_time)
                        finish_processes_count += 1
                    # 일이 끝난 CPU는 쉬게 해준다.
                    cpu.set_idle()

                # cpu가 쉬고 있고
                if cpu.is_idle():
                    # 대기열에 프로세스가 하나 이상 존재한다면
                    if self.ready_queue:
                        cpu.set_process(self.ready_queue.pop(0))

            # 현재시간 증가
            cur_time += 1
            super().work()
