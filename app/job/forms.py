# -*- coding: utf-8 -*-
"""Define external bounty related forms.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from django.forms import HiddenInput, ModelForm

from .models import Job


class JobForm(ModelForm):
    """Define the External Bounty form handling."""

    class Meta:
        """Define the ExternalBounty form metadata."""

        model = Job
        fields = ['title', 'description', 'amount', 'txid', 'job_type', 'job_location', 'skills',
        'company', 'github_profile', 'apply_location', 'token_symbol', 'token_address']

        widgets = {
            'txid': HiddenInput(),
            'token_address': HiddenInput(),
            'token_symbol': HiddenInput(),
            'amount': HiddenInput(),
        }
