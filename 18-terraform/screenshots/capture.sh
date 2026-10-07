#!/usr/bin/env bash
# Runs every Terraform workflow command for real and saves its raw output
# (including ANSI colours) to screenshots/logs/NN-name.log for rendering.
set -u
cd /mnt/c/Users/USER/Downloads/terraform-s3-demo
LOGS=screenshots/logs
rm -rf "$LOGS" && mkdir -p "$LOGS"

run() {  # run <file> <displayed command> <command to execute> [stdin answer]
  local file=$1 shown=$2 cmd=$3 answer=${4:-}
  echo "\$ $shown" > "$LOGS/$file.cmd"
  if [ -n "$answer" ]; then
    echo "$answer" | bash -c "$cmd" > "$LOGS/$file.log" 2>&1
  else
    bash -c "$cmd" > "$LOGS/$file.log" 2>&1
  fi
  local rc=$?
  echo "$answer" > "$LOGS/$file.answer"
  echo "[$file] exit=$rc"
}

run 00-prereq  "terraform version && aws sts get-caller-identity" "terraform version && aws sts get-caller-identity"
run 01-init     "terraform init"     "terraform init"
run 02-fmt      "terraform fmt"      "terraform fmt"
run 03-validate "terraform validate" "terraform validate"
run 04-plan     "terraform plan"     "terraform plan"
run 05-apply    "terraform apply"    "terraform apply" yes
run 06-show     "terraform show"     "terraform show"
run 07-output   "terraform output"   "terraform output"
run 08-verify   "aws s3api get-bucket-versioning --bucket \$(terraform output -raw bucket_name)" \
                "aws s3api get-bucket-versioning --bucket \$(terraform output -raw bucket_name)"
run 09-destroy  "terraform destroy"  "terraform destroy" yes
