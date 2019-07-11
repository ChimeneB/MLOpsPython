"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
# TODO: Convert to AZ ML CLI
from azureml.core import Workspace
import os
from azureml.core.compute import RemoteCompute, ComputeTarget
# from azureml.core.compute import DsvmCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

# Get workspace
ws = Workspace.from_config(auth=cli_auth)

remote_vm_name = os.environ.get("REMOTE_VM_NAME", None)
remote_vm_username = os.environ.get("REMOTE_VM_USERNAME", None)
remote_vm_password = os.environ.get("REMOTE_VM_PASSWORD", None)
remote_vm_ip = os.environ.get("REMOTE_VM_IP", None)

try:
    attach_config = RemoteCompute.attach_configuration(
        address=remote_vm_ip,
        username=remote_vm_username,
        password=remote_vm_password,
        ssh_port=22
    )

    dsvm_compute = ComputeTarget.attach(
        ws,
        remote_vm_name,
        attach_config
    )
    dsvm_compute.wait_for_completion(show_output=True)

except ComputeTargetException as e:
    print("Caught = {}".format(e.message))
    print("Compute config already attached.")


# Create VM if not available
# compute_target_name = remote_vm_name

# try:
#     dsvm_compute = DsvmCompute(workspace=ws, name=compute_target_name)
#     print('found existing:', dsvm_compute.name)
# except ComputeTargetException:
#     print('creating new.')
#     dsvm_config = DsvmCompute.provisioning_configuration(
#           vm_size="Standard_D2_v2")
#     dsvm_compute = DsvmCompute.create(
#           ws,
#           name=compute_target_name,
#           provisioning_configuration=dsvm_config)
#     dsvm_compute.wait_for_completion(show_output=True)
