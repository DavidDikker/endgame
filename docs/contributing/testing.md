# Testing

## Unit tests

* Run [pytest](https://docs.pytest.org/en/stable/) with the following:

```bash
make test
```

## Security tests

* Run [bandit](https://bandit.readthedocs.io/en/latest/) with the following:

```bash
make security-test
```

## Integration tests

After making any modifications to the program, you can run a full-fledged integration test, using this program against your own test infrastructure in AWS.

* First, set your environment variables

```bash
# Set the environment variable for the username that you will create a backdoor for.
export EVIL_PRINCIPAL="arn:aws:iam::999988887777:user/evil"
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
```

* Then run the full-fledged integration test:

```bash
make integration-test
```

This does the following:

* Sets up your local dev environment (see `setup-dev`) in the `Makefile`
* Creates the Terraform infrastructure (see `terraform-demo` in the `Makefile`)
* Runs `list-resources`, `exploit --dry-run`, and `expose` against this live infrastructure
* Destroys the Terraform infrastructure (see `terraform-destroy` in the `Makefile`)

Note that the `expose` command will not expose the resources to the world - it will only expose them to your rogue user, not to the world.
