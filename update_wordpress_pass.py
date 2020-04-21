#!/usr/bin/python
#import json
import os
import random
import string
import sys
from kubernetes import client, config, watch
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from pick import pick

def find_pods():
    pods = api.list_namespaced_pod(
            namespace=ns, watch=False)
    wordpress_pods = []
    for i in pods.items:
        name = i.metadata.name
        if "wordpress" in name:
            wordpress_pods.append(name)
    return wordpress_pods

def choose_pod(wordpress_pods):
    option, _ = pick(wordpress_pods, title="Choose the pod")
    print("%s Selected" %(option))
    pod = option
    return pod

def generate_password(stringLength=20):
    print ("Generating new password")
    letters_numbers = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_numbers) for i in range(stringLength)))
    print ("New password created")

def update_password(pod, password):
    print ("Updating gdadmin user\'s password on %s" %(pod))
    exec_command = [
        "/bin/sh",
        "-c",
        "/usr/local/bin/wp --allow-root --path=/var/www/wordpress/ user update gdadmin --user_pass=" + password]
    update = stream(api.connect_get_namespaced_pod_exec,
                    pod,
                    ns,
                    command=exec_command,
                    stderr=True,
                    stdin=False,
                    stdout=True,
                    tty=False)
    print(update)

def main():
    wordpress_pods = find_pods()
    pod = choose_pod(wordpress_pods)
    print ("%s has been selected" %(pod))
    password = generate_password(20)
    update_password(pod, password)
    print ("You can log into the wp-admin with:")
    print ("username: gdadmin")
    print ("password: %s" %(password))

if __name__ == '__main__':
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        sys.exit(1)
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    option, _ = pick(contexts, title="Pick the context to load",
                     default_index=active_index)
    print("%s Selected" %(option))

    ns = option
    os.system("kubectx %s" %(ns))
    config.load_kube_config()
    api = client.CoreV1Api()

    main()
