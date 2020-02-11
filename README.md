# existing_files
Ansible lookup plugin that, given a list files and paths, returns all the ones that exist. This is useful to avoid the pattern of having to `stat` a series of files to check if they exist before operating on them.

Heavily derived from Ansible's [first_found](https://docs.ansible.com/ansible/latest/plugins/lookup/first_found.html) lookup plugin, so all the rules that it applies to `files` and `paths` also apply here.

## Example usage
```yaml
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
```
