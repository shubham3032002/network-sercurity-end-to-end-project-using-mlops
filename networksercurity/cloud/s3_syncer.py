import os
import subprocess

class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        try:
            command = f"aws s3 sync {folder} {aws_bucket_url}"
            process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(process.stdout)  # Logs the output
        except subprocess.CalledProcessError as e:
            print(f"Error syncing to S3: {e.stderr}") 

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)
