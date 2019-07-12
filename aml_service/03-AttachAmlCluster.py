"""
Copyright (C) Microsoft Corporation. All rights reserved.​

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
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.authentication import AzureCliAuthentication
import os

cli_auth = AzureCliAuthentication()
# Get workspace
config_folder = os.environ.get("PIPELINE_CONFIG_FOLDER", './aml_config')
config_file = os.environ.get("PIPELINE_CONFIG_FILE", 'config.json')

cfg = os.path.join(config_folder, config_file)

# Get workspace
ws = Workspace.from_config(path=cfg, auth=cli_auth)

aml_cluster_name = os.environ.get("AML_CLUSTER_NAME", None)

# un-comment the below lines if you want to put AML Compute under Vnet. Also update /aml_config/security_config.json
# vnet_resourcegroup_name = config['vnet_resourcegroup_name']
# vnet_name = config['vnet_name']
# subnet_name = config['subnet_name']

# Verify that cluster does not exist already
try:
    cpu_cluster = AmlCompute(workspace=ws, name=aml_cluster_name)
    print("Found existing cluster, use it.")
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(
        vm_size=os.environ.get("AML_CLUSTER_VM_SIZE", None),
        vm_priority=os.environ.get("AML_CLUSTER_PRIORITY", 'lowpriority'),
        min_nodes=os.environ.get("AML_CLUSTER_MIN_NODES", 1),
        max_nodes=os.environ.get("AML_CLUSTER_MAX_NODES", 3),
        idle_seconds_before_scaledown="300",
        #    #Uncomment the below lines for VNet support
        #    vnet_resourcegroup_name=vnet_resourcegroup_name,
        #    vnet_name=vnet_name,
        #    subnet_name=subnet_name
    )
    cpu_cluster = ComputeTarget.create(ws, aml_cluster_name, compute_config)

cpu_cluster.wait_for_completion(show_output=True)
