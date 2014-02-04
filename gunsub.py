import base64
import httplib
import json
import logging
import os
import sys
import time


log = logging
level = os.environ.get('DEBUG') and logging.DEBUG or logging.INFO
logging.basicConfig(level=level)


def iterpage():
    page = 1
    while True:
        yield page
        page += 1


def gunsub(github_user, github_password,
           github_include_repos=[], github_exclude_repos=[],
           since=None):

    def req(uri, method='GET', body=None, headers={}):
        auth = base64.encodestring('{0}:{1}'
                                   .format(github_user, github_password))
        headers = headers.copy()
        headers.update({
            'Authorization': 'Basic '+auth.strip(),
            'User-Agent': 'gunsub/0.2 (https://github.com/jpetazzo/gunsub)'
        })
        c = httplib.HTTPSConnection('api.github.com')
        log.debug('{0} {1}'.format(method, uri))
        if body is not None:
            body = json.dumps(body)
            log.debug('JSONified body: {0!r} ({1} bytes)'
                      .format(body, len(body)))
        c.request(method, uri, body, headers)
        r = c.getresponse()
        log.debug('x-ratelimit-remaining: {0}'
                  .format(r.getheader('x-ratelimit-remaining')))
        result = json.loads(r.read())
        return result

    since_qs = ''
    if since is not None:
        since_qs = '&since=' + time.strftime('%FT%TZ', time.gmtime(since))
    else:
        log.info('Scanning all notifications (this could take a while)...')

    count = 0
    for page in iterpage():
        notifications = req('/notifications?page={0}{1}'
                            .format(page, since_qs))
        if not notifications:
            break
        for notification in notifications:
            # Check inclusion/exclusion rules.
            repo_name = notification['repository']['name']
            if github_include_repos:
                if repo_name not in github_include_repos:
                    continue
            if github_exclude_repos:
                if repo_name in github_exclude_repos:
                    continue
            # If we were initially subscribed because mentioned/created/etc,
            # don't touch the subscription information.
            if notification['reason'] != 'subscribed':
                continue
            # Now check if we explicitly subscribed to this thing.
            subscription_uri = ('/notifications/threads/{0}/subscription'
                                .format(notification['id']))
            subscription = req(subscription_uri)
            # If no subscription is found, then that subscription was implicit
            if 'url' not in subscription:
                # ... And we therefore unsubscribe from further notifications
                subject_url = notification['subject']['url']
                log.info('Unsubscribing from {0}...'.format(subject_url))
                result = req(subscription_uri, 'PUT', dict(subscribed=False,
                                                           ignored=True))
                if 'subscribed' not in result:
                    log.warning('When unsubscribing from {0}, I got this: '
                                '{1!r} and it does not contain {2!r}.'
                                .format(subject_url, result, 'subscribed'))
                count += 1
    log.info('Done; had to go through {0} page(s) of notifications, '
             'and unsubscribed from {1} thread(s).'
             .format(page, count))


if __name__ == '__main__':
    if ('GITHUB_USER' not in os.environ
            or 'GITHUB_PASSWORD' not in os.environ):
        print '''
You must set environment variables GITHUB_USER and GITHUB_PASSWORD.
You might also set GITHUB_INCLUDE_REPOS and GITHUB_EXCLUDE_REPOS to
comma-separated lists of repos to include or exclude.
If you set GITHUB_POLL_INTERVAL, the program will run in a loop and
poll github notifications on the configured interval (in seconds).

To read more about gunsub, check is project page on github:
https://github.com/jpetazzo/gunsub
'''
        sys.exit(1)
    github_user = os.environ['GITHUB_USER']
    github_password = os.environ['GITHUB_PASSWORD']
    github_include_repos = os.environ.get('GITHUB_INCLUDE_REPOS', None)
    if github_include_repos:
        github_include_repos = github_include_repos.split(',')
    github_exclude_repos = os.environ.get('GITHUB_EXCLUDE_REPOS', '')
    github_exclude_repos = github_exclude_repos.split(',')
    interval = os.environ.get('GITHUB_POLL_INTERVAL')
    interval = interval and int(interval)
    since = None
    while True:
        next_since = time.time()
        try:
            gunsub(github_user, github_password,
                   github_include_repos, github_exclude_repos,
                   since)
            since = next_since
        except:
            log.exception('Error in main loop!')
        if not interval:
            break
        log.debug('Sleeping for {0} seconds.'.format(interval))
        time.sleep(interval)
