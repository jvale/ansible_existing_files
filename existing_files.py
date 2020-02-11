# (c) 2013, seth vidal <skvidal@fedoraproject.org> red hat, inc
# (c) 2017 Ansible Project
# (c) 2019, João Vale <jpvale@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: existing_files
    author: João Vale <jpvale@gmail.com>
    version_added: historical
    short_description: return existing files from list
    description:
      - this lookup checks a list of files and paths and returns the full path of all existing combinations found.
      - As all lookups, when fed relative paths it will try use the current task's location first and go up the chain
        to the containing role/play/include/etc's location.
      - The list of files has precedence over the paths searched.
        i.e, A task in a role has a 'file1' in the play's relative path, this will be used, 'file2' in role's relative path will not.
      - Either a list of files C(_terms) or a key `files` with a list of files is required for this plugin to operate.
    notes:
      - This lookup can be used in 'dual mode', either passing a list of file names or a dictionary that has C(files) and C(paths).
    options:
      _terms:
        description: list of file names
      files:
        description: list of file names
      paths:
        description: list of paths in which to look for the files
"""

EXAMPLES = """
- name: |
        copy all existing files to /some/dir,
        looking in relative directories from where the task is defined and
        including any play objects that contain it
  copy: src={{ item }} dest=/some/dir
  loop: "{{ query('existing_files', findme) }}"
  vars:
    findme:
      - foo
      - "{{ inventory_hostname }}"
      - bar

- name: read vars from all files that actually exist
  include_vars: "{{ item }}"
  loop: "{{ query('existing_files', params) }}"
  vars:
    params:
      files:
        - '{{ ansible_os_distribution }}.yml'
        - '{{ ansible_os_family }}.yml'
        - default.yml
      paths:
        - 'vars'
"""

RETURN = """
  _raw:
    description:
      - paths to found files
"""
import os

from jinja2.exceptions import UndefinedError

from ansible.errors import AnsibleUndefinedVariable
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        result = None
        anydict = False

        for term in terms:
            if isinstance(term, dict):
                anydict = True

        total_search = []
        if anydict:
            for term in terms:
                if isinstance(term, dict):
                    files = term.get('files', [])
                    paths = term.get('paths', [])

                    filelist = files
                    if isinstance(files, basestring):
                        files = files.replace(',', ' ')
                        files = files.replace(';', ' ')
                        filelist = files.split(' ')

                    pathlist = paths
                    if paths:
                        if isinstance(paths, basestring):
                            paths = paths.replace(',', ' ')
                            paths = paths.replace(':', ' ')
                            paths = paths.replace(';', ' ')
                            pathlist = paths.split(' ')

                    if not pathlist:
                        total_search = filelist
                    else:
                        for path in pathlist:
                            for fn in filelist:
                                f = os.path.join(path, fn)
                                total_search.append(f)
                else:
                    total_search.append(term)
        else:
            total_search = self._flatten(terms)

        found_paths = []
        for fn in total_search:
            try:
                fn = self._templar.template(fn)
            except (AnsibleUndefinedVariable, UndefinedError) as e:
                continue

            if os.path.isabs(fn) and os.path.exists(fn):
                found_paths.append(fn)
            else:
                # if none of the above were found, just check the
                # current filename against the current dir
                path = self._loader.path_dwim(fn)
                if os.path.exists(path):
                    found_paths.append(path)

        return found_paths
