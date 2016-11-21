#!/usr/bin/env python
'''
Created on 2015-10-15

@author: James Quen
'''

import pexpect
import subprocess
import os
import re


# Change directory to be able to call git
os.chdir("/home/pi/misfit/Production/src/")


GIT_PASSWORD_PROMPT = "Enter passphrase for key \'\/home\/pi\/\.ssh\/id_rsa\'\:"
GIT_PASSWORD = "d@ly374"
GIT_PULL = "git pull origin "
GIT_FETCH = "git fetch"

def gitHardReset():
    """
    This function resets the commit just in case there were uncommitted changes.
    """

    # git reset --hard HEAD
    return subprocess.check_output("git reset --hard HEAD".split())

def gitDeleteAllTags():
    """
    This function deletes all tags to prepare for fetching.
    """
    # git tag -l | xargs git tag -d
    # TODO: Write a function that handles command line with pipe(s)
    listTags = subprocess.Popen("git tag -l".split(), stdout=subprocess.PIPE)
    deleteTags = subprocess.Popen("xargs git tag -d".split(), stdin=listTags.stdout, stdout=subprocess.PIPE)
    listTags.stdout.close()
    deleteTags.communicate()
    listTags.wait()

def gitPull(branch):
    """
    This function pulls the latest code from the branch.
    If the pull fails, the function will notify the caller with the error.

    @param branch The branch to pull from.
    """
    # git pull to get latest branch update
    pull = pexpect.spawn(GIT_PULL + branch, timeout=500)
    response = pull.expect([GIT_PASSWORD_PROMPT, "fatal\:", pexpect.EOF], timeout=500)

    # If the response is the prompt for the password, enter the password.
    if response == 0:
        pull.sendline(GIT_PASSWORD)
        pull.expect(pexpect.EOF)
        return (0, "Sent password successfully.")

    # If the response is fatal or EOF, return error code and message.
    elif response == 1 or response == 2:
        return (-3, pull.before)

def gitFetch():
    """
    This function gets the latest tags.
    If the fetch fails, the function will notify the caller with the error.
    """
    #git fetch to get latest tags
    fetch = pexpect.spawn(GIT_FETCH, timeout=500)
    response = fetch.expect([GIT_PASSWORD_PROMPT, "fatal\:", pexpect.EOF], timeout=500)

    # If the response is the prompt for the password, enter the password.
    if response == 0:
        fetch.sendline(GIT_PASSWORD)
        fetch.expect(pexpect.EOF)
        return (0, "Sent password successfully.")

    # If the response is fatal or EOF, return error code and message.
    elif response == 1 or response == 2:
        return (-3, fetch.before)

def gitGetTagsOnThisCommit():
    """
    This function gets all of the tags on the commit.
    """
    # Get the tags for this commit.
    # git tag --contains HEAD
    return subprocess.check_output("git tag --contains HEAD".split()).split("\n")

def gitGetCurrentBranchName():
    """
    This function returns the current branch name.
    """
    # Get the current branch name.
    # git rev-parse --abbrev-ref HEAD
    return subprocess.check_output("git rev-parse --abbrev-ref HEAD".split())

def gitGetCommitHash():
    """
    This function returns the current commit hash.
    """

    #git rev-parse HEAD
    return subprocess.check_output("git rev-parse HEAD".split()).strip()



