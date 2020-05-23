Documentation for Administrators
================================

Introduction
------------

*clubbable* is a website that lets you send club notices to members, and manage
image galleries for members to browse.

If you currently manage club membership using a Microsoft Access database, you
may be able [#]_ to import your data into *clubbable*.


How to upload images, documents, and the database to the website
----------------------------------------------------------------

1.  Log in to the website. Click the “Connect Dropbox account” button, which is
    visible to administrators.

    .. image:: img/01_connect_dropbox_account.png

2.  Sign in to Dropbox.

    .. image:: img/02_sign_in_to_dropbox.png

3.  The website is an app registered with Dropbox under the name “clubbable”.
    Dropbox will warn you that the app is not widely used. (It’s OK not to be
    popular.) Click “Continue”.

    .. image:: img/03_before_you_connect_this_app.png

4.  Allow the *clubbable* app to access its own folder inside your Dropbox
    folder by clicking “Allow”. (It will not have access to files outside of
    its folder.)

    .. image:: img/04_clubbable_would_like_to_access.png

5.  The Owl Club website will notify you, “Dropbox authentication successful.”
    Your Dropbox account is now linked to the website. When you add files under
    the “Dropbox\Apps\clubbable” folder, Dropbox will notify the website, and
    the website will copy the files from Dropbox according to the folders they
    have been placed in.

    .. image:: img/05_dropbox_authentication_successful.png

6.  Open your Dropbox folder. You will notice a new folder inside it named
    “Apps”.

    .. image:: img/06_open_dropbox_folder.png

7.  Open the Apps folder. You will find another new folder, “clubbable”. Open
    that folder too.

    .. image:: img/07_open_apps_folder.png

8.  Create new folders inside the “clubbable” folder named “Notices”,
    “Documents”, “Photographs”, and “Cartoons”.

    These folder names correspond to the names of the buttons on the website.
    If you put documents into the “Notices” or “Documents” folders, the website
    will know where to copy them. Likewise if you put images into the
    “Photographs” or “Cartoons” folders, the website will know where they
    belong. You will be able to find the new documents and images on the
    website within a few minutes.

    .. image:: img/08_create_new_folders.png

9.  Copy the latest version of the database into the “Dropbox\Apps\clubbable”
    folder. You can do this whenever you add a meeting, or add or update a
    member or a guest.

    The website will look for a file named “Owldom-2017-Tables.mdb”, and if it
    finds it, it will update its data with the data in that file. (It will need
    the actual database file; it will not be able to import data from a
    shortcut to the file.) The import process should take a few minutes. New
    members will be included in the list of members under the “Members” button
    on the website.


.. rubric:: Footnotes

.. [#] The database import tool will probably need to be customised for your
       specific Microsoft Access database. If you are not a software developer,
       you will probably need a software developer to do that for you. The good
       news is that all the source code for *clubbable* is available free of
       charge, to use and to modify however you like, `on the Internet`_.

.. _on the Internet: https://github.com/kaapstorm/clubbable
