# Gunsub: Github UNSUBscribe

Gunsub will automatically unsubscribe you from Github issues, pull requests,
comments, etc. if you are not directly involved in the conversation. Being
"directly involved" means talking or being mentioned in the conversation,
as well as explicitly subscribing to it.


## What's the point?

I wrote this because I wanted to be aware of everything happening in a given
Github repository (the [Docker](https://github.com/dotcloud/docker) repository
in that case), but I was only interested in the *first* message of each
conversation (e.g. when an issue is created); not in the following messages
(e.g. when further comments are added to an issue). If I want to get involved
into an issue, I just have to comment on it, or quietly subscribe to the
issue; and then I will receive future notifications. Likewise, if someone
mentions me (by adding `@jpetazzo` into a comment), I will automatically be
re-subscribed. But I will not receive multiple e-mail notifications for
"normal" issues.


## How does it work?

Gunsub uses the Github API; specifically, the `/notifications` endpoint.
It checks all the notifications that I have received. For each notification,
the API indicates the *reason* of the notification: is it because I was
mentioned there? Or automatically subscribed because I'm watching the
repository? Or something else? If I was automatically subscribed, then
Gunsub checks if there is a subscription information for that thread.
If there is a subscription information, it can be either to indicate a
manual subscription, or conversely, to indicate that I'm already ignoring
that thread; in either case, Gunsub doesn't change the subscription setting.
However, if there is no subscription information, Gunsub will unsubscribe
me from further notifications. The subscription information gets overridden
if I comment or get mentioned anyway.


## This is awesome, how can I use it too?

Thank you! Gunsub only uses the basic Python library, so you don't need
to install anything fancy. You only need to set two environment variables,
`GITHUB_USER` and `GITHUB_PASSWORD`, and run it with `python gunsub.py`.

Optionally, you may set `GITHUB_INCLUDE_REPOS` or `GITHUB_EXCLUDE_REPOS`
to a comma-separated list of repositories to include or exclude. If you
do not specify anything, by default, Gunsub will act upon all your
repositories; if you specify `GITHUB_INCLUDE_REPOS`, it will act *only*
on those; and if you specify `GITHUB_EXCLUDE_REPOS`, it will act on
all repositories *except* those. If you specify both, it will be a little
bit silly, but it will work anyway, operating on all included repositories
except those in the exclude list.

By default, Gunsub will do one pass over your notifications, unsubscribe
from the "passive" notifications, and exit. But you can also set the
`GITHUB_POLL_INTERVAL` environment variable to be a delay (in seconds):
in that case, it will run in a loop, waiting for the indicated delay
between each iteration.


## This seriously sucks, there are better ways to do it!

Please let me know. This is the first time I do something meaningful
with the Github API. I found the documentation to be technically
accurate, but a lot of explanations were missing. For instance, when
posting a subscription, there are two boolean flags: `ignore` and
`subscribe`. Everywhere I looked, they were XORed (i.e., if `ignore`
is `true` then `subscribe` is `false` and vice-versa). Is it
meaningful to have them both to `true` or `false`? I don't know.
So if you know more efficient ways to do that, I'd love to hear
about it!


## You should use the If-Modified-Since...

Yes, I understand that it would be nicer; and I might implement
this soon enough. Consider this as a Minimimal Viable Product :-)


## Running from Docker

Gunsub is so simple, that it can probably run literally anywhere, even
on Windows or OS X machines. However, in an ongoing effort to CONTAINERIZE
ALL THE THINGS!, I wrote a tiny Dockerfile to run it inside a Docker
container, and I uploaded it to the Docker registry.

If you already have a Docker installation, you can do something like this:

```bash
docker run -d -e GITHUB_USER=johndoe GITHUB_PASSWORD=SecretSesame \
       	      	 GITHUB_POLL_INTERVAL=300 jpetazzo/gunsub
```

... and Docker will start a Gunsub container, running the main loop
every five minutes.


