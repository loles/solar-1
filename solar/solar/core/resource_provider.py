import os
import requests
import StringIO
import subprocess
import zipfile

from solar import utils


class BaseProvider(object):
    def run(self):
        pass


class DirectoryProvider(BaseProvider):
    def __init__(self, directory):
        self.directory = directory


class GitProvider(BaseProvider):
    def __init__(self, repository, path='.'):
        self.repository = repository
        self.path = path

        resources_directory = self._resources_directory()

        if not os.path.exists(resources_directory):
            self._clone_repo()

        if path != '.':
            self.directory = os.path.join(resources_directory, path)
        else:
            self.directory = resources_directory

    def _resources_directory(self):
        repo_name = os.path.split(self.repository)[1]

        return os.path.join(
            utils.read_config()['resources-directory'],
            repo_name
        )

    def _clone_repo(self):
        resources_directory = self._resources_directory()

        with open('/tmp/git-provider.yaml', 'w') as f:
            f.write("""
---

- hosts: all
  tasks:
    - git: repo={repository} dest={destination} clone={clone} update=yes
            """.format(
                repository=self.repository,
                destination=resources_directory,
                clone='yes'
            ))

        subprocess.check_call([
            'ansible-playbook',
            '-i', '"localhost,"',
            '-c', 'local',
            '/tmp/git-provider.yaml'
        ])


class RemoteZipProvider(BaseProvider):
    """Download & extract zip from some URL.

    Assumes zip structure of the form:
    <group-name>
      <resource1>
      <resource2>
      ...
    """

    def __init__(self, url, path='.'):
        self.url = url
        self.path = path

        r = requests.get(url)
        s = StringIO.StringIO(r.content)
        z = zipfile.ZipFile(s)

        group_name = os.path.dirname(z.namelist()[0])
        base_resources_directory = utils.read_config()['resources-directory']
        resources_directory = os.path.join(
            base_resources_directory, group_name
        )
        if not os.path.exists(resources_directory):
            z.extractall(base_resources_directory)

        if path != '.':
            self.directory = os.path.join(resources_directory, path)
        else:
            self.directory = resources_directory