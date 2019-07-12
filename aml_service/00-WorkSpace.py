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
import azureml.core
from azureml.core import Workspace
from azureml.exceptions._azureml_exception import ProjectSystemException
from azureml.core.authentication import AzureCliAuthentication
import os, json, sys

print("SDK Version:", azureml.core.VERSION)

workspace_name = os.environ.get("WORKSPACE_NAME", None)
resource_group = os.environ.get("RESOURCE_GROUP", None)
subscription_id = os.environ.get("SUBSCRIPTION_ID", None)
location = os.environ.get("LOCATION", None)

cli_auth = AzureCliAuthentication()

try:
    ws = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=cli_auth,
    )

except ProjectSystemException:
    # this call might take a minute or two.
    print("Creating new workspace")
    ws = Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        # create_resource_group=True,
        location=location,
        auth=cli_auth,
    )

config_folder = os.environ.get("PIPELINE_CONFIG_FOLDER", './aml_config')
config_file = os.environ.get("PIPELINE_CONFIG_FILE", 'config.json')

ws.write_config(path=config_folder, file_name=config_file)

# print Workspace details
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep="\n")
