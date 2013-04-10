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
        run('touch wsgi.py')


def reset():
    with cd(env.project_dir):
        run('./manage.py reset_staging')


def _wwwrun(cmd):
    sudo(cmd, user='www-data')

@hosts('root@parkroulette.com')
def deploy():
    if not raw_input('Are you sure you want to deploy ?[y/N]').lower() == 'y':
        print 'Canceled.'
        return

    local('git tag -a `date +%y%m%d%H%M` -m "v`date +%y%m%d%H%M`"')
    local('git push production master')

    with cd(env.base_dir):
        _wwwrun('git pull')
        _wwwrun('find . -name "*.pyc" -exec rm {} \;')


    with cd(env.project_dir):
        _wwwrun('./manage.py collectstatic --noinput')
        _wwwrun('touch wsgi.py') # code reload
