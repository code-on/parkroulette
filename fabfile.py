from fabric.api import run, put, sudo, env, cd, local, hosts
import os

env.hosts = ['staging.code-on.be']
env.user = 'django'
env.base_dir = '/srv/sf-ticket-estimator'
env.project_name = 'sfte'
env.project_dir = '{0}/{1}'.format(env.base_dir, env.project_name)


def stage():
    local('git push origin master')
    with cd(env.base_dir):
        run('git pull')
        run('find . -name "*.pyc" -exec rm {} \;')

    with cd(env.project_dir):
        run('./manage.py collectstatic --noinput')

    with cd(env.base_dir):
        run('touch conf/run.wsgi')


def reset():
    with cd(env.project_dir):
        run('./manage.py reset_staging')