# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from json import dumps
from ..models import GitHubCore
from .commit import RepoCommit


class Branch(GitHubCore):
    """The :class:`Branch <Branch>` object. It holds the information GitHub
    returns about a branch on a
    :class:`Repository <github3.repos.repo.Repository>`.
    """

    # The Accept header will likely be removable once the feature is out of
    # preview mode. See: http://git.io/v4O1e
    PREVIEW_HEADERS = {'Accept': 'application/vnd.github.loki-preview+json'}

    def _update_attributes(self, branch):
        #: Name of the branch.
        self.name = branch.get('name')
        #: Returns the branch's
        #: :class:`RepoCommit <github3.repos.commit.RepoCommit>` or ``None``.
        self.commit = branch.get('commit')
        if self.commit:
            self.commit = RepoCommit(self.commit, self)
        #: Returns '_links' attribute.
        self.links = branch.get('_links', {})
        #: Provides the branch's protection status.
        self.protection = branch.get('protection')

    def _repr(self):
        return '<Repository Branch [{0}]>'.format(self.name)

    def protect(self, enforcement, status_checks):
        """Enable force push protection and configure status check enforcement.

        See: http://git.io/v4Gvu

        :param str enforcement: (required), Specifies the enforcement level of
            the status checks. Must be one of 'off', 'non_admins', or
            'everyone'.
        :param list status_checks: (required), An iterable of strings naming
            status checks that must pass before merging.
        """
        edit = {'protection': {'enabled': True, 'required_status_checks': {
            'enforcement_level': enforcement, 'contexts': status_checks}}}
        json = self._json(self._patch(self.links['self'], data=dumps(edit),
                                      headers=self.PREVIEW_HEADERS), 200)

        # When attempting to clear `contexts`, the reply from github doesn't
        # currently reflect the actual value. Let's fix that for now.
        cur_contexts = self.protection['required_status_checks']['contexts']
        if status_checks == [] != cur_contexts:
            json['protection']['required_status_checks']['contexts'] = []

        self._update_attributes(json)
        return True

    def unprotect(self):
        """Disable force push protection on this branch."""
        edit = {'protection': {'enabled': False}}
        json = self._json(self._patch(self.links['self'], data=dumps(edit),
                                      headers=self.PREVIEW_HEADERS), 200)
        self._update_attributes(json)
        return True
