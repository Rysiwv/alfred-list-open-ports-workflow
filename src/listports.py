import sys

import workflow.util
from workflow import Workflow

listen_ports_command = "lsof -i -P -n +c 100 | grep LISTEN"


def get_listen_ports():
    result = workflow.util.run_command([listen_ports_command], shell=True, text=True)
    # print(result)
    return result


def main(wf):
    query = wf.args[0] if len(wf.args) else None
    if query:
        pass
    else:
        results = get_listen_ports()
        process_dict = {}
        pid_dict = {}
        for line in results.split("\n"):
            if line.strip():
                split_word = line.split()
                process = split_word[0].replace("\\x20", " ")
                pid = split_word[1]
                user = split_word[2]
                port = split_word[8].split(":")[-1]
                user_ports_dict = {}
                if process in process_dict:
                    user_ports_dict = process_dict.get(process)
                ports_set = set()
                if user in user_ports_dict:
                    ports_set = user_ports_dict.get(user)
                ports_set.add(port)
                user_ports_dict[user] = ports_set
                process_dict[process] = user_ports_dict
                pid_dict[process] = pid

        for process in process_dict:
            for user in process_dict[process]:
                ports_str = ", ".join(process_dict[process][user])
                item = wf.add_item(title=process + " (" + user + ")",
                            subtitle=ports_str,
                            valid=True,
                            arg=process )
                item.add_modifier(key="cmd",
                                  subtitle="Kill all processes with this name.",
                                  arg=pid_dict[process],
                                  valid=True)

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
