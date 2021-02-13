# Terraform Demo Infrastructure

This program makes modifications to live AWS Infrastructure, which can vary from account to account. We have bootstrapped some of this for you.

> 🚨This will create real AWS infrastructure and will cost you money! 🚨

> _Note: It is not exposed to rogue IAM users or to the internet at first. That will only happen after you run the exposure commands._

## Prerequisites

* Valid credentials to an AWS account
* AWS CLI should be set up locally
* Terraform should be installed


### Installing Terraform

* Install `tfenv` (Terraform version manager) via Homebrew, and install Terraform 0.12.28

```bash
brew install tfenv
tfenv install 0.12.28
tfenv use 0.12.28
```

### Build the demo infrastructure

* Run the Terraform code to generate the example AWS resources.

```bash
make terraform-demo
```

* Don't forget to clean up after.

```bash
make terraform-destroy
```
