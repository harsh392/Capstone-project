# promote model

import os
import mlflow

def promote_model():
    # Set up DagsHub credentials for MLflow tracking
    dagshub_token = os.getenv("CAPSTONE_TEST")
    if not dagshub_token:
        raise EnvironmentError("CAPSTONE_TEST environment variable is not set")

    os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
    os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

    dagshub_url = "https://dagshub.com"
    repo_owner = "vikashdas770"
    repo_name = "YT-Capstone-Project"

    # Set up MLflow tracking URI
    mlflow.set_tracking_uri(f'{dagshub_url}/{repo_owner}/{repo_name}.mlflow')

    client = mlflow.MlflowClient()

    model_name = "my_model"
    
    # Helper function to get versions by stage (replaces deprecated get_latest_versions)
    def get_versions_by_stage(client, model_name, stage):
        all_versions = client.search_model_versions(f"name='{model_name}'")
        return [v for v in all_versions if v.current_stage == stage]
    
    # Get the latest version in staging
    staging_versions = get_versions_by_stage(client, model_name, "Staging")
    if not staging_versions:
        raise ValueError(f"No model versions found in 'Staging' stage for model '{model_name}'")
    latest_version_staging = max(staging_versions, key=lambda v: int(v.version)).version

    # Archive the current production model
    prod_versions = get_versions_by_stage(client, model_name, "Production")
    for version in prod_versions:
        client.transition_model_version_stage(
            name=model_name,
            version=version.version,
            stage="Archived"
        )

    # Promote the new model to production
    client.transition_model_version_stage(
        name=model_name,
        version=latest_version_staging,
        stage="Production"
    )
    print(f"Model version {latest_version_staging} promoted to Production")

if __name__ == "__main__":
    promote_model()