import os
import json
from simple_term_menu import TerminalMenu


from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


def obter_pods(namespace):
    print("pod1, pod2, pod3")
    input()
    return ["pod1", "pod2", "pod3"]

def obter_secrets(namespace):
    print("pod1, pod2, pod3")
    input()

    return ["pod1", "pod2", "pod3"]

def obter_logs(namespace):
    print("pod1, pod2, pod3")
    input()

    return ["pod1", "pod2", "pod3"]

def obter_configmaps(namespace):
    print("pod1, pod2, pod3")
    input()

    return ["pod1", "pod2", "pod3"]