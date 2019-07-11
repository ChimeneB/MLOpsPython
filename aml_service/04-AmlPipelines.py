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

import os
import datetime
import argparse
from azureml.core import Workspace, Experiment, Datastore
from azureml.core.runconfig import RunConfiguration, CondaDependencies
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.authentication import AzureCliAuthentication

parser = argparse.ArgumentParser()

parser.add_argument(
    '--pipeline_action',
    help='Defines whether this is a test or publish run',
    )

args = parser.parse_args()

print("Pipeline SDK-specific imports completed")

cli_auth = AzureCliAuthentication()

config_folder = os.environ.get("PIPELINE_CONFIG_FOLDER", './aml_config')
config_file = os.environ.get("PIPELINE_CONFIG_FILE", 'config.json')

cfg = os.path.join(config_folder, config_file)

# Get workspace
ws = Workspace.from_config(path=cfg, auth=cli_auth)
def_blob_store = Datastore(ws, os.environ.get("DATASTORE_NAME"))

experiment_name = os.environ.get("EXPERIMENT_NAME")
aml_cluster_name = os.environ.get("AML_CLUSTER_NAME")
aml_pipeline_name = os.environ.get("PIPELINE_NAME")
model_name = PipelineParameter(
    name="model_name",
    default_value=os.environ.get("MODEL_NAME")
    )

source_directory = os.environ.get("SOURCE_FOLDER", "code")

# Run Config
# Declare packages dependencies required in the pipeline
#       (these can also be expressed manually)
# cd = CondaDependencies.create(
#           pip_packages=["azureml-defaults", 'tensorflow==1.8.0'])
cd = CondaDependencies(os.path.join(config_folder, 'conda_dependencies.yml'))

run_config = RunConfiguration(conda_dependencies=cd)
aml_compute = ws.compute_targets[aml_cluster_name]
run_config.environment.docker.enabled = True
run_config.environment.spark.precache_packages = False

jsonconfigs = PipelineData("jsonconfigs", datastore=def_blob_store)

# Suffix for all the config files
config_suffix = datetime.datetime.now().strftime("%Y%m%d%H")
print("PipelineData object created")

# TODO: update training script to be more generic
# Create python script step to run the training/scoring main script
train = PythonScriptStep(
    name="Train New Model",
    script_name="training/train.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
        "--config_suffix", config_suffix,
        "--json_config", jsonconfigs,
        "--model_name", model_name,
        ],
    runconfig=run_config,
    # inputs=[jsonconfigs],
    outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step Train created")

# TODO: update evaluation script to be more generic
evaluate = PythonScriptStep(
    name="Evaluate New Model with Prod Model",
    script_name="evaluate/evaluate_model.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
                "--config_suffix", config_suffix,
                "--json_config", jsonconfigs,
                ],
    runconfig=run_config,
    inputs=[jsonconfigs],
    # outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step Evaluate created")

register_model = PythonScriptStep(
    name="Register New Trained Model",
    script_name="register/register_model.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
        "--config_suffix", config_suffix,
        "--json_config", jsonconfigs,
        "--model_name", model_name,
        ],
    runconfig=run_config,
    inputs=[jsonconfigs],
    # outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step register model created")

# Create Steps dependency such that they run in sequence
evaluate.run_after(train)
register_model.run_after(evaluate)

steps = [register_model]


# Build Pipeline
pipeline1 = Pipeline(workspace=ws, steps=steps)
print("Pipeline is built")

# Validate Pipeline
pipeline1.validate()
print("Pipeline validation complete")


# Submit unpublished pipeline with small data set for test
if args.pipeline_action == "pipeline-test":
    pipeline_run1 = Experiment(ws, experiment_name).submit(
        pipeline1, regenerate_outputs=True
    )
    print("Pipeline is submitted for execution")
    pipeline_run1.wait_for_completion(show_output=True)


# Define pipeline parameters
# run_env = PipelineParameter(
#   name="dev_flag",
#   default_value=True)

# dbname = PipelineParameter(
#   name="dbname",
#   default_value='opex')


# Publish Pipeline
if args.pipeline_action == "publish":
    published_pipeline1 = pipeline1.publish(
        name=aml_pipeline_name, 
        description="Model training/retraining pipeline"
    )
    print(
        "Pipeline is published as rest_endpoint {} ".format(
            published_pipeline1.endpoint
        )
    )
