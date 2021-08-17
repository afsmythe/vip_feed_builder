## Overview

An implementation of the VIP data model using the [Django web framework](https://docs.djangoproject.com/en/3.2/) to support data providers and data maintainers should they require use of a database to upload, edit and integrate elections data formatted to the [Voting Information Project version 5 specification](https://vip-specification.readthedocs.io/en/release/). There are a few inspirations for such an application, including the Version 3.0 [quick_feed](https://github.com/votinginfoproject/quick_feed) and the open Issue [Links to projects implementing this specification](https://github.com/votinginfoproject/vip-specification/issues/297).

Users of this application should familiarize themselves with [Django's Model layer](https://docs.djangoproject.com/en/3.2/#the-model-layer) including `Models` and `QuerySets`. The remaining offerings in Django (including Views, Templates and Admin) were minimally implemented here, and there could be a need for expansion going forward.

## Setup

The `vip_feed_builder` repository can be installed on its own. There is some integration with `vip-admin`, and `vip-feed-builder` should be installed alongside. Django supports [various database programs](https://docs.djangoproject.com/en/3.2/ref/databases/). The user's database configuration details should be configured in the `vip_feed_builder/config.py` file as

```
databases = {
    'default': {
        'ENGINE': <>,
        'NAME': <>',
        'USER': <>,
        'PASSWORD': <>,
        'HOST': '',
        'PORT': ''
    }
}
```

Initial database creation and subsequent database schema updates are handled by the [Django migrations functionality](https://docs.djangoproject.com/en/3.2/topics/migrations/). The lines of code below should be run to either create a new database or make updates to an existing Django formatted database (following updates to `models.py`). With `vip-feed-builder` as the current working directory:
```
$ python manage.py makemigrations
$ python manage.py migrate
```

To open a Django shell session and gain access to the Django ORM:
```
$ python manage.py shell
```

## What this application can do

This application can import VIP 5.x formatted feeds in either XML or CSV formats. Users have the option of working with the Django ORM to create, edit and delete records once they are imported in to the database. There is also an XML export function which exports the collected info to a single XML file.

At present, the application is only able to store a single VIP feed at one time. Any new imports of data will require the existing database records to be deleted first.

To import an XML file:
```
>>> from vip52.functions import process_file
>>> process_file(<vip_file>)
```

To import a CSV feed:
```
>>> from vip52 import csv_import
>>> csv_import.main(<path_to_csv_files>)
```

## Open questions and consideration

Some code review by a larger audience is needed (and welcomed!).

### Concerns around the specification's `repeating` sub-types, including `InternationalizedText` and `ExternalIdentifiers`.

Modeling a database using these repeating relationships would result in somewhat bloated table data and would require multiple SQL joins and other complex queries to tie the data together accurately. The Django ORM does a fine job of linking these types of data seamlessly (see [`ManyToManyField`](https://docs.djangoproject.com/en/3.2/ref/models/fields/#manytomanyfield)). Though, it has been suggested to instead implement the PostgreSQL array field, which is something Django (and other frameworks like Rails) supports (https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/fields/#arrayfield).
