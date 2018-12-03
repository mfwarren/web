# -*- coding: utf-8 -*-
#!/usr/bin/env python3
'''
    Copyright (C) 2017 Gitcoin Core

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

'''
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Contribution, Grant, Milestone, Subscription, Update
from marketing.mails import warn_subscription_failed

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'processes the txs associated with this grant'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)

    def handle(self, *args, **options):
        # setup
        network = options['network']

        #TODO - when https://gitcoincore.slack.com/archives/CBDTKB59A/p1543864404079500
        # is fixed, then remove these lines
        for grant in Grant.objects.all():
            grant.network = 'rinkeby'
            grant.save()

        # iter through Grants
        grants = Grant.objects.filter(network=network)
        print(f"got {grants.count()} grants")

        for grant in grants:
            subs = grant.subscriptions.filter(active=True)
            print(f" - {grant.pk} has {subs.count()} subs")

            for subscription in subs:
                is_ready_to_be_processed_db = subscription.get_is_ready_to_be_processed_from_db()
                
                print(f"  - subscription {subscription.pk}")
                if is_ready_to_be_processed_db:
                    print("   -- (ready via db) ")
                    is_ready_to_be_processed_web3 = subscription.get_is_ready_to_be_processed_from_web3()
                    is_active_web3 = subscription.get_is_active_from_web3()
                    signer = subscription.get_subscription_signer_from_web3()

                    print(is_ready_to_be_processed_web3, is_active_web3, signer)

                    if is_ready_to_be_processed_web3:
                        print("   -- (ready via web3) ")
                        print("   -- *executing* ")
                        txid = subscription.do_execute_subscription_via_web3()
                        
                        print(f"   -- *waiting for mine* (txid {txid}) ")
                        while not has_tx_mined(txid, subscription.grant.network):
                            time.sleep(10)
                        status, timestamp = get_tx_status(txid, subscription.grant.network, timezone.now())
                        
                        print(f"   -- *mined* (status: {status}) ")
                        was_success = status == 'success'
                        if not was_success:
                            warn_subscription_failed(subscription, txid, status)
                        else:
                            print("TODO: upon success, any DB mutations, send emails, handle failure")