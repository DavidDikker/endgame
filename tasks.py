#!/usr/bin/env python
import sys
import os
import logging
from invoke import task, Collection

BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "endgame", "bin", "cli.py"))
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, "endgame")
    )
)

logger = logging.getLogger(__name__)
# services that we will expose in these tests
EXPOSE_SERVICES = [
    "iam",
    "ecr",
    # "secretsmanager",
    "lambda"
]
# services to run the list-resources command against
LIST_SERVICES = [
    "iam",
    "lambda",
    "ecr",
    "efs",
    "secretsmanager",
    "s3"
]

EVIL_PRINCIPAL = os.getenv("EVIL_PRINCIPAL")
if not os.getenv("EVIL_PRINCIPAL"):
    raise Exception("Please set the EVIL_PRINCIPAL environment variable to the ARN of the rogue principal that you "
                    "want to give access to.")

# Create the necessary collections (namespaces)
ns = Collection()

test = Collection("test")
ns.add_collection(test)

# def exception_handler(func):
#     def inner_function(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except UnexpectedExit as u_e:
#             logger.critical(f"FAIL! UnexpectedExit: {u_e}")
#             sys.exit(1)
#         except Failure as f_e:
#             logger.critical(f"FAIL: Failure: {f_e}")
#             sys.exit(1)
#
#     return inner_function


# BUILD
@task
def build_package(c):
    """Build the policy_sentry package from the current directory contents for use with PyPi"""
    c.run('python -m pip install --upgrade setuptools wheel')
    c.run('python setup.py -q sdist bdist_wheel')


@task(pre=[build_package])
def install_package(c):
    """Install the package built from the current directory contents (not PyPi)"""
    c.run('pip3 install -q dist/endgame-*.tar.gz')


@task
def create_terraform(c):
    c.run("make terraform-demo")


@task
def destroy_terraform(c):
    c.run("make terraform-destroy")


# @exception_handler
# @task(pre=[create_terraform], post=[destroy_terraform])
# @task
@task(pre=[install_package])
def list_resources(c):
    for service in LIST_SERVICES:
        c.run(f"echo '\nListing {service}'", pty=True)


# @exception_handler
# @task(pre=[create_terraform], post=[destroy_terraform])
@task
def expose_dry_run(c):
    """DRY RUN"""
    for service in EXPOSE_SERVICES:
        c.run(f"{BIN} expose --service {service} --name test-resource-exposure --dry-run", pty=True)

# @exception_handler
# @task(pre=[create_terraform], post=[destroy_terraform])
@task
def expose_undo(c):
    """Test the undo capability, even though we will destroy it after anyway (just to test the capability)"""
    c.run(f"echo 'Exposing the Terraform infrastructure to {EVIL_PRINCIPAL}'")
    for service in EXPOSE_SERVICES:
        c.run(f"{BIN} expose --service {service} --name test-resource-exposure ", pty=True)
        c.run(f"echo 'Undoing the exposure to {EVIL_PRINCIPAL} before destroying, just to be extra sure and to test "
              f"it out.'")
        c.run(f"{BIN} expose --service {service} --name test-resource-exposure --undo", pty=True)


# @exception_handler
# @task(pre=[create_terraform], post=[destroy_terraform])
@task
def expose(c):
    """REAL EXPOSURE TO ROGUE ACCOUNT"""
    for service in EXPOSE_SERVICES:
        c.run(f"echo 'Exposing the Terraform infrastructure to {EVIL_PRINCIPAL}'")
        c.run(f"{BIN} expose --service {service} --name test-resource-exposure", pty=True)


test.add_task(list_resources, "list-resources")
test.add_task(expose_dry_run, "expose-dry-run")
test.add_task(expose_undo, "expose-undo")
test.add_task(expose, "expose")
