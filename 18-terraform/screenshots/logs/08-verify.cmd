$ aws s3api get-bucket-versioning --bucket $(terraform output -raw bucket_name)
